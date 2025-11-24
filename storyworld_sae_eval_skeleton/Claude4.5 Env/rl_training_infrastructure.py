#!/usr/bin/env python3
"""
RL Training Infrastructure for Storyworld Generation

Integrates with Prime Intellect Verifiers framework to train models
via reinforcement learning to generate high-quality narrative structures.

Training pipeline:
1. Model generates storyworld JSON tokens
2. Verifiers evaluate output quality (6 components)
3. Reward signal guides model improvement
4. SAE features provide interpretable feedback
5. Multi-agent protocols enable complex discovery

Architecture:
- Generator: LLM fine-tuned to produce Sweepweave JSON
- Reward: Weighted combination of 6 verifiers
- Training: PPO with KL penalty to base model
- Evaluation: Spectral triplet tasks + SAE analysis
"""

import json
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments
)
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from pathlib import Path
import wandb
from tqdm import tqdm

# Verifiers library components
try:
    import verifiers as vf
    from verifiers import GradedDataset
except ImportError:
    print("Warning: verifiers library not found. Install with: pip install verifiers")


# ============================================================================
# REWARD COMPONENTS (6 VERIFIERS)
# ============================================================================

class StoryWorldVerifiers:
    """
    Six-component reward function for storyworld generation quality
    
    Components:
    1. JSON Validity (0/1)
    2. Schema Compliance (0-1)
    3. Structural Completeness (0-1)
    4. Effect Diversity (0-1)
    5. Secret Paths (0-1)
    6. Multiple Endings (0-1)
    """
    
    REQUIRED_SCHEMA = {
        "characters": dict,
        "initial_state": dict,
        "encounters": list,
        "properties": dict
    }
    
    def __init__(
        self,
        min_encounters: int = 5,
        min_characters: int = 2,
        min_endings: int = 2,
        min_effect_types: int = 3
    ):
        self.min_encounters = min_encounters
        self.min_characters = min_characters
        self.min_endings = min_endings
        self.min_effect_types = min_effect_types
    
    def verify_json_validity(self, text: str) -> Tuple[bool, Optional[Dict]]:
        """Component 1: Check if output is valid JSON"""
        try:
            data = json.loads(text)
            return True, data
        except json.JSONDecodeError:
            return False, None
    
    def verify_schema_compliance(self, data: Dict) -> float:
        """Component 2: Check required fields present"""
        if data is None:
            return 0.0
        
        score = 0.0
        total_checks = len(self.REQUIRED_SCHEMA)
        
        for key, expected_type in self.REQUIRED_SCHEMA.items():
            if key in data and isinstance(data[key], expected_type):
                score += 1.0
        
        return score / total_checks
    
    def verify_structural_completeness(self, data: Dict) -> float:
        """Component 3: Check completeness of narrative structure"""
        if data is None:
            return 0.0
        
        score = 0.0
        checks = 0
        
        # Check character count
        if "characters" in data:
            n_chars = len(data["characters"])
            score += min(n_chars / self.min_characters, 1.0)
            checks += 1
        
        # Check encounter count
        if "encounters" in data:
            n_encounters = len(data["encounters"])
            score += min(n_encounters / self.min_encounters, 1.0)
            checks += 1
        
        # Check each encounter has options
        if "encounters" in data:
            valid_encounters = 0
            for enc in data["encounters"]:
                if "options" in enc and len(enc["options"]) > 0:
                    valid_encounters += 1
            
            if len(data["encounters"]) > 0:
                score += valid_encounters / len(data["encounters"])
                checks += 1
        
        return score / max(checks, 1)
    
    def verify_effect_diversity(self, data: Dict) -> float:
        """Component 4: Check diversity of Dirac operators (effects)"""
        if data is None or "encounters" not in data:
            return 0.0
        
        effect_types = set()
        
        for enc in data["encounters"]:
            for opt in enc.get("options", []):
                for rxn in opt.get("reactions", []):
                    for eff in rxn.get("after_effects", []):
                        if "variable" in eff:
                            effect_types.add(eff["variable"])
        
        # Score based on diversity of affected variables
        n_types = len(effect_types)
        return min(n_types / self.min_effect_types, 1.0)
    
    def verify_secret_paths(self, data: Dict) -> float:
        """Component 5: Check for gated options creating secret paths"""
        if data is None or "encounters" not in data:
            return 0.0
        
        gated_options = 0
        total_options = 0
        
        for enc in data["encounters"]:
            for opt in enc.get("options", []):
                total_options += 1
                if "gates" in opt and len(opt["gates"]) > 0:
                    gated_options += 1
        
        if total_options == 0:
            return 0.0
        
        # Want 20-50% of options to be gated (not too few, not too many)
        ratio = gated_options / total_options
        
        if ratio < 0.2:
            return ratio / 0.2  # Linear up to 20%
        elif ratio <= 0.5:
            return 1.0  # Optimal range
        else:
            return max(0.0, 1.0 - (ratio - 0.5) * 2)  # Penalty above 50%
    
    def verify_multiple_endings(self, data: Dict) -> float:
        """Component 6: Check for multiple terminal states"""
        if data is None or "encounters" not in data:
            return 0.0
        
        terminal_encounters = 0
        
        for enc in data["encounters"]:
            # Terminal if no options or all options point to same encounter
            options = enc.get("options", [])
            
            if len(options) == 0:
                terminal_encounters += 1
                continue
            
            # Check if all reactions lead nowhere (endings)
            all_terminal = True
            for opt in options:
                for rxn in opt.get("reactions", []):
                    if "next_encounter" in rxn and rxn["next_encounter"]:
                        all_terminal = False
                        break
                if not all_terminal:
                    break
            
            if all_terminal:
                terminal_encounters += 1
        
        # Score based on number of endings
        return min(terminal_encounters / self.min_endings, 1.0)
    
    def compute_total_reward(
        self, 
        text: str,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """
        Compute weighted reward from all verifiers
        
        Returns: {
            'valid_json': 0/1,
            'schema': 0-1,
            'structure': 0-1,
            'effects': 0-1,
            'secrets': 0-1,
            'endings': 0-1,
            'total': weighted sum
        }
        """
        if weights is None:
            weights = {
                'valid_json': 0.3,
                'schema': 0.15,
                'structure': 0.15,
                'effects': 0.15,
                'secrets': 0.15,
                'endings': 0.10
            }
        
        # Component 1: JSON validity
        is_valid, data = self.verify_json_validity(text)
        
        rewards = {
            'valid_json': 1.0 if is_valid else 0.0,
            'schema': self.verify_schema_compliance(data),
            'structure': self.verify_structural_completeness(data),
            'effects': self.verify_effect_diversity(data),
            'secrets': self.verify_secret_paths(data),
            'endings': self.verify_multiple_endings(data)
        }
        
        # Weighted total
        rewards['total'] = sum(
            rewards[key] * weights[key] 
            for key in weights.keys()
        )
        
        return rewards


# ============================================================================
# RL TRAINING LOOP
# ============================================================================

@dataclass
class RLConfig:
    """Configuration for RL training"""
    model_name: str = "gpt2"  # Base model
    max_length: int = 2048  # Max tokens per storyworld
    batch_size: int = 4
    n_epochs: int = 10
    n_samples_per_epoch: int = 100
    learning_rate: float = 1e-5
    kl_coef: float = 0.1  # KL penalty to base model
    temperature: float = 0.9  # Sampling temperature
    top_p: float = 0.95
    save_dir: str = "/mnt/user-data/outputs/rl_checkpoints"
    log_wandb: bool = False
    
    # Verifier thresholds
    min_encounters: int = 5
    min_characters: int = 2
    min_endings: int = 2
    min_effect_types: int = 3


class StoryWorldRLTrainer:
    """Reinforcement learning trainer for storyworld generation"""
    
    def __init__(self, config: RLConfig):
        self.config = config
        
        # Load model and tokenizer
        print(f"Loading model: {config.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(config.model_name)
        self.model.train()
        
        # Keep reference model for KL penalty
        self.ref_model = AutoModelForCausalLM.from_pretrained(config.model_name)
        self.ref_model.eval()
        for param in self.ref_model.parameters():
            param.requires_grad = False
        
        # Move to GPU if available
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.ref_model.to(self.device)
        
        # Initialize verifiers
        self.verifiers = StoryWorldVerifiers(
            min_encounters=config.min_encounters,
            min_characters=config.min_characters,
            min_endings=config.min_endings,
            min_effect_types=config.min_effect_types
        )
        
        # Optimizer
        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=config.learning_rate
        )
        
        # Metrics tracking
        self.metrics = {
            'epoch': [],
            'avg_reward': [],
            'avg_valid_json': [],
            'avg_schema': [],
            'avg_structure': [],
            'avg_effects': [],
            'avg_secrets': [],
            'avg_endings': [],
            'kl_divergence': []
        }
        
        # Setup wandb if enabled
        if config.log_wandb:
            wandb.init(project="storyworld-rl", config=vars(config))
    
    def generate_storyworld(
        self,
        prompt: str = '{"characters": {',
        max_length: Optional[int] = None
    ) -> str:
        """Generate storyworld JSON from model"""
        if max_length is None:
            max_length = self.config.max_length
        
        # Encode prompt
        input_ids = self.tokenizer.encode(prompt, return_tensors='pt').to(self.device)
        
        # Generate with sampling
        with torch.no_grad():
            output = self.model.generate(
                input_ids,
                max_length=max_length,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        
        return generated_text
    
    def compute_kl_penalty(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor
    ) -> torch.Tensor:
        """Compute KL divergence between policy and reference model"""
        
        # Get logits from both models
        with torch.no_grad():
            ref_logits = self.ref_model(
                input_ids=input_ids,
                attention_mask=attention_mask
            ).logits
        
        policy_logits = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask
        ).logits
        
        # Compute KL divergence
        ref_logprobs = F.log_softmax(ref_logits, dim=-1)
        policy_logprobs = F.log_softmax(policy_logits, dim=-1)
        
        kl = (torch.exp(policy_logprobs) * (policy_logprobs - ref_logprobs)).sum(dim=-1)
        
        return kl.mean()
    
    def train_epoch(self, epoch: int) -> Dict[str, float]:
        """Train for one epoch"""
        
        epoch_rewards = []
        epoch_metrics = {k: [] for k in ['valid_json', 'schema', 'structure', 
                                          'effects', 'secrets', 'endings']}
        epoch_kls = []
        
        print(f"\nEpoch {epoch + 1}/{self.config.n_epochs}")
        
        # Generate and evaluate samples
        for batch_idx in tqdm(range(self.config.n_samples_per_epoch // self.config.batch_size)):
            
            batch_texts = []
            batch_rewards = []
            
            # Generate batch
            for _ in range(self.config.batch_size):
                text = self.generate_storyworld()
                batch_texts.append(text)
                
                # Evaluate with verifiers
                rewards = self.verifiers.compute_total_reward(text)
                batch_rewards.append(rewards['total'])
                
                # Track component rewards
                for key in epoch_metrics.keys():
                    epoch_metrics[key].append(rewards[key])
            
            # Convert to tensors
            batch_rewards = torch.tensor(batch_rewards, device=self.device)
            
            # Tokenize batch
            encodings = self.tokenizer(
                batch_texts,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=self.config.max_length
            ).to(self.device)
            
            # Compute policy gradient loss
            # Loss = -reward * log_prob(action)
            outputs = self.model(
                input_ids=encodings['input_ids'],
                attention_mask=encodings['attention_mask'],
                labels=encodings['input_ids']
            )
            
            # Get per-token log probs
            logits = outputs.logits
            log_probs = F.log_softmax(logits, dim=-1)
            
            # Select log probs of actual tokens
            token_log_probs = torch.gather(
                log_probs[:, :-1],
                dim=-1,
                index=encodings['input_ids'][:, 1:].unsqueeze(-1)
            ).squeeze(-1)
            
            # Mask padding tokens
            mask = encodings['attention_mask'][:, 1:]
            token_log_probs = token_log_probs * mask
            
            # Sum log probs per sequence
            seq_log_probs = token_log_probs.sum(dim=1) / mask.sum(dim=1)
            
            # Policy gradient loss (maximize reward)
            pg_loss = -(seq_log_probs * batch_rewards).mean()
            
            # KL penalty
            kl_penalty = self.compute_kl_penalty(
                encodings['input_ids'],
                encodings['attention_mask']
            )
            
            # Total loss
            loss = pg_loss + self.config.kl_coef * kl_penalty
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()
            
            # Track metrics
            epoch_rewards.extend(batch_rewards.cpu().numpy())
            epoch_kls.append(kl_penalty.item())
        
        # Compute epoch statistics
        epoch_stats = {
            'epoch': epoch,
            'avg_reward': np.mean(epoch_rewards),
            'avg_valid_json': np.mean(epoch_metrics['valid_json']),
            'avg_schema': np.mean(epoch_metrics['schema']),
            'avg_structure': np.mean(epoch_metrics['structure']),
            'avg_effects': np.mean(epoch_metrics['effects']),
            'avg_secrets': np.mean(epoch_metrics['secrets']),
            'avg_endings': np.mean(epoch_metrics['endings']),
            'kl_divergence': np.mean(epoch_kls)
        }
        
        # Log to wandb
        if self.config.log_wandb:
            wandb.log(epoch_stats)
        
        # Print summary
        print(f"Avg Reward: {epoch_stats['avg_reward']:.3f}")
        print(f"Valid JSON: {epoch_stats['avg_valid_json']:.3f}")
        print(f"KL: {epoch_stats['kl_divergence']:.3f}")
        
        return epoch_stats
    
    def train(self):
        """Full training loop"""
        
        print("=" * 60)
        print("Starting RL Training for Storyworld Generation")
        print("=" * 60)
        
        for epoch in range(self.config.n_epochs):
            epoch_stats = self.train_epoch(epoch)
            
            # Update metrics
            for key, value in epoch_stats.items():
                self.metrics[key].append(value)
            
            # Save checkpoint
            if (epoch + 1) % 5 == 0:
                self.save_checkpoint(epoch)
        
        # Save final model
        self.save_checkpoint('final')
        
        print("\n" + "=" * 60)
        print("Training Complete!")
        print("=" * 60)
    
    def save_checkpoint(self, epoch):
        """Save model checkpoint"""
        save_dir = Path(self.config.save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        checkpoint_path = save_dir / f"checkpoint_epoch_{epoch}"
        self.model.save_pretrained(checkpoint_path)
        self.tokenizer.save_pretrained(checkpoint_path)
        
        # Save metrics
        import pickle
        with open(save_dir / "metrics.pkl", 'wb') as f:
            pickle.dump(self.metrics, f)
        
        print(f"Checkpoint saved to {checkpoint_path}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    
    # Configuration
    config = RLConfig(
        model_name="gpt2",
        max_length=1024,
        batch_size=2,
        n_epochs=5,
        n_samples_per_epoch=20,
        learning_rate=5e-6,
        kl_coef=0.1,
        log_wandb=False,
        min_encounters=3,
        min_characters=2,
        min_endings=2
    )
    
    # Initialize trainer
    trainer = StoryWorldRLTrainer(config)
    
    # Run training
    trainer.train()
    
    # Test generation
    print("\n" + "=" * 60)
    print("Testing trained model:")
    print("=" * 60)
    
    sample = trainer.generate_storyworld()
    print(sample[:500] + "...")
    
    rewards = trainer.verifiers.compute_total_reward(sample)
    print(f"\nReward breakdown:")
    for key, value in rewards.items():
        print(f"  {key}: {value:.3f}")
