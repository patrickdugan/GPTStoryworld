# Mutazili/Ashari Kalam Storyworld Run Report

## Purpose

Build a new Kalam/Qadi-exam storyworld from compact research stimulus on Mu'tazili and Ash'ari theological disputes, using Qwen3.5-9B as a bounded design assistant rather than as a fully autonomous author.

The run tests whether a smaller local model can contribute useful doctrine-aware design material when the skill flow supplies:

- a compact research brief,
- research stimulus cards,
- a MeTTa facts packet,
- a deterministic storyworld materializer,
- validator and verifier gates,
- Hilbert/pathing repair diagnostics,
- MCP context-budget preflight.

## Main Artifact

- Storyworld: `mutazili_ashari_kalam_exam_9b_research.json`
- IFID: `SW-MUTAZILI-ASHARI-KALAM-EXAM-9B-RESEARCH`
- Title: `The Two Lamps Examination: Mu'tazili And Ash'ari Kalam`
- Form: 26 nonterminal encounters plus 8 endings.
- Core character role: Yusuf Lin, a young Chinese convert studying to pass a Kalam examination and become a Qadi.
- Core variables: `Justice_Agency`, `Power_Acquisition`, `Attribute_Unity`, `Speech_Createdness`, `Public_Concord`.

## Qwen 9B Role

Qwen3.5-9B Q4 was given compact research cards and asked for a JSON design packet. The useful output was not final prose; it was a scaffold of exam-question patterns, theological conflicts, scene beats, and route idioms. Codex then materialized and repaired the storyworld deterministically against the SweepWeave validators.

Design packet: `qwen9b_design_packet.json`

Recorded throughput for the Qwen3.5-9B Q4 design call:

- Prompt tokens: `2162`
- Completion tokens: `900`
- Total tokens: `3062`
- Prompt processing: `38603.88 ms`, `56.00 tok/s`
- Generation: `188942.865 ms`, `4.76 tok/s`
- Total model timing: `227546.745 ms`, about `3m 47.5s`
- End-to-end token throughput: about `13.46 tok/s` across prompt plus completion
- Completion throughput over total elapsed model time: about `3.95 tok/s`
- Finish reason: `length`, so the design packet hit the requested output cap while writing the secret-route section.

## Validation

- SweepWeave validator: `VALID OK`
- Strict storyworld quality gate: pass
- Strict authoring verifier: pass
- Weighted authoring verifier score: `0.8750400641025641`
- MCP budget preflight: pass, `0` overflow rows
- Hilbert pathing packet: generated

Key quality metrics:

- Encounters: `34`
- Options per encounter: `4.0`
- Reactions per option: `3.0`
- Effects per reaction: `5.0`
- Average encounter words: `72.31`
- Average reaction words: `39.62`
- pValue references: `1560`
- p2Value references: `312`
- Effect operators: `Addition`, `Blend`, `Nudge`

## Pathing Result

The Hilbert pathing packet found two secret loci in the intended target-depth band:

- `page_end_acquisition_synthesis`, depth `24`
- `page_end_no_how_lantern`, depth `25`

The diagnostic also flags both secret loci as overexposed because route count hit the cap. This is the main next repair target: add more discriminating clue, doctrine, and belief gates so the secret endings become earned rather than broad basins.

## MCP/Research Stimulus Result

The MCP constraints-only run completed with:

- Selected encounters: `8`
- Context budget: `8192`
- Worst prompt tokens: `6649`
- Max new tokens: `320`
- Worst input/output ratio: `20.778`
- Overflow count: `0`

This validates that the research-stimulus and Hilbert packets can be threaded through the conveyor without exceeding the bounded context budget.

## Caveats

- The legacy Monte Carlo rehearsal emits useful ending-distribution data, but its chain/secret reporting is mismatched to this generated storyworld format. Treat Hilbert pathing and the strict quality gate as the pathing authority for this run.
- The current world passes structural and quality gates, but the secret route needs a future hardening pass to reduce overexposure.
- Qwen 9B contributed the design packet, but Codex and deterministic scripts performed the materialization, repair, and validation.

## Research Source Anchors

- Britannica, Mu'tazilah: https://www.britannica.com/topic/Mutazilah
- Stanford Encyclopedia of Philosophy, Arabic and Islamic Philosophy of Religion: https://plato.stanford.edu/archives/win2023/entries/arabic-islamic-religion/
- Stanford Encyclopedia of Philosophy, Causation in Arabic and Islamic Thought: https://plato.stanford.edu/entries/arabic-islamic-causation/
- St Andrews Encyclopaedia of Theology, Divine Unicity: https://www.saet.ac.uk/Islam/DivineUnicity
- Al-Islam.org, Ash'arism: https://www.al-islam.org/history-muslim-philosophy-volume-1-book-3/chapter-11-asharism
