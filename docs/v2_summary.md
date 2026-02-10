# Reactome LNP Agent — v2 Summary

## What Changed (v1 → v2)

### Agent Architecture
- **v1**: 5-node pipeline with 3 hardcoded experts (Reaction, Design Rules, Synthesis Planner)
- **v2**: 10-node pipeline with 7 YAML-configured agents (Router, 5 parallel workers, Lead Agent supervisor)

### New Agents
| Agent | File | Role |
|-------|------|------|
| Router | `src/agents/router.yaml` | Classifies queries → synthesis / lookup / general |
| Reaction Expert | `src/agents/reaction_expert.yaml` | SMARTS template matching, feasibility |
| Lipid Design Expert | `src/agents/lipid_design_expert.yaml` | Retrosynthesis + SAR + design rules (merged from 3 v1 experts) |
| Generative AI Expert | `src/agents/generative_ai_expert.yaml` | De novo generation + RL optimization (NEW) |
| Property Prediction Expert | `src/agents/property_prediction_expert.yaml` | ML models + uncertainty quantification (NEW) |
| Literature Scout | `src/agents/literature_scout.yaml` | PubMed, PubChem, web search (NEW) |
| Lead Agent | `src/agents/lead_agent.yaml` | Supervisor — conflict resolution, confidence levels |

### YAML-Driven Configuration
- All agent prompts, model params, and tools defined in `src/agents/*.yaml`
- `system.yaml` master config with 6 global constraints auto-injected into every agent
- `src/agents/__init__.py` loader with `get_system_prompt()`, `load_all_agents()`

### Backend Changes (`src/backend/`)
- `agent.py` — 10-node LangGraph StateGraph with conditional routing
  - New nodes: `rewrite_query`, `router`, LLM-based reranking in `retrieve`
  - 5 parallel expert workers for synthesis queries
  - Lookup queries → literature only; General → literature + web
- `tools.py` — NEW: PubMed (NCBI E-utils), PubChem (PUG REST), web search (DDG)
- `main.py` — Updated SSE protocol with all 10 node status events, 6 expert detail fields, file upload endpoint (`/api/chat-with-files`)
- State fields changed: `design_rules_check` + `synthesis_plan` → `lipid_design_analysis` + `generative_analysis` + `prediction_analysis`

### Frontend Changes (`src/frontend/reactome-ui/`)
- `api.ts` — Updated `ChatMessage.details` and `QueryResult` interfaces for 6 expert fields
- `conversation.ts` — NEW: localStorage-backed conversation persistence (up to 20)
- `chat.html` — 6 collapsible expert detail panels, file upload UI
- `sidebar.html` — Conversation list with new/delete/select, date grouping
- `workflow.ts` — 10-step pipeline visualization with parallel indicators

### Documentation
- `docs/technical_summary_v2.pdf` — 18 pages, syntax-highlighted code blocks, wrapped tables
- `docs/generate_pdf_v2.py` — PDF generator with Python/YAML/SSE/shell syntax highlighting
- `notes/reactome_lnp_agent_workflow_v2.pdf` — Graphviz workflow diagram

### Tests
- `tests/backend/` — API, agent, chemistry, and tools test specs

---

## Standalone & Desktop Apps

> **Key principle**: The standalone (web) and standalone-desktop (native GUI) apps are **performance comparison builds** of the same frontend — they must be visually identical to the Angular frontend and use the same backend API.

### Architecture

```
┌─────────────────────────────────────────────────────┐
│              Same FastAPI Backend (port 8000)        │
│         agent.py + rag.py + tools.py + main.py      │
└──────────┬──────────────┬──────────────┬────────────┘
           │              │              │
    ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼─────────┐
    │  Angular 21 │ │  Dioxus    │ │  Dioxus      │
    │  Web App    │ │  WASM Web  │ │  Desktop     │
    │  (port 4200)│ │  (port 8001)│ │  (native)   │
    │  TypeScript │ │  Rust/WASM │ │  Rust/wry    │
    └─────────────┘ └────────────┘ └──────────────┘
     Reference UI    Same UI         Same UI
                     Web perf test   macOS/Win/Linux
```

### Rules

1. **Same backend** — All three frontends hit the same FastAPI backend on port 8000. No separate backends.
2. **Identical UI** — The Dioxus apps must replicate the Angular frontend pixel-for-pixel: same layout, colors, components, interactions, and responsive behavior.
3. **Purpose** — Compare framework performance (Angular vs Dioxus WASM vs Dioxus native) with identical UI and backend, isolating only the frontend runtime as the variable.
4. **Framework** — Both standalone apps are built with **Dioxus**:
   - `standalone/` — Dioxus WASM, compiled with Trunk, served via Python HTTP server
   - `standalone-desktop/` — Dioxus desktop (wry/tao), native GUI app, primarily for **macOS** users but cross-platform (Linux/Windows)
5. **Feature parity** — Must support all features: SSE chat streaming, conversation persistence, expert detail panels, reaction browser, workflow visualization, file upload, SMILES analysis.

### Current Status

The standalone apps currently implement only molecular analysis (SMILES scoring). They need to be updated to match the full Angular frontend with all v2 features.

### Build

```bash
# Standalone WASM (port 8001)
cd standalone && trunk build --release && python serve.py

# Desktop (native binary)
cd standalone-desktop && ./build.sh && ./target/release/lnp-desktop
```
