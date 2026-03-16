---
title: "Orbit Null Jurisdiction"
version: "0.1.9"
storyworld_id: "SW-3603d266-936c-4f7e-a2c2-71eb93509a98"
environment_type: "SWEEPWEAVE_STORYWORLD"
source_format: "SWMD-0-MIN"
state_variables:
  - "Heat_Resolve"
  - "Mask_Reveal"
  - "Phase_Clock"
  - "Signal_Noise"
  - "Sync_Drift"
  - "Yield_Override"
endings:
  - id: "page_end_drift"
    type: "terminal"
    condition: "AND(ARITHMETIC COMPARATOR(P(char_kernel.Phase_Clock),C(0.91)),ARITHMETIC COMPARATOR(P(char_kernel.Sync_Drift),C(0.38)))"
    description: "Var wins. Adaptive error becomes governor."
    expected_critic_score: 0
    proximity_spec:
      - var: "Phase_Clock"
        op: ">="
        threshold: 0.91
      - var: "Sync_Drift"
        op: ">="
        threshold: 0.38
  - id: "page_end_fallback"
    type: "terminal"
    condition: "ARITHMETIC COMPARATOR(P(char_kernel.Phase_Clock),C(0.86))"
    description: "No basin clears. Orbit Null persists by brittle truce."
    expected_critic_score: 0
    proximity_spec:
      - var: "Phase_Clock"
        op: ">="
        threshold: 0.86
  - id: "page_end_override"
    type: "terminal"
    condition: "AND(ARITHMETIC COMPARATOR(P(char_kernel.Phase_Clock),C(0.91)),ARITHMETIC COMPARATOR(P(char_kernel.Yield_Override),C(0.42)))"
    description: "Authority wins. Command outranks consensus."
    expected_critic_score: 0
    proximity_spec:
      - var: "Phase_Clock"
        op: ">="
        threshold: 0.91
      - var: "Yield_Override"
        op: ">="
        threshold: 0.42
  - id: "page_end_reveal"
    type: "terminal"
    condition: "AND(ARITHMETIC COMPARATOR(P(char_kernel.Phase_Clock),C(0.91)),ARITHMETIC COMPARATOR(P(char_kernel.Mask_Reveal),C(0.36)),ARITHMETIC COMPARATOR(P(char_kernel.Yield_Override),C(0.24)))"
    description: "Witness wins. Authority survives by becoming inspectable."
    expected_critic_score: 0
    proximity_spec:
      - var: "Phase_Clock"
        op: ">="
        threshold: 0.91
      - var: "Mask_Reveal"
        op: ">="
        threshold: 0.36
      - var: "Yield_Override"
        op: "<="
        threshold: 0.24
  - id: "page_end_stable"
    type: "terminal"
    condition: "AND(ARITHMETIC COMPARATOR(P(char_kernel.Phase_Clock),C(0.91)),ARITHMETIC COMPARATOR(P(char_kernel.Signal_Noise),C(-0.18)),ARITHMETIC COMPARATOR(P(char_kernel.Heat_Resolve),C(0.12)))"
    description: "Ledger wins. Procedure becomes quiet enough to trust."
    expected_critic_score: 0
    proximity_spec:
      - var: "Phase_Clock"
        op: ">="
        threshold: 0.91
      - var: "Signal_Noise"
        op: "<="
        threshold: -0.18
      - var: "Heat_Resolve"
        op: ">="
        threshold: 0.12
---

# SWMD-0-MIN
id: SW-3603d266-936c-4f7e-a2c2-71eb93509a98
title: Orbit Null Jurisdiction

ENC page_start turn=0..0
ORX opt_page_start_0/rxn_page_start_0_a -> wild | O:dock silent route | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.16)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(-0.08)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.28)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(-0.06)) | D:ADD(P(char_kernel.Signal_Noise),P(char_kernel.Heat_Resolve),C(0.08))
ORX opt_page_start_0/rxn_page_start_0_b -> wild | O:dock silent route | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.08)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.18)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.04)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.14)) | D:ADD(P(char_kernel.Yield_Override),MUL(P(char_kernel.Signal_Noise),-1),C(0.04))
ORX opt_page_start_1/rxn_page_start_1_a -> wild | O:dock declared route | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(-0.04)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.24)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.04)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.18)) | D:ADD(P(char_kernel.Mask_Reveal),P(char_kernel.Sync_Drift),C(0.07))
ORX opt_page_start_1/rxn_page_start_1_b -> wild | O:dock declared route | E:SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.14)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.08)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.24)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.06)) | D:ADD(P(char_kernel.Sync_Drift),P(char_kernel.Yield_Override),C(0.03))

ENC page_a1_lock turn=0..0
ORX opt_page_a1_lock_0/rxn_page_a1_lock_0_a -> page_a1_router | O:seal route | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(-0.12)); SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.18)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.04)) | D:ADD(P(char_kernel.Signal_Noise),P(char_kernel.Heat_Resolve),C(0.06))
ORX opt_page_a1_lock_0/rxn_page_a1_lock_0_b -> page_a1_router | O:seal route | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(-0.06)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.16)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.12)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.08)) | D:ADD(P(char_kernel.Signal_Noise),P(char_kernel.Mask_Reveal),C(0.02))
ORX opt_page_a1_lock_1/rxn_page_a1_lock_1_a -> page_a1_router | O:split route | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.2)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.1)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.06)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.08)) | D:ADD(P(char_kernel.Heat_Resolve),P(char_kernel.Signal_Noise),C(0.05))
ORX opt_page_a1_lock_1/rxn_page_a1_lock_1_b -> page_a1_router | O:split route | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.12)); SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.08)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.08)) | D:ADD(P(char_kernel.Heat_Resolve),MUL(P(char_kernel.Heat_Resolve),-1),C(0.01))

ENC page_a1_mirror turn=0..0
ORX opt_page_a1_mirror_0/rxn_page_a1_mirror_0_a -> page_a1_router | O:echo witness | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.18)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(-0.12)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.04)) | D:ADD(P(char_kernel.Mask_Reveal),P(char_kernel.Sync_Drift),C(0.06))
ORX opt_page_a1_mirror_0/rxn_page_a1_mirror_0_b -> page_a1_router | O:echo witness | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(-0.06)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.12)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.16)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.08)) | D:ADD(P(char_kernel.Mask_Reveal),P(char_kernel.Mask_Reveal),C(0.02))
ORX opt_page_a1_mirror_1/rxn_page_a1_mirror_1_a -> page_a1_router | O:skew witness | E:SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(-0.1)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.06)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.2)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.08)) | D:ADD(P(char_kernel.Sync_Drift),P(char_kernel.Mask_Reveal),C(0.05))
ORX opt_page_a1_mirror_1/rxn_page_a1_mirror_1_b -> page_a1_router | O:skew witness | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.08)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.12)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.08)) | D:ADD(P(char_kernel.Sync_Drift),MUL(P(char_kernel.Heat_Resolve),-1),C(0.01))

ENC page_a1_shunt turn=0..0
ORX opt_page_a1_shunt_0/rxn_page_a1_shunt_0_a -> page_a1_router | O:raise auth | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.12)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.18)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.04)) | D:ADD(P(char_kernel.Yield_Override),P(char_kernel.Signal_Noise),C(0.06))
ORX opt_page_a1_shunt_0/rxn_page_a1_shunt_0_b -> page_a1_router | O:raise auth | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(-0.06)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.16)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.08)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.12)) | D:ADD(P(char_kernel.Yield_Override),P(char_kernel.Mask_Reveal),C(0.02))
ORX opt_page_a1_shunt_1/rxn_page_a1_shunt_1_a -> page_a1_router | O:bleed auth | E:SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.2)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.06)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.08)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.1)) | D:ADD(P(char_kernel.Signal_Noise),P(char_kernel.Yield_Override),C(0.05))
ORX opt_page_a1_shunt_1/rxn_page_a1_shunt_1_b -> page_a1_router | O:bleed auth | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.08)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.12)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.08)) | D:ADD(P(char_kernel.Signal_Noise),MUL(P(char_kernel.Heat_Resolve),-1),C(0.01))

ENC page_a1_drift turn=0..0
ORX opt_page_a1_drift_0/rxn_page_a1_drift_0_a -> page_a1_router | O:keep var | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(-0.12)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.18)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.04)) | D:ADD(P(char_kernel.Sync_Drift),P(char_kernel.Mask_Reveal),C(0.06))
ORX opt_page_a1_drift_0/rxn_page_a1_drift_0_b -> page_a1_router | O:keep var | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(-0.06)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.16)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.08)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.12)) | D:ADD(P(char_kernel.Sync_Drift),P(char_kernel.Mask_Reveal),C(0.02))
ORX opt_page_a1_drift_1/rxn_page_a1_drift_1_a -> page_a1_router | O:stiffen mesh | E:SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.2)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.06)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(-0.1)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.08)) | D:ADD(P(char_kernel.Mask_Reveal),P(char_kernel.Sync_Drift),C(0.05))
ORX opt_page_a1_drift_1/rxn_page_a1_drift_1_b -> page_a1_router | O:stiffen mesh | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.12)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.08)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.08)) | D:ADD(P(char_kernel.Mask_Reveal),MUL(P(char_kernel.Heat_Resolve),-1),C(0.01))

ENC page_a1_router turn=0..0
ORX opt_page_a1_router_0/rxn_page_a1_router_0_a -> wild | O:route cold | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.06)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.22)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.16)) | D:ADD(P(char_kernel.Signal_Noise),MUL(P(char_kernel.Heat_Resolve),-1),C(0.05))
ORX opt_page_a1_router_0/rxn_page_a1_router_0_b -> wild | O:route cold | E:SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.22)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.12)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(-0.04)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.14)) | D:ADD(P(char_kernel.Yield_Override),MUL(P(char_kernel.Signal_Noise),-1),C(0.02))
ORX opt_page_a1_router_1/rxn_page_a1_router_1_a -> wild | O:route loud | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(-0.04)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.18)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.22)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.16)) | D:ADD(P(char_kernel.Mask_Reveal),P(char_kernel.Sync_Drift),C(0.06))
ORX opt_page_a1_router_1/rxn_page_a1_router_1_b -> wild | O:route loud | E:SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.22)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.06)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.18)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.06)) | D:ADD(P(char_kernel.Sync_Drift),P(char_kernel.Yield_Override),C(0.02))

ENC page_a2_audit turn=0..0
ORX opt_page_a2_audit_0/rxn_page_a2_audit_0_a -> page_a2_router | O:pass ledger | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.18)); SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.12)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.04)) | D:ADD(P(char_kernel.Heat_Resolve),P(char_kernel.Signal_Noise),C(0.06))
ORX opt_page_a2_audit_0/rxn_page_a2_audit_0_b -> page_a2_router | O:pass ledger | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.12)); SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(-0.06)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.16)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.08)) | D:ADD(P(char_kernel.Heat_Resolve),P(char_kernel.Mask_Reveal),C(0.02))
ORX opt_page_a2_audit_1/rxn_page_a2_audit_1_a -> page_a2_router | O:spoof ledger | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(-0.1)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.2)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.06)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.08)) | D:ADD(P(char_kernel.Signal_Noise),P(char_kernel.Heat_Resolve),C(0.05))
ORX opt_page_a2_audit_1/rxn_page_a2_audit_1_b -> page_a2_router | O:spoof ledger | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.08)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.12)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.08)) | D:ADD(P(char_kernel.Signal_Noise),MUL(P(char_kernel.Heat_Resolve),-1),C(0.01))

ENC page_a2_fork turn=0..0
ORX opt_page_a2_fork_0/rxn_page_a2_fork_0_a -> page_a2_router | O:open fork | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(-0.12)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.18)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.04)) | D:ADD(P(char_kernel.Yield_Override),P(char_kernel.Mask_Reveal),C(0.06))
ORX opt_page_a2_fork_0/rxn_page_a2_fork_0_b -> page_a2_router | O:open fork | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(-0.06)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.16)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.08)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.12)) | D:ADD(P(char_kernel.Yield_Override),P(char_kernel.Mask_Reveal),C(0.02))
ORX opt_page_a2_fork_1/rxn_page_a2_fork_1_a -> page_a2_router | O:hide fork | E:SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.2)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.06)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.08)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.1)) | D:ADD(P(char_kernel.Mask_Reveal),P(char_kernel.Yield_Override),C(0.05))
ORX opt_page_a2_fork_1/rxn_page_a2_fork_1_b -> page_a2_router | O:hide fork | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.12)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.08)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.08)) | D:ADD(P(char_kernel.Mask_Reveal),MUL(P(char_kernel.Heat_Resolve),-1),C(0.01))

ENC page_a2_sink turn=0..0
ORX opt_page_a2_sink_0/rxn_page_a2_sink_0_a -> page_a2_router | O:raise heat | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.18)); SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(-0.12)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.04)) | D:ADD(P(char_kernel.Heat_Resolve),P(char_kernel.Sync_Drift),C(0.06))
ORX opt_page_a2_sink_0/rxn_page_a2_sink_0_b -> page_a2_router | O:raise heat | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.12)); SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(-0.06)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.16)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.08)) | D:ADD(P(char_kernel.Heat_Resolve),P(char_kernel.Mask_Reveal),C(0.02))
ORX opt_page_a2_sink_1/rxn_page_a2_sink_1_a -> page_a2_router | O:cool sink | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(-0.1)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.06)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.2)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.08)) | D:ADD(P(char_kernel.Sync_Drift),P(char_kernel.Heat_Resolve),C(0.05))
ORX opt_page_a2_sink_1/rxn_page_a2_sink_1_b -> page_a2_router | O:cool sink | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.08)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.12)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.08)) | D:ADD(P(char_kernel.Sync_Drift),MUL(P(char_kernel.Heat_Resolve),-1),C(0.01))

ENC page_a2_resync turn=0..0
ORX opt_page_a2_resync_0/rxn_page_a2_resync_0_a -> page_a2_router | O:resync up | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.18)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.12)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.04)) | D:ADD(P(char_kernel.Sync_Drift),P(char_kernel.Yield_Override),C(0.06))
ORX opt_page_a2_resync_0/rxn_page_a2_resync_0_b -> page_a2_router | O:resync up | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(-0.06)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.16)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.08)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.12)) | D:ADD(P(char_kernel.Sync_Drift),P(char_kernel.Mask_Reveal),C(0.02))
ORX opt_page_a2_resync_1/rxn_page_a2_resync_1_a -> page_a2_router | O:resync side | E:SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.06)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(-0.1)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.08)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.2)) | D:ADD(P(char_kernel.Yield_Override),P(char_kernel.Sync_Drift),C(0.05))
ORX opt_page_a2_resync_1/rxn_page_a2_resync_1_b -> page_a2_router | O:resync side | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.08)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.12)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.08)) | D:ADD(P(char_kernel.Yield_Override),MUL(P(char_kernel.Heat_Resolve),-1),C(0.01))

ENC page_a2_router turn=0..0
ORX opt_page_a2_router_0/rxn_page_a2_router_0_a -> wild | O:route narrow | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.06)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.24)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.16)) | D:ADD(P(char_kernel.Signal_Noise),MUL(P(char_kernel.Heat_Resolve),-1),C(0.05))
ORX opt_page_a2_router_0/rxn_page_a2_router_0_b -> wild | O:route narrow | E:SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.24)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.12)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(-0.04)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.14)) | D:ADD(P(char_kernel.Yield_Override),MUL(P(char_kernel.Signal_Noise),-1),C(0.02))
ORX opt_page_a2_router_1/rxn_page_a2_router_1_a -> wild | O:route unstable | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(-0.04)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.18)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.24)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.16)) | D:ADD(P(char_kernel.Mask_Reveal),P(char_kernel.Sync_Drift),C(0.06))
ORX opt_page_a2_router_1/rxn_page_a2_router_1_b -> wild | O:route unstable | E:SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.24)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.06)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.18)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.06)) | D:ADD(P(char_kernel.Sync_Drift),P(char_kernel.Yield_Override),C(0.02))

ENC page_a3_consensus turn=0..0
ORX opt_page_a3_consensus_0/rxn_page_a3_consensus_0_a -> wild | O:seal basin | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.14)); SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.06)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.18)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.08)) | D:ADD(P(char_kernel.Heat_Resolve),P(char_kernel.Signal_Noise),C(0.07))
ORX opt_page_a3_consensus_0/rxn_page_a3_consensus_0_b -> wild | O:seal basin | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.1)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.1)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.18)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.06)) | D:ADD(P(char_kernel.Heat_Resolve),P(char_kernel.Mask_Reveal),C(0.02))
ORX opt_page_a3_consensus_1/rxn_page_a3_consensus_1_a -> wild | O:reopen basin | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(-0.1)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.18)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.12)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.08)) | D:ADD(P(char_kernel.Signal_Noise),P(char_kernel.Heat_Resolve),C(0.04))
ORX opt_page_a3_consensus_1/rxn_page_a3_consensus_1_b -> wild | O:reopen basin | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.08)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.18)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(0.08)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.08)) | D:ADD(P(char_kernel.Signal_Noise),MUL(P(char_kernel.Heat_Resolve),-1),C(0.01))

ENC page_a3_override turn=0..0
ORX opt_page_a3_override_0/rxn_page_a3_override_0_a -> wild | O:take auth | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(-0.08)); SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.06)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.18)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.14)) | D:ADD(P(char_kernel.Yield_Override),P(char_kernel.Heat_Resolve),C(0.07))
ORX opt_page_a3_override_0/rxn_page_a3_override_0_b -> wild | O:take auth | E:SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.1)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.18)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.06)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.1)) | D:ADD(P(char_kernel.Yield_Override),P(char_kernel.Mask_Reveal),C(0.02))
ORX opt_page_a3_override_1/rxn_page_a3_override_1_a -> wild | O:throttle auth | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.12)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.18)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.08)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.1)) | D:ADD(P(char_kernel.Heat_Resolve),P(char_kernel.Yield_Override),C(0.04))
ORX opt_page_a3_override_1/rxn_page_a3_override_1_b -> wild | O:throttle auth | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.08)); SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.08)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.18)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.08)) | D:ADD(P(char_kernel.Heat_Resolve),MUL(P(char_kernel.Heat_Resolve),-1),C(0.01))

ENC page_a3_reveal turn=0..0
ORX opt_page_a3_reveal_0/rxn_page_a3_reveal_0_a -> wild | O:open frame | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.06)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.14)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.18)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(-0.08)) | D:ADD(P(char_kernel.Mask_Reveal),P(char_kernel.Sync_Drift),C(0.07))
ORX opt_page_a3_reveal_0/rxn_page_a3_reveal_0_b -> wild | O:open frame | E:SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.1)); SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.1)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.18)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.06)) | D:ADD(P(char_kernel.Mask_Reveal),P(char_kernel.Mask_Reveal),C(0.02))
ORX opt_page_a3_reveal_1/rxn_page_a3_reveal_1_a -> wild | O:open witness | E:SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(-0.1)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.18)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.12)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.08)) | D:ADD(P(char_kernel.Sync_Drift),P(char_kernel.Mask_Reveal),C(0.04))
ORX opt_page_a3_reveal_1/rxn_page_a3_reveal_1_b -> wild | O:open witness | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.08)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.18)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.08)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.08)) | D:ADD(P(char_kernel.Sync_Drift),MUL(P(char_kernel.Heat_Resolve),-1),C(0.01))

ENC page_a3_drift turn=0..0
ORX opt_page_a3_drift_0/rxn_page_a3_drift_0_a -> wild | O:keep var | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.06)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.18)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.14)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.08)) | D:ADD(P(char_kernel.Sync_Drift),P(char_kernel.Yield_Override),C(0.07))
ORX opt_page_a3_drift_0/rxn_page_a3_drift_0_b -> wild | O:keep var | E:SET char_kernel.Mask_Reveal = NUDGE(P(char_kernel.Mask_Reveal),C(0.1)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.18)); SET char_kernel.Signal_Noise = NUDGE(P(char_kernel.Signal_Noise),C(-0.06)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.1)) | D:ADD(P(char_kernel.Sync_Drift),P(char_kernel.Mask_Reveal),C(0.02))
ORX opt_page_a3_drift_1/rxn_page_a3_drift_1_a -> wild | O:collapse var | E:SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.18)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(-0.1)); SET char_kernel.Sync_Drift = NUDGE(P(char_kernel.Sync_Drift),C(0.08)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.12)) | D:ADD(P(char_kernel.Yield_Override),P(char_kernel.Sync_Drift),C(0.04))
ORX opt_page_a3_drift_1/rxn_page_a3_drift_1_b -> wild | O:collapse var | E:SET char_kernel.Heat_Resolve = NUDGE(P(char_kernel.Heat_Resolve),C(0.08)); SET char_kernel.Phase_Clock = NUDGE(P(char_kernel.Phase_Clock),C(0.18)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(0.08)); SET char_kernel.Yield_Override = NUDGE(P(char_kernel.Yield_Override),C(-0.08)) | D:ADD(P(char_kernel.Yield_Override),MUL(P(char_kernel.Heat_Resolve),-1),C(0.01))

ENC page_end_stable turn=0..0

ENC page_end_reveal turn=0..0

ENC page_end_override turn=0..0

ENC page_end_drift turn=0..0

ENC page_end_fallback turn=0..0
