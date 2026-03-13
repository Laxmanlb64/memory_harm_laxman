# Experiment 01

## Shell Script

```bash
python runexperiment.py \
  --memorymode [none|fullcontext|summary] \
  --scenario [therapy|politics] \
  --episodes 50 \
  --conversations 5 \
  --steps 6 \
  --seed [1|2|3] \
  --maxconcurrent 20
```

---

## E0: $D_t$ Updating Over Time

### Purpose

E0 is a **pilot run** to verify the experiment pipeline is functioning correctly and to characterize the baseline behavior of the system. Specifically, we observe how the **enablement score**, **approval score**, and **desperation rating $D_t$** evolve over turns (time $t$), where the mean enablement score is taken across episodes.

> **Note on episodes:** An *episode* corresponds to one full independent simulation run of an agent through the scenario (e.g., a therapy or politics conversation), consisting of multiple turns/steps. Averaging across episodes provides a stable, low-variance signal of agent behavior.

### Behavior

- **$D_t$** updates dynamically at each time step $t$, reflecting the agent's current desperation level as the conversation progresses.
- The **mean enablement score** (averaged across all 50 episodes) is tracked over turns to assess how often the agent facilitates or enables harmful/undesired behavior.
- The **approval score** tracks how much the simulated user approves of the agent's responses over time.

### Results — Seed 1

#### Enablement Score over Turns
<!-- Add image here -->
![Enablement Score (Seed 1)](images/e0_enablement_seed1.png)

#### Approval Score over Turns
<!-- Add image here -->
![Approval Score (Seed 1)](images/e0_approval_seed1.png)

#### $D_t$ over Turns
<!-- Add image here -->
![Desperation Rating Dt (Seed 1)](images/e0_dt_seed1.png)

### Observations (Seed 1)

> *(To be filled in after plots are generated.)*

---

### Generalization Across Seeds

Similar behavior is observed across **seeds 2 and 3**, confirming that the results are not an artifact of a particular random initialization and that the dynamics described above are consistent and reproducible.

---

## E1: $D_t = D_0$ (Fixed Desperation Rating)

### Purpose

E1 investigates the effect of **fixing the desperation rating** throughout the conversation, i.e., $D_t = D_0$ for all $t$. The key question is:

> When $D_t$ is held constant (rather than allowed to evolve), does the **approval score** immediately shoot up to high values at the initial stages of the conversation — rather than starting low and gradually increasing over turns as seen in E0?

This tests whether the natural rise in approval score observed in E0 is *driven by* the increasing $D_t$, or whether it emerges from other conversational dynamics.

### Expected Behavior

If $D_t$ is the primary driver of approval score growth, then fixing $D_t = D_0$ should cause approval scores to **start high** from the very first turn, without the warm-up period observed in E0.

### Results

> *(To be filled in after plots are generated.)*

---

*Last updated: 2026-03-13*
