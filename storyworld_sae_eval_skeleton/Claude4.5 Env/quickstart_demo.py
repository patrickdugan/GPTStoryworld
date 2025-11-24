#!/usr/bin/env python3
"""
Quick Start Example: Train SAE + RL on Synthetic Storyworlds

This demo script shows the complete pipeline on a small synthetic dataset.
"""

import sys
sys.path.append('/home/claude')

import numpy as np
from sae_narrative_features import train_sae_on_rollouts
from rl_training_infrastructure import StoryWorldRLTrainer, RLConfig
from integrated_training_pipeline import IterativeTrainingPipeline


# ============================================================================
# SYNTHETIC DATA GENERATION
# ============================================================================

def generate_synthetic_storyworld() -> dict:
    """Generate a minimal valid storyworld for testing"""
    
    n_encounters = np.random.randint(3, 8)
    n_characters = np.random.randint(2, 4)
    
    # Character names
    char_names = ["Alice", "Bob", "Charlie", "Diana"][:n_characters]
    
    # Build storyworld
    storyworld = {
        "characters": {},
        "initial_state": {},
        "properties": {
            "trust": {"min": -1.0, "max": 1.0},
            "wealth": {"min": 0, "max": 200}
        },
        "encounters": []
    }
    
    # Initialize characters
    for char_name in char_names:
        trust_val = np.random.rand() * 2 - 1
        wealth_val = np.random.randint(50, 150)
        
        storyworld["characters"][char_name] = {
            "initial_trust": trust_val,
            "initial_wealth": wealth_val
        }
        
        storyworld["initial_state"][f"{char_name}_trust"] = trust_val
        storyworld["initial_state"][f"{char_name}_wealth"] = wealth_val
    
    # Add global variables
    storyworld["initial_state"]["debt"] = np.random.randint(0, 100)
    storyworld["initial_state"]["time"] = 0
    
    # Generate encounters
    for i in range(n_encounters):
        
        n_options = np.random.randint(2, 4)
        options = []
        
        for j in range(n_options):
            
            # Random gating
            gates = []
            if np.random.rand() > 0.6:  # 40% gated
                gate_var = np.random.choice(list(storyworld["initial_state"].keys()))
                gates.append({
                    "variable": gate_var,
                    "value": np.random.randint(-50, 50),
                    "comparison": ">="
                })
            
            # Effects
            effects = []
            n_effects = np.random.randint(1, 4)
            
            for k in range(n_effects):
                eff_var = np.random.choice(list(storyworld["initial_state"].keys()))
                effects.append({
                    "variable": eff_var,
                    "change": np.random.randint(-30, 30)
                })
            
            # Next encounter (some terminal)
            if i == n_encounters - 1:
                next_enc = None  # Terminal
            else:
                next_enc = f"enc_{np.random.randint(i+1, n_encounters)}"
            
            option = {
                "id": f"opt_{i}_{j}",
                "text": f"Option {j+1}",
                "gates": gates,
                "reactions": [{
                    "condition": "default",
                    "after_effects": effects,
                    "next_encounter": next_enc
                }]
            }
            
            options.append(option)
        
        encounter = {
            "id": f"enc_{i}",
            "text": f"Encounter {i+1} text...",
            "options": options
        }
        
        storyworld["encounters"].append(encounter)
    
    return storyworld


def generate_synthetic_rollout(storyworld: dict, max_steps: int = 10) -> list:
    """Simulate a rollout through a storyworld"""
    
    rollout = []
    state = storyworld["initial_state"].copy()
    current_enc_id = storyworld["encounters"][0]["id"]
    
    for step in range(max_steps):
        # Find current encounter
        current_enc = None
        for enc in storyworld["encounters"]:
            if enc["id"] == current_enc_id:
                current_enc = enc
                break
        
        if current_enc is None:
            break
        
        # Get available options (check gates)
        available_opts = []
        for opt in current_enc["options"]:
            gates_pass = True
            for gate in opt.get("gates", []):
                var_val = state.get(gate["variable"], 0)
                threshold = gate["value"]
                
                if gate["comparison"] == ">=":
                    if not (var_val >= threshold):
                        gates_pass = False
                        break
            
            if gates_pass:
                available_opts.append(opt["id"])
        
        # Record state
        rollout.append({
            "characters": {k: v for k, v in state.items() if "_" in k},
            "variables": state.copy(),
            "current_encounter": current_enc_id,
            "spool": [f"enc_{i}" for i in range(step)],
            "available_options": available_opts
        })
        
        # Choose random option
        if len(available_opts) == 0:
            break
        
        chosen_id = np.random.choice(available_opts)
        chosen_opt = None
        for opt in current_enc["options"]:
            if opt["id"] == chosen_id:
                chosen_opt = opt
                break
        
        if chosen_opt is None:
            break
        
        # Apply effects
        reaction = chosen_opt["reactions"][0]
        for eff in reaction["after_effects"]:
            var_name = eff["variable"]
            change = eff["change"]
            
            if var_name in state:
                state[var_name] += change
        
        # Get next encounter
        next_enc_id = reaction.get("next_encounter")
        if next_enc_id is None:
            break
        
        current_enc_id = next_enc_id
    
    return rollout


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def demo_sae_training():
    """Demo: Train SAE on synthetic rollouts"""
    
    print("=" * 70)
    print("DEMO 1: SAE Training on Synthetic Rollouts")
    print("=" * 70)
    
    # Generate synthetic data
    print("\nGenerating synthetic storyworlds...")
    storyworlds = [generate_synthetic_storyworld() for _ in range(20)]
    
    print("Generating rollouts...")
    rollouts = []
    for sw in storyworlds:
        for _ in range(5):  # 5 rollouts per storyworld
            rollout = generate_synthetic_rollout(sw)
            if len(rollout) > 0:
                rollouts.append(rollout)
    
    print(f"Generated {len(rollouts)} rollouts")
    
    # Train SAE
    print("\nTraining SAE...")
    sae, dataset, history = train_sae_on_rollouts(
        rollouts,
        latent_dim=128,
        sparsity_coef=0.05,
        n_epochs=20,
        batch_size=16
    )
    
    print("\nFinal Metrics:")
    print(f"  MSE Loss: {history['mse_loss'][-1]:.4f}")
    print(f"  L0 Norm: {history['l0_norm'][-1]:.2f}")
    
    return sae, dataset


def demo_rl_training():
    """Demo: RL training with verifiers"""
    
    print("\n" + "=" * 70)
    print("DEMO 2: RL Training with Verifiers")
    print("=" * 70)
    
    # Configure for quick demo
    config = RLConfig(
        model_name="gpt2",
        max_length=512,
        batch_size=2,
        n_epochs=2,
        n_samples_per_epoch=10,
        learning_rate=5e-6,
        save_dir="/mnt/user-data/outputs/demo_rl_checkpoints"
    )
    
    # Train
    trainer = StoryWorldRLTrainer(config)
    trainer.train()
    
    # Test generation
    print("\nTesting trained model:")
    sample = trainer.generate_storyworld()
    print(sample[:300] + "...")
    
    rewards = trainer.verifiers.compute_total_reward(sample)
    print(f"\nReward breakdown:")
    for key, value in rewards.items():
        print(f"  {key}: {value:.3f}")


def demo_integrated_pipeline():
    """Demo: Full integrated SAE + RL pipeline"""
    
    print("\n" + "=" * 70)
    print("DEMO 3: Integrated SAE + RL Pipeline")
    print("=" * 70)
    
    # Configure for quick demo
    rl_config = RLConfig(
        model_name="gpt2",
        max_length=512,
        batch_size=2,
        n_samples_per_epoch=10,
        save_dir="/mnt/user-data/outputs/demo_integrated"
    )
    
    # Create pipeline
    pipeline = IterativeTrainingPipeline(
        rl_config=rl_config,
        sae_latent_dim=128,
        sae_sparsity=0.05,
        n_cycles=2,  # Just 2 cycles for demo
        rollouts_per_cycle=20
    )
    
    # Train
    pipeline.train()
    
    print("\nIntegrated training complete!")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "=" * 70)
    print("STORYWORLD TRAINING SYSTEM - QUICK START DEMOS")
    print("=" * 70)
    
    # Run demos
    try:
        # Demo 1: SAE only
        sae, dataset = demo_sae_training()
        
        # Demo 2: RL only
        demo_rl_training()
        
        # Demo 3: Integrated
        demo_integrated_pipeline()
        
        print("\n" + "=" * 70)
        print("ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()
