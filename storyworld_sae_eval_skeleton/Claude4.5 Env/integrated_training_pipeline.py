#!/usr/bin/env python3
"""
Integrated Training Pipeline: SAE Features + RL Optimization

Combines sparse autoencoder feature discovery with reinforcement learning
to train models that generate interpretable, high-quality storyworlds.

Pipeline:
1. Generate initial storyworlds with base model
2. Collect rollouts and train SAE on state representations
3. Identify interpretable features (character arcs, plot structures)
4. Use SAE features as auxiliary reward signal in RL
5. Fine-tune model with feature-aware rewards
6. Iterate: re-train SAE on improved rollouts

This creates a virtuous cycle where SAE provides interpretability
and RL drives quality improvements.
"""

import json
import numpy as np
import torch
from pathlib import Path
from typing import Dict, List, Tuple
import pickle
from tqdm import tqdm

# Import components
from sae_narrative_features import (
    SparseAutoencoder,
    StoryWorldStateExtractor,
    RolloutDataset,
    train_sae_on_rollouts
)
from rl_training_infrastructure import (
    StoryWorldVerifiers,
    StoryWorldRLTrainer,
    RLConfig
)


# ============================================================================
# FEATURE-AWARE REWARD AUGMENTATION
# ============================================================================

class FeatureAwareVerifiers(StoryWorldVerifiers):
    """
    Extended verifiers that incorporate SAE feature quality
    
    Adds 7th component: Feature Interpretability
    - High score if SAE features are sparse and predictive of affordances
    - Measures I(z; a | s) and ||z||_0
    """
    
    def __init__(
        self,
        sae: SparseAutoencoder,
        extractor: StoryWorldStateExtractor,
        feature_weight: float = 0.1,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.sae = sae
        self.extractor = extractor
        self.feature_weight = feature_weight
        
        # Move SAE to eval mode
        self.sae.eval()
        for param in self.sae.parameters():
            param.requires_grad = False
    
    def verify_feature_quality(self, data: Dict) -> float:
        """
        Component 7: SAE feature interpretability
        
        Measures:
        1. Sparsity: L0 norm of features (fewer active features = better)
        2. Reconstruction: How well features reconstruct state
        3. Affordance prediction: Features should correlate with option count
        """
        if data is None:
            return 0.0
        
        try:
            # Simulate rollout to get states
            states = self._simulate_rollout(data, max_steps=10)
            
            if len(states) == 0:
                return 0.0
            
            # Extract state vectors
            state_vectors = [
                self.extractor.extract_state_vector(s) 
                for s in states
            ]
            
            # Compute SAE features
            features_list = []
            reconstructions = []
            
            device = next(self.sae.parameters()).device
            
            for state_vec in state_vectors:
                state_tensor = torch.from_numpy(state_vec).float().unsqueeze(0).to(device)
                
                with torch.no_grad():
                    features = self.sae.encode(state_tensor)
                    recon = self.sae.decode(features)
                
                features_list.append(features.cpu().numpy())
                reconstructions.append(recon.cpu().numpy())
            
            # Metric 1: Sparsity (lower L0 = better)
            l0_norms = [np.sum(f > 1e-3) for f in features_list]
            avg_l0 = np.mean(l0_norms)
            sparsity_score = max(0, 1.0 - avg_l0 / 100)  # Normalize
            
            # Metric 2: Reconstruction quality
            mse_scores = []
            for state_vec, recon in zip(state_vectors, reconstructions):
                mse = np.mean((state_vec - recon[0]) ** 2)
                mse_scores.append(mse)
            
            avg_mse = np.mean(mse_scores)
            recon_score = np.exp(-avg_mse)  # Exponential decay
            
            # Metric 3: Affordance correlation (would need actual affordances)
            # For now, use feature activation variance as proxy
            feature_matrix = np.vstack(features_list)
            feature_variance = np.var(feature_matrix, axis=0).mean()
            variance_score = min(feature_variance * 10, 1.0)
            
            # Combined score
            total_score = (
                0.4 * sparsity_score +
                0.4 * recon_score +
                0.2 * variance_score
            )
            
            return total_score
            
        except Exception as e:
            print(f"Feature quality verification failed: {e}")
            return 0.0
    
    def _simulate_rollout(
        self, 
        data: Dict, 
        max_steps: int = 10
    ) -> List[Dict]:
        """
        Simulate a rollout through the storyworld
        
        Returns list of states encountered
        """
        if "encounters" not in data or "initial_state" not in data:
            return []
        
        states = []
        current_state = data["initial_state"].copy()
        current_enc_id = None
        
        # Find first encounter
        if len(data["encounters"]) > 0:
            current_enc_id = data["encounters"][0].get("id", "enc_0")
        else:
            return []
        
        for step in range(max_steps):
            # Find current encounter
            current_enc = None
            for enc in data["encounters"]:
                if enc.get("id") == current_enc_id:
                    current_enc = enc
                    break
            
            if current_enc is None:
                break
            
            # Record state
            states.append({
                'characters': current_state.copy(),
                'variables': current_state.copy(),
                'current_encounter': current_enc_id,
                'spool': [],  # Simplified
                'available_options': [opt.get("id", f"opt_{i}") 
                                     for i, opt in enumerate(current_enc.get("options", []))]
            })
            
            # Choose random option
            options = current_enc.get("options", [])
            if len(options) == 0:
                break
            
            chosen_option = np.random.choice(options)
            
            # Apply effects and find next encounter
            next_enc_id = None
            for reaction in chosen_option.get("reactions", []):
                # Apply effects
                for effect in reaction.get("after_effects", []):
                    var_name = effect.get("variable")
                    change = effect.get("change", 0)
                    
                    if var_name in current_state:
                        current_state[var_name] += change
                
                # Get next encounter
                if "next_encounter" in reaction:
                    next_enc_id = reaction["next_encounter"]
                    break
            
            if next_enc_id is None:
                break
            
            current_enc_id = next_enc_id
        
        return states
    
    def compute_total_reward(
        self, 
        text: str,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """Extended reward with feature quality"""
        
        # Get base rewards
        base_rewards = super().compute_total_reward(text, weights=None)
        
        # Add feature quality if data is valid
        valid, data = self.verify_json_validity(text)
        
        if valid:
            base_rewards['feature_quality'] = self.verify_feature_quality(data)
        else:
            base_rewards['feature_quality'] = 0.0
        
        # Recompute total with new component
        if weights is None:
            weights = {
                'valid_json': 0.25,
                'schema': 0.10,
                'structure': 0.15,
                'effects': 0.15,
                'secrets': 0.15,
                'endings': 0.10,
                'feature_quality': 0.10
            }
        
        base_rewards['total'] = sum(
            base_rewards[key] * weights.get(key, 0.0)
            for key in weights.keys()
        )
        
        return base_rewards


# ============================================================================
# ITERATIVE TRAINING PIPELINE
# ============================================================================

class IterativeTrainingPipeline:
    """
    Iterative pipeline alternating between SAE training and RL optimization
    
    Cycle:
    1. Generate rollouts with current policy
    2. Train SAE on rollout states → discover features
    3. Analyze features → identify interpretable patterns
    4. Use features in reward → guide RL training
    5. Update policy → generate better rollouts
    6. Repeat
    """
    
    def __init__(
        self,
        rl_config: RLConfig,
        sae_latent_dim: int = 256,
        sae_sparsity: float = 0.05,
        n_cycles: int = 5,
        rollouts_per_cycle: int = 100
    ):
        self.rl_config = rl_config
        self.sae_latent_dim = sae_latent_dim
        self.sae_sparsity = sae_sparsity
        self.n_cycles = n_cycles
        self.rollouts_per_cycle = rollouts_per_cycle
        
        # Initialize RL trainer
        self.rl_trainer = StoryWorldRLTrainer(rl_config)
        
        # SAE components (initialized in first cycle)
        self.sae = None
        self.extractor = None
        
        # Metrics
        self.cycle_metrics = []
    
    def generate_rollouts(self, n_rollouts: int) -> List[List[Dict]]:
        """Generate rollouts with current policy"""
        
        print(f"Generating {n_rollouts} rollouts...")
        
        rollouts = []
        
        for i in tqdm(range(n_rollouts)):
            # Generate storyworld
            text = self.rl_trainer.generate_storyworld()
            
            # Parse JSON
            try:
                data = json.loads(text)
                
                # Simulate rollout through storyworld
                states = self._simulate_full_rollout(data)
                
                if len(states) > 0:
                    rollouts.append(states)
                    
            except json.JSONDecodeError:
                continue
        
        print(f"Generated {len(rollouts)} valid rollouts")
        
        return rollouts
    
    def _simulate_full_rollout(self, data: Dict) -> List[Dict]:
        """Simulate complete rollout (reuses logic from verifier)"""
        verifier = FeatureAwareVerifiers(
            sae=self.sae if self.sae else None,
            extractor=self.extractor if self.extractor else StoryWorldStateExtractor()
        )
        return verifier._simulate_rollout(data, max_steps=20)
    
    def train_cycle(self, cycle: int):
        """Run one iteration of the training cycle"""
        
        print("\n" + "=" * 70)
        print(f"CYCLE {cycle + 1}/{self.n_cycles}")
        print("=" * 70)
        
        # Step 1: Generate rollouts with current policy
        rollouts = self.generate_rollouts(self.rollouts_per_cycle)
        
        if len(rollouts) == 0:
            print("No valid rollouts generated. Skipping cycle.")
            return
        
        # Step 2: Train SAE on rollout states
        print("\nTraining SAE on rollout states...")
        
        sae, dataset, sae_history = train_sae_on_rollouts(
            rollouts,
            latent_dim=self.sae_latent_dim,
            sparsity_coef=self.sae_sparsity,
            n_epochs=30,
            batch_size=32
        )
        
        self.sae = sae
        self.extractor = StoryWorldStateExtractor()
        
        # Step 3: Update RL trainer with feature-aware verifiers
        print("\nUpdating verifiers with SAE features...")
        
        self.rl_trainer.verifiers = FeatureAwareVerifiers(
            sae=self.sae,
            extractor=self.extractor,
            min_encounters=self.rl_config.min_encounters,
            min_characters=self.rl_config.min_characters,
            min_endings=self.rl_config.min_endings,
            min_effect_types=self.rl_config.min_effect_types
        )
        
        # Step 4: Run RL training with updated rewards
        print("\nRunning RL optimization...")
        
        # Train for a few epochs
        original_epochs = self.rl_config.n_epochs
        self.rl_config.n_epochs = 2  # Fewer epochs per cycle
        
        for epoch in range(2):
            epoch_stats = self.rl_trainer.train_epoch(
                cycle * 2 + epoch
            )
        
        self.rl_config.n_epochs = original_epochs
        
        # Step 5: Record cycle metrics
        cycle_metric = {
            'cycle': cycle,
            'sae_final_loss': sae_history['total_loss'][-1],
            'sae_final_l0': sae_history['l0_norm'][-1],
            'rl_reward': self.rl_trainer.metrics['avg_reward'][-1],
            'rl_valid_json': self.rl_trainer.metrics['avg_valid_json'][-1]
        }
        
        self.cycle_metrics.append(cycle_metric)
        
        print(f"\nCycle {cycle + 1} Summary:")
        print(f"  SAE L0: {cycle_metric['sae_final_l0']:.2f}")
        print(f"  RL Reward: {cycle_metric['rl_reward']:.3f}")
        print(f"  Valid JSON: {cycle_metric['rl_valid_json']:.3f}")
    
    def train(self):
        """Run full iterative training pipeline"""
        
        print("=" * 70)
        print("ITERATIVE TRAINING PIPELINE: SAE + RL")
        print("=" * 70)
        
        for cycle in range(self.n_cycles):
            self.train_cycle(cycle)
            
            # Save checkpoints
            self.save_checkpoint(cycle)
        
        print("\n" + "=" * 70)
        print("TRAINING COMPLETE")
        print("=" * 70)
        
        # Print final summary
        self.print_summary()
    
    def save_checkpoint(self, cycle: int):
        """Save all components"""
        
        save_dir = Path(self.rl_config.save_dir) / f"cycle_{cycle}"
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Save RL model
        self.rl_trainer.model.save_pretrained(save_dir / "rl_model")
        
        # Save SAE
        if self.sae is not None:
            torch.save(self.sae.state_dict(), save_dir / "sae.pt")
        
        # Save metrics
        with open(save_dir / "cycle_metrics.pkl", 'wb') as f:
            pickle.dump(self.cycle_metrics, f)
        
        print(f"Checkpoint saved to {save_dir}")
    
    def print_summary(self):
        """Print training summary"""
        
        print("\nTraining Summary:")
        print("-" * 70)
        
        for metric in self.cycle_metrics:
            print(f"Cycle {metric['cycle'] + 1}:")
            print(f"  SAE L0: {metric['sae_final_l0']:.2f}")
            print(f"  RL Reward: {metric['rl_reward']:.3f}")
            print(f"  Valid JSON: {metric['rl_valid_json']:.3f}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    
    # Configure training
    rl_config = RLConfig(
        model_name="gpt2",
        max_length=1024,
        batch_size=2,
        n_epochs=4,  # Will be overridden in cycles
        n_samples_per_epoch=20,
        learning_rate=5e-6,
        kl_coef=0.1,
        save_dir="/mnt/user-data/outputs/integrated_training"
    )
    
    # Create pipeline
    pipeline = IterativeTrainingPipeline(
        rl_config=rl_config,
        sae_latent_dim=256,
        sae_sparsity=0.05,
        n_cycles=3,
        rollouts_per_cycle=50
    )
    
    # Run training
    pipeline.train()
