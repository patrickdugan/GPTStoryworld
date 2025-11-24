#!/usr/bin/env python3
"""
Corpus Amplification System for Sweepweave

Generates billions of tokens through:
1. Combinatorial theme/property expansion
2. Variable complexity (characters, encounters, spools)
3. Semantic injection from existing corpus
4. Quality filtering via RL-trained models

Target: 1M storyworlds × 20k tokens = 20B tokens
"""

import json
import random
import itertools
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import argparse


@dataclass
class StoryConfig:
    """Configuration for generating a storyworld"""
    num_characters: int
    num_properties: int
    num_encounters: int
    num_spools: int
    themes: List[str]
    setting: str
    property_axes: List[Tuple[str, str]]
    unique_id: str


# ============================================================================
# EXPANDED CONFIGURATION SPACE
# ============================================================================

# Personality/relationship axes (can be combined for 100+ unique property sets)
PROPERTY_AXES = [
    # Classic psychological dimensions
    ("Pragmatic", "Idealistic"),
    ("Stable", "Volatile"),
    ("Trust", "Betrayal"),
    ("Loyal", "Treacherous"),
    ("Calm", "Explosive"),
    ("Honest", "Tricky"),
    ("Cautious", "Reckless"),
    ("Compassionate", "Ruthless"),
    ("Humble", "Arrogant"),
    ("Cooperative", "Competitive"),
    
    # Cognitive styles
    ("Analytical", "Intuitive"),
    ("Focused", "Scattered"),
    ("Systematic", "Improvisational"),
    ("Literal", "Metaphorical"),
    ("Skeptical", "Credulous"),
    
    # Social dynamics
    ("Reserved", "Expressive"),
    ("Diplomatic", "Confrontational"),
    ("Yielding", "Assertive"),
    ("Independent", "Conformist"),
    ("Private", "Transparent"),
    
    # Moral/ethical
    ("Consequentialist", "Deontological"),
    ("Utilitarian", "Rights_Based"),
    ("Mercy", "Justice"),
    ("Forgiveness", "Retribution"),
    ("Equality", "Hierarchy"),
    
    # Epistemic
    ("Evidence_Based", "Faith_Based"),
    ("Open_Minded", "Dogmatic"),
    ("Certain", "Uncertain"),
    ("Empirical", "Theoretical"),
    ("Inductive", "Deductive"),
    
    # Temporal
    ("Present_Focused", "Future_Oriented"),
    ("Patient", "Impulsive"),
    ("Reflective", "Reactive"),
    ("Planning", "Spontaneous"),
    ("Long_Term", "Short_Term"),
]

# Thematic dimensions (can be combined for 1000+ unique theme sets)
THEMES = [
    # AI/Technology
    "alignment problem",
    "mesa-optimization",
    "instrumental convergence",
    "value learning",
    "corrigibility",
    "interpretability",
    "mechanistic transparency",
    "epistemic cleanliness",
    
    # Warfare/Conflict
    "6th generation warfare",
    "information dominance",
    "memetic warfare",
    "asymmetric conflict",
    "deterrence theory",
    "escalation dynamics",
    
    # Philosophy
    "consciousness and qualia",
    "free will vs determinism",
    "personal identity",
    "moral realism",
    "epistemic humility",
    "wujudic logic",
    
    # Social/Political
    "surveillance capitalism",
    "consent manufacturing",
    "institutional capture",
    "principal-agent problems",
    "preference falsification",
    "Schelling points",
    
    # Economics/Game Theory
    "coordination failures",
    "tragedy of commons",
    "public goods provision",
    "mechanism design",
    "information asymmetry",
    "adverse selection",
    
    # Narrative/Meta
    "storyworld coherence",
    "narrative causality",
    "dramatic irony",
    "unreliable narration",
    "metafictional awareness",
    "recursive embedding",
]

# Settings/scenarios (100+ options)
SETTINGS = [
    # Space/Sci-fi
    "space station negotiation",
    "generation ship committee",
    "orbital habitat council",
    "asteroid mining dispute",
    "terraform project oversight",
    "first contact protocol",
    "dyson sphere construction",
    "wormhole transit authority",
    
    # Cyberpunk/Near-future
    "corporate board meeting",
    "underground hacktivist cell",
    "augmented reality courtroom",
    "neural interface clinic",
    "surveillance state resistance",
    "posthuman commune",
    "AI rights tribunal",
    "data haven negotiation",
    
    # Research/Academic
    "quantum computing lab",
    "bioethics committee",
    "particle physics collaboration",
    "archaeological expedition",
    "climate modeling team",
    "synthetic biology startup",
    "consciousness research facility",
    "prediction market consortium",
    
    # Governance/Politics
    "decentralized protocol governance",
    "diplomatic summit",
    "treaty negotiation",
    "constitutional convention",
    "regulatory hearing",
    "emergency response team",
    "disaster recovery committee",
    "referendum campaign",
    
    # Economic/Financial
    "venture capital pitch",
    "merger negotiation",
    "bankruptcy proceedings",
    "market manipulation investigation",
    "derivatives clearinghouse",
    "central bank meeting",
    "crypto protocol fork",
    "carbon credit exchange",
]


# ============================================================================
# CONFIGURATION GENERATOR
# ============================================================================

class ConfigGenerator:
    """Generate diverse storyworld configurations"""
    
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.config_count = 0
    
    def generate_config(
        self,
        min_chars: int = 2,
        max_chars: int = 5,
        min_props: int = 2,
        max_props: int = 6,
        min_encs: int = 5,
        max_encs: int = 30,
        min_spools: int = 2,
        max_spools: int = 5,
        num_themes: int = 2,
    ) -> StoryConfig:
        """Generate a random valid configuration"""
        
        num_characters = self.rng.randint(min_chars, max_chars)
        num_properties = self.rng.randint(min_props, max_props)
        num_encounters = self.rng.randint(min_encs, max_encs)
        num_spools = self.rng.randint(min_spools, max_spools)
        
        # Sample themes and setting
        themes = self.rng.sample(THEMES, min(num_themes, len(THEMES)))
        setting = self.rng.choice(SETTINGS)
        
        # Sample property axes
        property_axes = self.rng.sample(PROPERTY_AXES, min(num_properties, len(PROPERTY_AXES)))
        
        self.config_count += 1
        unique_id = f"SW-GEN-{self.config_count:06d}"
        
        return StoryConfig(
            num_characters=num_characters,
            num_properties=num_properties,
            num_encounters=num_encounters,
            num_spools=num_spools,
            themes=themes,
            setting=setting,
            property_axes=property_axes,
            unique_id=unique_id,
        )
    
    def generate_batch(self, num_configs: int, **kwargs) -> List[StoryConfig]:
        """Generate a batch of configurations"""
        return [self.generate_config(**kwargs) for _ in range(num_configs)]
    
    def estimate_coverage(self) -> Dict[str, int]:
        """Estimate total possible unique configurations"""
        
        # Character counts: 2-5 = 4 options
        char_options = 4
        
        # Property counts: 2-6 = 5 options
        prop_options = 5
        
        # Encounter counts: 5-30 = 26 options
        enc_options = 26
        
        # Spool counts: 2-5 = 4 options
        spool_options = 4
        
        # Theme combinations (choose 2 from ~50): C(50,2) = 1225
        theme_combinations = len(THEMES) * (len(THEMES) - 1) // 2
        
        # Settings: ~100
        setting_options = len(SETTINGS)
        
        # Property axis combinations (choose 3 from ~30): C(30,3) = 4060
        prop_combinations = len(PROPERTY_AXES) * (len(PROPERTY_AXES) - 1) * (len(PROPERTY_AXES) - 2) // 6
        
        total = (char_options * prop_options * enc_options * spool_options * 
                 theme_combinations * setting_options * prop_combinations)
        
        return {
            "character_options": char_options,
            "property_options": prop_options,
            "encounter_options": enc_options,
            "spool_options": spool_options,
            "theme_combinations": theme_combinations,
            "setting_options": setting_options,
            "property_combinations": prop_combinations,
            "total_unique_configs": total,
        }


# ============================================================================
# CORPUS INJECTION
# ============================================================================

class CorpusInjector:
    """Inject semantic content from existing corpus into storyworld generation"""
    
    def __init__(self, corpus_path: Optional[Path] = None):
        self.corpus_path = corpus_path
        self.corpus_loaded = False
        self.semantic_index = {}
    
    def load_corpus(self):
        """Load and index existing corpus (placeholder for QFT-MCP integration)"""
        if not self.corpus_path or not self.corpus_path.exists():
            print("No corpus provided, using synthetic content")
            return
        
        # TODO: Integrate with QFT-MCP for phase-based retrieval
        # For now, just load raw text
        print(f"Loading corpus from {self.corpus_path}")
        self.corpus_loaded = True
    
    def get_thematic_content(self, theme: str, max_tokens: int = 500) -> str:
        """Retrieve corpus content relevant to theme"""
        
        if not self.corpus_loaded:
            # Synthetic fallback
            return f"[Thematic content about {theme}]"
        
        # TODO: Use QFT-MCP to retrieve phase-encoded relevant passages
        # For now, placeholder
        return f"[Retrieved content about {theme}]"
    
    def enhance_prompt(self, base_prompt: str, config: StoryConfig) -> str:
        """Enhance prompt with corpus-derived content"""
        
        enhancements = []
        
        for theme in config.themes:
            content = self.get_thematic_content(theme)
            enhancements.append(f"\nThematic guidance for '{theme}':\n{content}")
        
        if enhancements:
            return base_prompt + "\n\n" + "\n".join(enhancements)
        
        return base_prompt


# ============================================================================
# BATCH GENERATION SYSTEM
# ============================================================================

class BatchGenerator:
    """Orchestrate large-scale storyworld generation"""
    
    def __init__(
        self,
        output_dir: Path,
        config_generator: ConfigGenerator,
        corpus_injector: Optional[CorpusInjector] = None,
    ):
        self.output_dir = output_dir
        self.config_generator = config_generator
        self.corpus_injector = corpus_injector
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.output_dir / "manifest.jsonl"
    
    def generate_batch(
        self,
        batch_size: int = 1000,
        batch_id: Optional[int] = None,
    ) -> List[StoryConfig]:
        """Generate a batch of configurations and save manifest"""
        
        configs = self.config_generator.generate_batch(batch_size)
        
        # Save manifest
        with open(self.manifest_path, "a") as f:
            for config in configs:
                entry = {
                    "unique_id": config.unique_id,
                    "batch_id": batch_id,
                    "num_characters": config.num_characters,
                    "num_properties": config.num_properties,
                    "num_encounters": config.num_encounters,
                    "num_spools": config.num_spools,
                    "themes": config.themes,
                    "setting": config.setting,
                    "property_axes": [f"{p[0]}_{p[1]}" for p in config.property_axes],
                }
                f.write(json.dumps(entry) + "\n")
        
        return configs
    
    def estimate_token_count(self, config: StoryConfig) -> int:
        """Estimate tokens in generated storyworld"""
        
        # Rough estimates:
        # - Base structure: ~1000 tokens
        # - Per character: ~200 tokens
        # - Per property: ~100 tokens
        # - Per encounter: ~500-1000 tokens (depending on options/reactions)
        # - Per spool: ~50 tokens
        
        base = 1000
        char_tokens = config.num_characters * 200
        prop_tokens = config.num_properties * 100
        enc_tokens = config.num_encounters * 750  # Average
        spool_tokens = config.num_spools * 50
        
        return base + char_tokens + prop_tokens + enc_tokens + spool_tokens
    
    def estimate_corpus_size(self, num_storyworlds: int) -> Dict[str, float]:
        """Estimate total corpus size"""
        
        # Sample configs to get average
        sample_configs = self.config_generator.generate_batch(100)
        avg_tokens = sum(self.estimate_token_count(c) for c in sample_configs) / len(sample_configs)
        
        total_tokens = num_storyworlds * avg_tokens
        
        return {
            "num_storyworlds": num_storyworlds,
            "avg_tokens_per_storyworld": avg_tokens,
            "total_tokens": total_tokens,
            "total_tokens_billions": total_tokens / 1e9,
        }


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Sweepweave corpus amplification system")
    parser.add_argument("--output-dir", type=Path, default=Path("./corpus_output"),
                        help="Output directory for generated configs")
    parser.add_argument("--batch-size", type=int, default=1000,
                        help="Number of configs per batch")
    parser.add_argument("--num-batches", type=int, default=10,
                        help="Number of batches to generate")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")
    parser.add_argument("--corpus-path", type=Path,
                        help="Path to existing corpus for semantic injection")
    parser.add_argument("--estimate-only", action="store_true",
                        help="Only show coverage estimates")
    
    args = parser.parse_args()
    
    # Initialize
    config_gen = ConfigGenerator(seed=args.seed)
    corpus_inj = CorpusInjector(corpus_path=args.corpus_path) if args.corpus_path else None
    batch_gen = BatchGenerator(args.output_dir, config_gen, corpus_inj)
    
    # Show coverage estimate
    coverage = config_gen.estimate_coverage()
    print("\n=== CONFIGURATION SPACE COVERAGE ===")
    for key, value in coverage.items():
        if value > 1e6:
            print(f"{key}: {value:,.0f} ({value/1e6:.1f}M)")
        else:
            print(f"{key}: {value:,}")
    
    # Estimate corpus size
    print("\n=== CORPUS SIZE ESTIMATES ===")
    for target in [1000, 10000, 100000, 1000000]:
        est = batch_gen.estimate_corpus_size(target)
        print(f"\n{target:,} storyworlds:")
        print(f"  Avg tokens/storyworld: {est['avg_tokens_per_storyworld']:,.0f}")
        print(f"  Total tokens: {est['total_tokens']:,.0f} ({est['total_tokens_billions']:.2f}B)")
    
    if args.estimate_only:
        return
    
    # Generate batches
    print(f"\n=== GENERATING {args.num_batches} BATCHES ===")
    for batch_id in range(args.num_batches):
        configs = batch_gen.generate_batch(args.batch_size, batch_id)
        print(f"Batch {batch_id}: {len(configs)} configs generated")
    
    print(f"\nManifest written to: {batch_gen.manifest_path}")
    print(f"Total configs: {args.num_batches * args.batch_size:,}")


if __name__ == "__main__":
    main()
