# Pitch: Hermes 9-TRM Creative Skill Mesh

## Title

Hermes 9-TRM Creative Skill Mesh: Making Compact Models Useful For Bounded Storyworld Assembly

## Short Abstract

This demo shows a Hermes skill architecture for complex creative-engineering tasks where a local 27B model is not trusted as an autonomous builder. Instead, storyworld encounter assembly is decomposed into MCP memory packets, MeTTa symbolic control facts, nine small trained control policies, bounded LLM input requests, and verifier-backed commit/veto. The LLM contributes local imagination; the skill mesh supplies context discipline, mechanics, validation, and repair.

## What Was Built

- A 9-role TRM/control taxonomy for encounter assembly.
- A 1000-row trajectory library with about 284k estimated tokens.
- Train/val splits for compact control training.
- A tiny per-role control baseline trained on 900 rows and evaluated on 100 held-out rows.
- A storyworld evidence run showing whole-context pressure reduced by MCP packets and MeTTa/TRM repair improving authoring score.

## Key Numbers

- Corpus: 1000 trajectories, 900 train, 100 validation.
- Tiny mesh accuracy: 96/100 held-out action decisions.
- Whole storyworld context estimate: 705,087 tokens.
- Worst MCP packet estimate: 13,556 tokens.
- MCP overflow count: 0.
- Authoring score: 0.6076 to 0.7200.
- Authoring score delta: +0.11236.

## Live Demo Flow

1. Show the whole storyworld token estimate and explain why naive long-context authoring fails.
2. Show MCP preflight reducing the working context to a bounded encounter packet.
3. Show the 9 TRMs and how each works the LLM for one limited input.
4. Show the tiny trained control mesh eval receipt.
5. Show MeTTa/TRM repair evidence and before/after storyworld score.

## Honest Scope

This is not a claim that a 27B model can autonomously build high-quality 80-encounter storyworlds. It is a claim that compact trained control policies can make smaller models viable inside a larger skill architecture. The current trained model is a tiny per-role baseline, not a full neural TRM or QLoRA run. The next step is to train neural TRMs on the same trajectory views and replace the tiny baseline one role at a time.

## One-Liner

The model is not the authorial brain; the Hermes skill mesh is the control plane that lets a smaller model contribute bounded imagination without losing the game design.
