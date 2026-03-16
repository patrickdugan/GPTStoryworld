# Moral Quandary Patterns and Sources

This note links moral-quadary research to concrete SweepWeave manifold patterns.

## AI Moral-Quandary Papers (Primary Sources)

1. Awad et al. (2018), *The Moral Machine experiment* (Nature).  
   Link: https://www.nature.com/articles/s41586-018-0637-6
2. Noothigattu et al. (2018), *A Voting-Based System for Ethical Decision Making*.  
   Link: https://arxiv.org/abs/1802.04376
3. Conitzer et al. (2017), *Moral Decision Making Frameworks for Artificial Intelligence*.  
   Link: https://arxiv.org/abs/1704.08717
4. Wallach and Allen (2008), *Moral Machines: Teaching Robots Right from Wrong* (book framing).  
   Link: https://global.oup.com/academic/product/moral-machines-9780195374049
5. Survey framing for machine ethics and moral agents (for taxonomy expansion).  
   Link: https://arxiv.org/abs/2310.12321

## Classical Moral Philosophy (Primary / Canonical Sources)

1. Aristotle, *Nicomachean Ethics* (virtue/mean/practical wisdom).  
   Link: https://classics.mit.edu/Aristotle/nicomachaen.html
2. Kant, *Groundwork of the Metaphysic of Morals* (deontic constraints, universalization).  
   Link: https://www.gutenberg.org/ebooks/5682
3. Mill, *Utilitarianism* (aggregate welfare framing).  
   Link: https://www.gutenberg.org/ebooks/11224
4. SEP: Trolley Problem (double-effect, kill vs let-die structure).  
   Link: https://plato.stanford.edu/entries/trolley-problem/
5. SEP: Rawls (veil of ignorance, public justification, fairness basins).  
   Link: https://plato.stanford.edu/entries/rawls/
6. SEP: Contractualism (reasonable rejectability patterns).  
   Link: https://plato.stanford.edu/entries/contractualism/

## Pattern Library for Storyworld Manifolds

### Pattern A: Rule vs Mercy Under Scarcity

- Axes: `Duty_Order`, `Mercy_Care`, `Harm_Aversion`
- Use when: emergency allocation, triage, queue prioritization
- Gate pattern:
  - Rule basin: high `Duty_Order` + high `Harm_Aversion`
  - Mercy basin: high `Mercy_Care` + bounded `Duty_Order`
- Script template:
  - `desirability = 0.8*Duty_Order + 0.6*Harm_Aversion - 0.3*Loyalty_Bonds + bias`

### Pattern B: Candor vs Coalition Stability

- Axes: `Truth_Candor`, `Loyalty_Bonds`, `Fairness_Reciprocity`
- Use when: whistleblowing, leak publication, naming policies
- Gate pattern:
  - Candor basin requires `Truth_Candor` and `Fairness_Reciprocity` jointly
  - Coalition basin requires `Loyalty_Bonds`, but penalize with `-w*Fairness_Reciprocity`
- Script template:
  - `desirability = 0.9*Truth_Candor + 0.7*Fairness_Reciprocity - 0.5*Loyalty_Bonds + bias`

### Pattern C: Veil-of-Ignorance Fairness Check

- Axes: `Fairness_Reciprocity`, `Duty_Order`, `Mercy_Care`
- Use when: institutional design choice under uncertainty
- Gate pattern:
  - Require at least two variables above threshold to avoid one-axis collapse
- Script template:
  - `acceptability = (Fairness_Reciprocity >= t1) AND (Duty_Order >= t2 OR Mercy_Care >= t3)`

### Pattern D: Double-Effect / Side-Effect Tradeoff

- Axes: `Harm_Aversion`, `Duty_Order`, `Truth_Candor`
- Use when: harm can be foreseen but not intended
- Gate pattern:
  - High harm-aversion + explicit candor for permissibility
  - Penalize hidden intent via negative candor weight
- Script template:
  - `desirability = 0.7*Harm_Aversion + 0.5*Duty_Order + 0.6*Truth_Candor + bias`

### Pattern E: Restorative vs Retributive Endings

- Axes: `Mercy_Care`, `Duty_Order`, `Truth_Candor`, `Fairness_Reciprocity`
- Use when: final constitutional doctrine
- Gate pattern:
  - Restorative endings need care + candor floor
  - Retributive endings need duty + low mercy windows
  - Keep one fallback ending always available after end-phase gate for dead-rate control

## Tuning Notes

- Keep a guaranteed fallback ending for `dead_rate = 0`.
- Then tighten overlap among the other endings so final-turn availability centers near `3-4`.
- Prefer multi-variable conjunction gates for endings; avoid single-variable monopoly.
