#!/usr/bin/env python3
"""
Sparse Autoencoder for Narrative Feature Extraction

Trains SAEs on storyworld rollout states to discover interpretable features
that correspond to narrative affordances, character arcs, and plot structures.

Key objectives:
1. Learn sparse feature representations z from state vectors s
2. Maximize I(z; a | s) - mutual information between features and affordances
3. Identify features that predict available options (C(s) ∝ ||z||_0)
4. Extract Dirac operator eigenmodes for spectral analysis
"""

import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.metrics import mutual_info_score
import pickle


# ============================================================================
# SPARSE AUTOENCODER ARCHITECTURE
# ============================================================================

class SparseAutoencoder(nn.Module):
    """
    SAE with L1 sparsity penalty for discovering narrative features
    
    Architecture:
    - Encoder: s ∈ R^d → z ∈ R^k (sparse latent)
    - Decoder: z ∈ R^k → ŝ ∈ R^d (reconstruction)
    
    Loss: MSE(s, ŝ) + λ₁||z||₁ + λ₂||W_enc||₂²
    """
    
    def __init__(
        self,
        input_dim: int,
        latent_dim: int,
        sparsity_coef: float = 0.1,
        l2_coef: float = 1e-5,
    ):
        super().__init__()
        
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.sparsity_coef = sparsity_coef
        self.l2_coef = l2_coef
        
        # Encoder: Linear + ReLU for non-negativity
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, latent_dim),
            nn.ReLU()
        )
        
        # Decoder: Linear only (allow negative reconstructions)
        self.decoder = nn.Linear(latent_dim, input_dim)
        
    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Encode state to sparse features"""
        return self.encoder(x)
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode features back to state"""
        return self.decoder(z)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Full forward pass"""
        z = self.encode(x)
        x_recon = self.decode(z)
        return x_recon, z
    
    def loss(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Compute total loss with breakdown"""
        x_recon, z = self.forward(x)
        
        # Reconstruction loss
        mse_loss = F.mse_loss(x_recon, x)
        
        # Sparsity penalty (L1 on activations)
        sparsity_loss = torch.mean(torch.abs(z))
        
        # Weight decay (L2 on encoder weights)
        l2_loss = torch.norm(self.encoder[0].weight, p=2)
        
        # Total loss
        total_loss = (
            mse_loss + 
            self.sparsity_coef * sparsity_loss + 
            self.l2_coef * l2_loss
        )
        
        return {
            'total': total_loss,
            'mse': mse_loss,
            'sparsity': sparsity_loss,
            'l2': l2_loss,
            'l0': torch.mean((z > 1e-3).float().sum(dim=-1))  # Approximate L0
        }


# ============================================================================
# STATE EXTRACTION FROM STORYWORLDS
# ============================================================================

class StoryWorldStateExtractor:
    """Extract state vectors from storyworld rollouts"""
    
    def __init__(self):
        self.property_vocab = {}  # Maps property names to indices
        self.character_vocab = {}  # Maps character names to indices
        
    def extract_state_vector(
        self, 
        state: Dict[str, any],
        normalize: bool = True
    ) -> np.ndarray:
        """
        Convert storyworld state to vector representation
        
        State structure:
        {
            "characters": {
                "Alice": {"trust": 0.5, "wealth": 100, ...},
                "Bob": {"trust": -0.2, "wealth": 50, ...}
            },
            "variables": {"debt": 30, "time": 5, ...},
            "current_encounter": "enc_3",
            "spool": ["enc_1", "enc_2"]
        }
        
        Vector: [char_props_flat, variables_flat, encounter_id, spool_length]
        """
        vector_parts = []
        
        # Character properties (flattened)
        if "characters" in state:
            for char_name in sorted(state["characters"].keys()):
                char_state = state["characters"][char_name]
                for prop_name in sorted(char_state.keys()):
                    value = char_state[prop_name]
                    if isinstance(value, (int, float)):
                        vector_parts.append(float(value))
        
        # Global variables
        if "variables" in state:
            for var_name in sorted(state["variables"].keys()):
                value = state["variables"][var_name]
                if isinstance(value, (int, float)):
                    vector_parts.append(float(value))
        
        # Encounter index
        if "current_encounter" in state:
            enc_id = hash(state["current_encounter"]) % 1000
            vector_parts.append(float(enc_id))
        
        # Spool depth (trajectory position)
        if "spool" in state:
            vector_parts.append(float(len(state["spool"])))
        
        vector = np.array(vector_parts, dtype=np.float32)
        
        if normalize:
            # Z-score normalization
            vector = (vector - vector.mean()) / (vector.std() + 1e-8)
        
        return vector
    
    def extract_affordances(self, state: Dict[str, any]) -> List[str]:
        """Extract available affordances (options) at state"""
        affordances = []
        
        if "available_options" in state:
            affordances = state["available_options"]
        
        return affordances


# ============================================================================
# ROLLOUT DATASET
# ============================================================================

class RolloutDataset(Dataset):
    """Dataset of (state, affordances) pairs from storyworld rollouts"""
    
    def __init__(
        self,
        rollouts: List[List[Dict]],
        extractor: StoryWorldStateExtractor
    ):
        self.samples = []
        self.extractor = extractor
        
        # Extract all (state, affordances) pairs
        for rollout in rollouts:
            for step in rollout:
                state_vector = extractor.extract_state_vector(step)
                affordances = extractor.extract_affordances(step)
                
                self.samples.append({
                    'state': state_vector,
                    'affordances': affordances,
                    'cardinality': len(affordances)
                })
        
        # Compute dataset statistics
        self.state_dim = self.samples[0]['state'].shape[0]
        self.max_cardinality = max(s['cardinality'] for s in self.samples)
        
        print(f"Dataset: {len(self.samples)} samples")
        print(f"State dim: {self.state_dim}")
        print(f"Max affordance cardinality: {self.max_cardinality}")
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        sample = self.samples[idx]
        return {
            'state': torch.from_numpy(sample['state']).float(),
            'cardinality': torch.tensor(sample['cardinality']).float()
        }


# ============================================================================
# TRAINING
# ============================================================================

def train_sae_on_rollouts(
    rollouts: List[List[Dict]],
    latent_dim: int = 512,
    sparsity_coef: float = 0.1,
    n_epochs: int = 100,
    batch_size: int = 64,
    learning_rate: float = 1e-3,
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
) -> Tuple[SparseAutoencoder, RolloutDataset, Dict]:
    """
    Train SAE on storyworld rollouts
    
    Returns: (trained_sae, dataset, training_history)
    """
    
    # Extract states from rollouts
    extractor = StoryWorldStateExtractor()
    dataset = RolloutDataset(rollouts, extractor)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # Initialize SAE
    sae = SparseAutoencoder(
        input_dim=dataset.state_dim,
        latent_dim=latent_dim,
        sparsity_coef=sparsity_coef
    ).to(device)
    
    optimizer = torch.optim.Adam(sae.parameters(), lr=learning_rate)
    
    # Training loop
    history = {
        'total_loss': [],
        'mse_loss': [],
        'sparsity_loss': [],
        'l0_norm': []
    }
    
    print(f"Training SAE on {len(dataset)} samples...")
    print(f"Device: {device}")
    
    for epoch in range(n_epochs):
        epoch_losses = []
        epoch_mse = []
        epoch_sparsity = []
        epoch_l0 = []
        
        for batch in dataloader:
            states = batch['state'].to(device)
            
            # Forward pass
            losses = sae.loss(states)
            
            # Backward pass
            optimizer.zero_grad()
            losses['total'].backward()
            optimizer.step()
            
            # Track metrics
            epoch_losses.append(losses['total'].item())
            epoch_mse.append(losses['mse'].item())
            epoch_sparsity.append(losses['sparsity'].item())
            epoch_l0.append(losses['l0'].item())
        
        # Record epoch statistics
        history['total_loss'].append(np.mean(epoch_losses))
        history['mse_loss'].append(np.mean(epoch_mse))
        history['sparsity_loss'].append(np.mean(epoch_sparsity))
        history['l0_norm'].append(np.mean(epoch_l0))
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{n_epochs}")
            print(f"  Loss: {history['total_loss'][-1]:.4f}")
            print(f"  MSE: {history['mse_loss'][-1]:.4f}")
            print(f"  L0: {history['l0_norm'][-1]:.2f}")
    
    return sae, dataset, history


if __name__ == "__main__":
    # Create synthetic rollouts for demo
    def create_synthetic_rollout(n_steps: int = 10) -> List[Dict]:
        rollout = []
        for i in range(n_steps):
            state = {
                'characters': {
                    'Alice': {
                        'trust': np.random.rand() * 2 - 1,
                        'wealth': np.random.randint(0, 200)
                    },
                    'Bob': {
                        'trust': np.random.rand() * 2 - 1,
                        'wealth': np.random.randint(0, 200)
                    }
                },
                'variables': {
                    'debt': np.random.randint(0, 100),
                    'time': i
                },
                'current_encounter': f'enc_{i}',
                'spool': [f'enc_{j}' for j in range(i)],
                'available_options': [f'opt_{k}' for k in range(np.random.randint(1, 6))]
            }
            rollout.append(state)
        return rollout
    
    rollouts = [create_synthetic_rollout() for _ in range(100)]
    
    # Train SAE
    sae, dataset, history = train_sae_on_rollouts(
        rollouts,
        latent_dim=256,
        sparsity_coef=0.05,
        n_epochs=50,
        batch_size=32
    )
    
    # Save model
    save_dir = Path("/mnt/user-data/outputs/sae_models")
    save_dir.mkdir(exist_ok=True, parents=True)
    
    torch.save(sae.state_dict(), save_dir / "sae_narrative.pt")
    with open(save_dir / "training_history.pkl", 'wb') as f:
        pickle.dump(history, f)
    
    print(f"\nModel saved to {save_dir}")
