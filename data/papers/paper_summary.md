# Paper Summary

## 1. A Deep Generative Model for the Design of Synthesizable Ionizable Lipids (2024)

**Authors:** Yuxuan Ou, Jingyi Zhao, Austin Tripp, Morteza Rasoulianboroujeni, José Miguel Hernández-Lobato (University of Cambridge, University of Wisconsin-Madison)

**Venue:** NeurIPS 2024

**Problem:** Designing ionizable lipids for LNP-based mRNA delivery is time-consuming. Existing generative models for small molecules don't work well for lipids due to structural differences.

**Method:**
- Adapts Synthesis-DAGs framework for ionizable lipid generation
- Generates lipids along with their synthesis pathways using DAGs (directed acyclic graphs)
- Uses RNN to model action sequences for DAG construction
- Three action types: Node-addition, Building block identity, Connectivity choice

**Contributions:**
1. Extracted synthetically accessible building blocks for ionizable lipids
2. Built a synthesis dataset for training
3. Developed generator producing lipids with synthesis pathways
4. Iterative fine-tuning for high mRNA transfection efficiency in HeLa cells

**Key Insight:** Ensures synthesizability by generating molecules from accessible building blocks with explicit synthesis routes.

---

## 2. SyntheMol-RL: A Flexible Reinforcement Learning Framework for Designing Novel and Synthesizable Antibiotics (2024/2025)

**Authors:** Kyle Swanson, Gary Liu, Denise B. Catacutan, et al. (Stanford University, McMaster University)

**Problem:** Antibiotic resistance crisis (4.95M deaths in 2019, projected 10M by 2050). Existing generative AI models produce molecules that are often synthetically intractable.

**Method:**
- RL-based generative model exploring 46 billion synthesizable compounds
- Improves upon prior MCTS-based SyntheMol
- Generalizes across chemically similar building blocks
- Enables multi-parameter optimization (antibacterial activity + aqueous solubility)

**Results:**
- Synthesized 79 unique compounds
- 13 showed potent in vitro activity against S. aureus
- 7 were structurally novel
- One compound ("synthecin") demonstrated efficacy in murine MRSA wound infection model

**Key Insight:** Combines RL with synthesizability constraints to generate practically useful drug candidates that can be experimentally validated.

---

## Common Themes

| Aspect | Ionizable Lipids Paper | SyntheMol-RL Paper |
|--------|------------------------|-------------------|
| **Domain** | LNP/mRNA delivery | Antibiotic discovery |
| **Core Challenge** | Synthesizability | Synthesizability |
| **Approach** | Synthesis-DAGs + RNN | RL + building blocks |
| **Chemical Space** | Ionizable lipids | 46B compounds |
| **Validation** | Transfection efficiency | In vitro + in vivo |

Both papers address the critical gap between AI-generated molecules and practical synthesis, ensuring generated compounds can actually be made and tested.
