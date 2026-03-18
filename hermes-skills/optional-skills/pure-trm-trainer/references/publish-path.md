# Publish Path

Hermes distinguishes between bundled skills, official optional skills, and community skills.

## Official Hermes path

- Upstream repo: `https://github.com/NousResearch/hermes-agent`
- Official optional skills folder: `optional-skills/`
- Submission mode: fork the Hermes repo, add the skill under `optional-skills/<skill-name>/`, then open a PR.

Use this path when the skill should be treated as official-but-not-universal inside Hermes.

## Community / registry path

- Keep the skill in an external Agent Skills repo or registry.
- Current local repo for this skill: `C:/projects/GPTStoryworld/hermes-skills/pure-trm-trainer`
- Good fit for `hermes skills publish`, GitHub tap sources, skills.sh, or another community registry.

Use this path when the skill is niche, experimental, or better maintained outside Hermes core.

## Recommended path for TRM trainer

`pure-trm-trainer` is a specialized training skill, so it fits best as:

1. community/external registry skill for now
2. PR to `NousResearch/hermes-agent/optional-skills/` only if Hermes maintainers want it bundled as an official optional skill

## Practical commands

```bash
hermes skills publish skills/pure-trm-trainer --to github --repo yourorg/skills-repo
hermes skills tap add yourorg/skills-repo
hermes skills install yourorg/skills-repo/pure-trm-trainer
```

For an official PR:

1. fork `NousResearch/hermes-agent`
2. copy `pure-trm-trainer` into `optional-skills/pure-trm-trainer`
3. open a PR
