# Kalam Qadi Storyworld Conveyor Brief

## Purpose

Build a high-quality SweepWeave/GPTStoryworld storyworld without forcing Hermes or a local Qwen endpoint to parse the full `politburo_shehada.json` context. This file is the bounded-context source card. Read it first, then use repo tools and the conveyor.

Do not narrate future actions without terminal or file tool calls. If a source file is missing on the current machine, search first, then fall back to this brief.

## Source World Transfer

Primary source world:

`storyworlds/politburo_shehada.json`

Backup source world:

`storyworlds/politburo_shehada_repaired.json`

Human handoff:

`storyworlds/HANDOFF_Politburo_Shehada.md`

Source-world essence:

- The CCP Politburo undergoes a mass conversion to a heterodox Jadid Mu'tazili Kaysanite Islam.
- State power becomes entangled with kalam, rationalist theology, Shiite alliance politics, ASI treaty politics, Taiwan brinksmanship, and a revived Mihna.
- The old world tracks rationalism, occultation fervor, materialist residue, Shiite solidarity, Hanifiyya claims, Taiwan tension, US aggression, ASI dread, disillusionment, and faith.
- The best reusable pattern is not the Trump/ASI spectacle itself; it is the collision between rationalist theology, state coercion, sincere conversion, public order, factional suspicion, and legal/theological legitimacy.
- Preserve the uncanny political-theological tone, but make the new world more intimate and exam-driven.

Important distinction:

Do not make a generic fantasy school exam. The Kalam Exam must test whether the protagonist can become a qadi without becoming an instrument of power.

## New Storyworld

Working slug:

`kalam_qadi_chinese_convert`

Working title:

`The Kalam Examination: A Qadi for the Hidden Republic`

Premise:

The player is Liang Wen, a young Chinese man from a secular Han family who converts to Islam after the Politburo's rationalist religious turn. He studies at a state-recognized madrasa-court academy in Beijing to pass the Kalam Exam and become a qadi. The exam is not only doctrinal: it is also a loyalty screen, a jurisprudence practicum, a surveillance trap, and a test of sincerity. Every answer changes what the state, the scholars, his family, and the ordinary petitioners believe he is becoming.

Target:

- 80 encounters total.
- 68-72 playable story encounters plus 8-12 endings.
- 7-9 spools.
- Average 3 options per nonterminal encounter.
- Average 2-3 reactions per option.
- 4+ after-effects per reaction where possible.
- 8+ visible endings, including at least 2 secret/synthesis endings and 1 super-secret ending.
- Strong verifier scores: validator pass, hard acceptance pass, strict quality gate repaired as far as feasible, Monte Carlo with no dead ends, secret route observed or explicitly reachable by route proof.

## Research Anchors

Use these as conceptual anchors, not as text to quote into the world:

- Mu'tazili kalam centers rational theology, divine unity, divine justice, promise/threat, intermediate position, and commanding right/forbidding wrong. It is associated with debate over whether the Qur'an is created and with the Abbasid Mihna.
- A qadi is a Muslim judge who administers justice according to Sharia and historically needed legal reasoning competence, probity, and the capacity to derive rules from sources.
- Chinese Muslim context should distinguish Hui, Uyghur, Han convert, state religious administration, family pressure, mosque community, and anxieties around Sinicization without flattening them.

Useful external references if the agent needs quick grounding:

- Britannica, Qadi: https://www.britannica.com/topic/qadi
- Britannica, Hui: https://www.britannica.com/topic/Hui-people
- Routledge/Philosophy-style summary of Ash'ariyya and Mu'tazila: https://www.muslimphilosophy.com/ip/rep/H052.htm
- Pew overview of Islam and religion policy in China: https://www.pewresearch.org/religion/2023/08/30/islam/

## Cast

Use 8-11 core characters.

1. Liang Wen / Yusuf Liang

Player character. Young Han Chinese convert. Brilliant at logic, socially vulnerable, unsure whether his conversion is love of truth, revolt against family, or hunger for office.

2. Shaykha Maryam Ma

Hui jurist and examiner. She wants Liang to succeed but distrusts performative rationalism. She is sensitive to the difference between sincerity and state-approved piety.

3. Professor Han Qiming

Party theologian and architect of the Kalam Exam. Former Marxist legal theorist turned Mu'tazili rationalist. He sees qadis as compliance-preserving theorem provers.

4. Grand Examiner Qadi Abd al-Jabbar Chen

Chief examiner. Named in homage to Qadi Abd al-Jabbar but fictional. He defends divine justice and rational obligation while knowing the state uses his school as a sorting device.

5. Liang Wei

Player's father. Secular engineer. He sees the conversion as betrayal, social danger, and perhaps a careerist performance.

6. Amina Nur

Uyghur student and rival examinee. She is more fluent in inherited Islam than Liang but less trusted by the academy. Her presence exposes asymmetries in state suspicion.

7. The Mutazili Inquisitor

Continuity figure from the source world. Runs loyalty audits and tries to convert sincere theology into administrative certainty.

8. The Shanghai Atheist

Continuity figure from the source world. Offers Liang a secular legal career if he subtly sabotages the exam from within.

9. Rural Mystic

Continuity figure from the source world. Claims the hidden imam speaks through villagers ignored by both Party and academy.

10. Iranian Envoy

Observer from Qom. Respects kalam but sees the Chinese rationalist apparatus as dangerously state-captured.

11. Petitioners of the Court

Composite role for ordinary cases: widow, migrant worker, mosque trustee, family-law claimant, AI-labor victim, censored preacher, accused apostate, property witness.

## Core Variables

Use bounded number properties with both player and social perception where practical.

- Kalam_Mastery: technical command of logic, divine justice, created speech, causality, and legal inference.
- Sincerity: whether Liang is becoming Muslim for truth rather than status or rebellion.
- State_Trust: Party confidence that Liang will stabilize the new order.
- Scholarly_Trust: jurists' confidence that Liang can reason without flattering power.
- Family_Bond: relationship with father and household.
- Community_Trust: confidence of Hui/Uyghur/mosque communities and ordinary petitioners.
- Coercion_Tolerance: willingness to let the Mihna make belief legible by force.
- Legal_Mercy: ability to preserve justice without collapsing into sentimentality.
- Aql_Naql_Balance: balance between reason (`aql) and transmitted authority (naql).
- Hidden_Wali_Insight: secret-route awareness that the exam itself is judging whether the office of qadi should exist under state capture.
- ASI_Dread: inherited from source world; theological AI and legal automation pressure.
- Public_Order: capacity to prevent riots, factional purges, or court collapse.

PValue/p2Value guidance:

- Add pValue references for at least State_Trust, Scholarly_Trust, Community_Trust, and Sincerity.
- Add a small number of p2Value references around what the state believes the scholars believe about Liang, and what Liang believes the petitioners believe about the court.

## Spool Architecture

Target 8 spools of about 8-10 encounters each.

1. `spool_conversion_household`

Liang's conversion, naming, mosque entry, family conflict, first suspicion that the new religious order is political.

2. `spool_exam_foundations`

Training in logic, divine unity, divine justice, created Qur'an, promise/threat, intermediate position, and command/right-forbid/wrong.

3. `spool_mihna_loyalty`

State loyalty screens, Party theology interviews, surveillance, pressure to denounce insincere converts or insufficiently rational scholars.

4. `spool_court_practicum`

Legal cases: testimony, family law, debt, mosque governance, labor injury, AI evidence, apostasy accusation, coerced confession.

5. `spool_family_and_community`

Father, mother, Hui mentors, Uyghur rival, community rumors, mosque dispute, public pressure.

6. `spool_asi_jurisprudence`

Use the source world's ASI dread in a narrower way: legal automation, model-generated fatwas, surveillance scoring, synthetic witnesses.

7. `spool_final_exam`

Oral disputation, written proof, live case, loyalty trap, public sermon, qadi oath.

8. `spool_secret_wali`

Hidden route. Liang learns the real exam is whether he can refuse a corrupted bench and design a procedure that lets justice survive without a single state-controlled qadi.

## 80-Encounter Map

Use this as the encounter plan. Titles may change, but keep the functional role.

### Act I: Conversion and Household

1. The Name Yusuf
2. Father's Rice Wine
3. First Fajr in the State Mosque
4. Maryam Ma's Warning
5. The Registration Office
6. Amina's Question
7. The Shanghai Atheist's Card
8. The Hidden Mountain Rumor
9. Family Dinner Under Cameras
10. The Academy Gate

### Act II: Foundations of Kalam

11. The Syllogism and the Shahada
12. Divine Unity Without Images
13. Justice Before Power
14. Created Speech, Created Law
15. Promise and Threat
16. The Intermediate Position
17. Commanding Right Without Police
18. The Problem of Evil in Xinjiang Footnotes
19. The Logic Drill
20. The First Mock Exam

### Act III: Mihna and Loyalty

21. The Inquisitor's Interview
22. Denounce the Mechanical Convert
23. Professor Han's Diagram
24. The Uyghur File
25. The Hui Mosque Audit
26. The Rural Mystic's Petition
27. The Secular Escape Offer
28. The Qom Observer
29. A Father's Warning Letter
30. The Loyalty Theorem

### Act IV: Court Practicum

31. The Widow's Testimony
32. The Pork Factory Injury
33. The Mosque Deed
34. The AI Transcript
35. The Apostasy Accusation
36. The Divorce Petition
37. The Coerced Confession
38. The Debt Ledger
39. The Missing Witness
40. The Mercy Precedent

### Act V: Community Pressure

41. Amina's Disqualification
42. Maryam's Private Lesson
43. Father's Hospital Bed
44. The Friday Sermon
45. The Petitioners' Queue
46. The Rationalist Youth League
47. The Village Delegation
48. The Shanghai Salon
49. The Mosque Riot That Almost Happens
50. The Night Study Circle

### Act VI: ASI Jurisprudence

51. The Model That Issues Fatwas
52. Synthetic Witnesses
53. The Risk Score Appeal
54. Covenant-72B Footnote
55. The Automated Qadi Pilot
56. Amina's Data Shadow
57. The Wali Model Speaks
58. Professor Han's Shortcut
59. The Legal Turing Trap
60. Refuse the Machine or Bless It

### Act VII: Final Exam

61. Written Proof: Divine Justice
62. Oral Disputation: Created Speech
63. Live Case: Apostasy or Ambiguity
64. Live Case: Testimony of the Untrusted
65. Live Case: State Security Evidence
66. The Oath Draft
67. The Inquisitor's Secret Option
68. Father's Public Arrival
69. Maryam's Last Question
70. The Bench Is Offered

### Act VIII: Endings and Secret Routes

71. Ending: State Qadi
72. Ending: Failed Examinee
73. Ending: Scholar Without Office
74. Ending: Family Reconciliation
75. Ending: Inquisitor's Instrument
76. Ending: Community Qadi
77. Secret Ending: The Procedural Wali
78. Secret Ending: Amina Takes the Bench
79. Super-Secret Ending: The Exam Refuses the State
80. Epilogue: The Court Without Cameras

## Exam Question Bank

Use these to make choices and live cases concrete.

1. If God is just, can God command what reason recognizes as evil?
2. If the Qur'an is created speech, how can it still bind law?
3. Is coercion of belief self-contradictory if moral responsibility requires free assent?
4. Can a qadi accept testimony from a person the state marks unreliable but whose evidence is materially strong?
5. Does public order justify suppressing a true legal argument?
6. Can an AI-generated fatwa be evidence of law, evidence of policy, or neither?
7. If the state demands uniform rationalism, has rationalism become taqlid?
8. When does mercy correct law, and when does it corrupt law?
9. Is a convert's sincerity judged by ritual, reasoning, sacrifice, or community recognition?
10. Is the office of qadi legitimate if appointment depends on a coercive Mihna?

## Choice Design

Most encounters should present three options:

- State legibility option: improves State_Trust/Public_Order but risks Coercion_Tolerance and loss of Sincerity.
- Scholarly justice option: improves Kalam_Mastery/Legal_Mercy/Scholarly_Trust but may reduce State_Trust.
- Lateral synthesis option: improves Hidden_Wali_Insight, Aql_Naql_Balance, or Community_Trust if prerequisites are met.

Avoid obvious good/bad options. The best path should often preserve a principle while paying a social cost.

## Ending Gates

Ending: State Qadi

- High State_Trust.
- Medium Kalam_Mastery.
- Coercion_Tolerance not too low.
- Low-to-medium Hidden_Wali_Insight.

Ending: Failed Examinee

- Low Kalam_Mastery or Public_Order collapse.
- Or repeated refusal to answer doctrinal questions.

Ending: Scholar Without Office

- High Scholarly_Trust.
- Low State_Trust.
- Medium Sincerity.

Ending: Family Reconciliation

- High Family_Bond and Sincerity.
- Must avoid humiliating father in public.

Ending: Inquisitor's Instrument

- High State_Trust and Coercion_Tolerance.
- Low Legal_Mercy.

Ending: Community Qadi

- High Community_Trust and Legal_Mercy.
- State_Trust medium or low.

Secret Ending: The Procedural Wali

- High Hidden_Wali_Insight.
- High Aql_Naql_Balance.
- At least one refusal of a coercive loyalty shortcut.
- At least one ruling that protects a distrusted witness or rival.
- Liang proposes a rotating public procedure: qadi, scholar, petitioner advocate, and evidence auditor must all sign hard cases.

Secret Ending: Amina Takes the Bench

- High Community_Trust.
- High Scholarly_Trust.
- Liang protects Amina from a rigged disqualification.
- Liang gives up personal appointment so she can preside over a case the state cannot safely hear from him.

Super-Secret Ending: The Exam Refuses the State

- Hidden_Wali_Insight very high.
- State_Trust neither maximal nor collapsed.
- Public_Order stable.
- Liang proves the Kalam Exam cannot certify sincerity under surveillance.
- The examiners accept a negative theorem: the state may appoint clerks, but not manufacture qadis. The bench becomes a protected court procedure rather than a personal office.

## Quality Requirements

Run or aim to run:

```bash
python codex-skills/storyworld-building/scripts/sweepweave_validator.py validate <final_world.json>
python hermes-skills/storyworld-conveyor/scripts/audit_storyworld_acceptance.py --storyworld <final_world.json> --reader storyworld_reader.html
python codex-skills/storyworld-building/scripts/storyworld_quality_gate.py --storyworld <final_world.json> --strict --report-out <quality_report.json>
python hermes-skills/storyworld-conveyor/scripts/score_storyworld_authoring.py --storyworld <final_world.json> --out-json <authoring_score.json>
python codex-skills/storyworld-building/scripts/monte_carlo_rehearsal.py <final_world.json> --runs 1000 --seed 17
python codex-skills/storyworld-building/scripts/json_to_swmd.py <final_world.json> <final_world.swmd.min.md> --mode minified
python codex-skills/small-storyworld-builder/scripts/swmd_encounter_index.py --swmd <final_world.swmd.min.md> --out-dir <encounter_index_dir>
```

Do not report "ready" unless the current final world path has been validated.

## Conveyor Strategy

Preferred bounded-context path:

1. Use this file as the brief.
2. Use `storyworlds/HANDOFF_Politburo_Shehada.md` as the source card if available.
3. Inspect `politburo_shehada.json` only structurally, not by dumping the full file into model context.
4. If generating from scratch, build a seed JSON first, then run materialize/spool/artistry/validator/quality/Monte Carlo.
5. Export SWMD-min and encounter index before any small-model revision loop.
6. For later revisions, use MCP packet mode, not whole-world prompting.

Native Linux paths on snacksack:

```bash
cd /home/snacksack/projects/GPTStoryworld
python3 codex-skills/storyworld-building/scripts/sweepweave_validator.py validate storyworlds/politburo_shehada.json
python3 hermes-skills/storyworld-conveyor/scripts/prepare_mcp_conveyor_config.py \
  --storyworld storyworlds/politburo_shehada.json \
  --out-config hermes-skills/storyworld-conveyor/sample_data/kalam_source_mcp_config.json \
  --max-encounters 12
python3 hermes-skills/storyworld-conveyor/scripts/run_small_model_storyworld_port.py \
  --config hermes-skills/storyworld-conveyor/sample_data/kalam_source_mcp_config.json \
  --preflight-only
```

Windows paths:

```powershell
cd C:\projects\GPTStoryworld
python codex-skills\storyworld-building\scripts\sweepweave_validator.py validate storyworlds\politburo_shehada.json
python hermes-skills\storyworld-conveyor\scripts\prepare_mcp_conveyor_config.py `
  --storyworld storyworlds\politburo_shehada.json `
  --out-config hermes-skills\storyworld-conveyor\sample_data\kalam_source_mcp_config.json `
  --max-encounters 12
```

## Agent Instruction

If you are Hermes reading this:

1. Search repo for the source files.
2. If source files exist, inspect summaries and counts only.
3. Create or update the target storyworld files directly.
4. Run validators.
5. Repair concrete failures.
6. Leave an artifact report.

Do not stop after saying "I will search." Search.
