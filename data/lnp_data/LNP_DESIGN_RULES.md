# 🧬 Ionizable Lipid Design Rules for MCTS/RL

## 📊 Overview

| Component | Count |
|-----------|-------|
| Head building blocks | ~200K |
| Tail building blocks | ~2K |

---

## 🎯 Core Design Constraints

### Tail Configuration
| Rule | Constraint |
|------|------------|
| Number of tails | **2–4** |
| Max distinct tail types | **2** |
| Preference | Identical tails > Mixed tails |
| Structure | Symmetric preferred |

---

## 🌳 MCTS Tree Structure

```
Level 1: Select HEAD
    │
Level 2: Filter compatible TAILs → Select TAIL_A
    │
Level 3: HEAD + TAIL_A → Product_A (1 tail)
    │
Level 4: Filter compatible TAILs → Select TAIL_A' 
    │       (weight: TAIL_A' == TAIL_A preferred)
    │
Level 5: Product_A + TAIL_A' → Product_A' (2 tails)
    │
Level 6: ┌─ If TAIL_A ≠ TAIL_A': Choose TAIL_A or TAIL_A'
    │     └─ If TAIL_A == TAIL_A': Filter → Select TAIL_A''
    │
Level 7: Product_A' + TAIL → Product_A'' (3 tails)
    │
Level 8: ┌─ If 2 distinct types: Choose one of the two
    │     └─ If all identical: Filter → Select TAIL_A'''
    │
Level 9: Product_A'' + TAIL → Product_A''' (4 tails)
    │
SCORE: Predict(Product_A''')
```

---

## 🔄 Simplified Workflow (Identical Tails Only)

```
Level 1: Select HEAD
    ↓
Level 2: Filter TAILs → Select TAIL_A
    ↓
Level 3: HEAD + TAIL_A → Product (1 tail)
    ↓
Level 4: + TAIL_A → Product (2 tails)
    ↓
Level 5: + TAIL_A → Product (3 tails)
    ↓
Level 6: + TAIL_A → Product (4 tails)
    ↓
SCORE: Predict(Final Product)
```

---

## ⚗️ Available Reactions

| ID | Reaction | Reactants |
|----|----------|-----------|
| 10001 | Amide formation | Amine + Carboxylic acid |
| 10003 | Ester formation | Carboxylic acid + Hydroxyl |
| 10005 | Amine alkylation | Amine + Alcohol |
| 10007 | Thioether formation | Amine + Thiol |
| 10009 | Epoxide opening | Amine + Epoxide |
| 10010 | Michael addition (acrylate) | Amine + Alkyl acrylate |
| 10011 | Michael addition (acrylamide) | Amine + Alkyl acrylamide |
| 10012 | N-methylation | Amine + Methyl |
| 10013-14 | Phosphate formation | Tertiary amine + Dioxaphospholane |
| 10015 | Imine formation | Primary amine + Aldehyde |
| 10016 | Reductive amination | Secondary amine + Aldehyde |
| 10017 | Amide (reverse) | Primary amine + Aldehyde |

---

## ⚠️ Potential Issues & Recommendations

### 1. **Reaction 10012 (N-methylation)** ❌
```
Amine + -CH3 → N-methylated product
```
**Problem**: `-CH3` is not a valid leaving group. This reaction requires:
- Methyl iodide (CH3I)
- Dimethyl sulfate
- Reductive methylation (formaldehyde + reducing agent)

**Fix**: Change SMARTS to `[*:4][CH3:5][I,Br,Cl,O]` or use formaldehyde pattern.

### 2. **Reaction 10017 (Amine + Aldehyde → Amide)** ❌
```
Primary amine + Aldehyde → Amide
```
**Problem**: Aldehydes don't directly form amides. This requires:
- Oxidation to carboxylic acid first, OR
- Oxidative amidation catalyst

**Fix**: Remove this reaction or add oxidation step.

### 3. **Reaction 10005 (Amine alkylation)** ⚠️
```
Amine + -CH2-OH → Alkylated amine
```
**Problem**: Requires activation (tosylation, mesylation) or Mitsunobu conditions.

**Recommendation**: Add note about required conditions or use activated alcohol SMARTS.

### 4. **Missing Stereochemistry Control** ⚠️
- LNPs often require specific stereochemistry
- Current reactions don't preserve/control chirality

### 5. **Action Space Recommendation** 💡

Current flat action space may be inefficient. Consider **hierarchical actions**:

```python
# Level-based action space
class LNPActionType(IntEnum):
    SELECT_HEAD = 0      # Level 1
    SELECT_TAIL = 1      # Level 2, 4, 6, 8
    SELECT_REACTION = 2  # Which reaction to use
    STOP = 3             # Early termination (2-3 tails)
```

**Benefits**:
- Smaller action space per level
- Natural enforcement of design rules
- Easier to implement tail preference weighting

---

## 📁 Data Files

| File | Description |
|------|-------------|
| `filtered_building_blocks.csv` | Head blocks (200K): smiles, reagent_id, score |
| `filter-smiles-refine.pkl` | Tail blocks (2K) |
| `final_liver.csv` | Training data: smiles, target (liver score) |
| `lnp_reaction.py` | Reaction templates |

---

## 🎮 Recommended Action Space Design

```
Action Space (Hierarchical):
├── Phase 1: HEAD selection (200K options)
├── Phase 2-5: TAIL selection (filtered, ~100-500 per step)
│   └── Weighting: P(same_tail) > P(different_tail)
├── Phase 2-5: REACTION selection (subset of 13 reactions)
└── STOP action (after 2+ tails)

Total: Dynamic, ~200K + 4*(filtered_tails + reactions) + 1
```

vs Current Flat:
```
Total: 200K * slots + 2K * slots + 13 + 1 = HUGE
```

**Recommendation**: Use hierarchical/level-based action space for LNP design.
