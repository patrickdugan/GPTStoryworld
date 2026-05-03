# MC Formula Tuning Patch

- World: `C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\working_worlds\nine_lantern_27b_lattice_mc_tuned\nine_lantern_27b_lattice_mc_tuned.json`
- Source rows: 8
- Quality pass: True failures=[]
- Before MC: {'page_end_city_forgets': 0.382, 'page_end_shared_fault': 0.18600000000000003, 'page_end_magician_legend': 0.114, 'page_end_diplomat_state': 0.11199999999999999, 'page_end_corpse_reenthroned': 0.1, 'page_end_outside_causality': 0.078, 'page_end_witness_mask': 0.027999999999999997}
- After MC: {'page_end_shared_fault': 0.27399999999999997, 'page_end_city_forgets': 0.251, 'page_end_magician_legend': 0.128, 'page_end_corpse_reenthroned': 0.126, 'page_end_diplomat_state': 0.12, 'page_end_outside_causality': 0.071, 'page_end_witness_mask': 0.03}
- Balance delta: {'mae': -0.012285714285714289, 'dominance': -0.10800000000000004, 'minimum': 0.0020000000000000018}

Training interpretation: candidate MC actions become reliable TRM labels only after the patch's measured delta is known.
