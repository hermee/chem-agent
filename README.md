# 🧬 Reactome LNP Agent

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Angular](https://img.shields.io/badge/Angular-21-DD0031?style=for-the-badge&logo=angular&logoColor=white)](https://angular.io/)
[![Rust](https://img.shields.io/badge/Rust-1.83-000000?style=for-the-badge&logo=rust&logoColor=white)](https://www.rust-lang.org/)
[![Dioxus](https://img.shields.io/badge/Dioxus-0.6-4A90E2?style=for-the-badge&logo=rust&logoColor=white)](https://dioxuslabs.com/)
[![AWS Bedrock](https://img.shields.io/badge/AWS_Bedrock-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/bedrock/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> **AI-powered multi-agent system for ionizable lipid design and synthesis planning using LangGraph, AWS Bedrock, and RDKit**

A full-stack application combining Retrieval-Augmented Generation (RAG) with parallel expert analysis for designing ionizable lipids used in lipid nanoparticle (LNP) formulations for mRNA delivery.

---

## ✨ Features

- 🤖 **Multi-Agent LangGraph Pipeline** - 5-node DAG with parallel expert execution
- 🧠 **AWS Bedrock Integration** - Claude Sonnet 4.5 + Titan Embeddings
- 📚 **RAG System** - FAISS vector store with 33 research papers (4,800+ vectors)
- 🔬 **Molecular Analysis** - RDKit-powered property scoring (QED, SA Score, LogP, TPSA)
- 💬 **Real-time Streaming** - SSE-based chat with live progress updates
- 🎨 **Modern UI** - Angular 21 + Tailwind CSS v4
- 🖥️ **Cross-Platform Desktop** - Dioxus-based native apps (Linux/macOS/Windows)
- 🧪 **13 Reaction Templates** - SMARTS-based synthesis planning

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Angular    │  │   Dioxus     │  │   Desktop    │     │
│  │   Web App    │  │   WASM App   │  │   (Dioxus)   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │      FastAPI Backend (6 endpoints)  │
          │  ┌────────────────────────────────┐ │
          │  │   LangGraph Agent Pipeline     │ │
          │  │  ┌──────────┐  ┌──────────┐   │ │
          │  │  │ Reaction │  │  Design  │   │ │
          │  │  │  Expert  │  │  Rules   │   │ │
          │  │  └────┬─────┘  └────┬─────┘   │ │
          │  │       └──────┬───────┘         │ │
          │  │              ▼                 │ │
          │  │      Synthesis Planner         │ │
          │  └────────────────────────────────┘ │
          │  ┌────────────────────────────────┐ │
          │  │  FAISS Vector Store (local)    │ │
          │  │  • 454 chunks, 1024-dim        │ │
          │  │  • 33 research papers          │ │
          │  └────────────────────────────────┘ │
          └──────────────────┬──────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │         AWS Bedrock (us-west-2)     │
          │  • Claude Sonnet 4.5 (LLM)          │
          │  • Titan Embed Text v2 (Embeddings) │
          └─────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Rust 1.83+ (for desktop apps)
- AWS credentials with Bedrock access

### 1. Clone & Setup

```bash
git clone https://github.com/hermee/chem-agent.git
cd chem-agent

# Install Python dependencies
uv sync

# Install Angular dependencies
cd src/frontend/reactome-ui
npm install
cd ../../..
```

### 2. Configure AWS

```bash
# Create .env file
cat > .env << EOF
AWS_REGION=us-west-2
AWS_PROFILE=default
MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
EOF
```

### 3. Run the Application

```bash
# Start both backend and frontend
./run.sh

# Or separately:
# Backend (port 8000)
.venv/bin/uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (port 4200)
cd src/frontend/reactome-ui && ng serve --host 0.0.0.0 --port 4200
```

Access at: **http://localhost:4200**

---

## 🖥️ Desktop Applications

### Dioxus Standalone (Molecular Analysis)

```bash
cd standalone
trunk build --release
python serve.py  # http://localhost:8001
```

### Dioxus Desktop (Full App)

```bash
cd standalone-desktop
./build.sh
./target/release/lnp-desktop
```

**Requirements:** Backend on port 8000, Angular on port 4200

---

## 📊 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI + Python 3.12 | REST API + SSE streaming |
| **Orchestration** | LangGraph | Multi-agent workflow (5 nodes) |
| **LLM** | Claude Sonnet 4.5 (Bedrock) | Expert analysis & synthesis planning |
| **Embeddings** | Titan Embed Text v2 | Document & query vectorization |
| **Vector DB** | FAISS (local) | 454 chunks, 1024-dim embeddings |
| **Molecular** | RDKit | Property scoring & 2D visualization |
| **Frontend** | Angular 21 + Tailwind CSS | SPA with real-time chat |
| **Desktop** | Dioxus 0.6 (Rust) | Cross-platform native apps |
| **Data** | 33 PDFs + CSV + SMARTS | Research papers + reactions + building blocks |

---

## 🔬 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check + model info |
| `GET` | `/api/reactions` | List 13 reaction templates |
| `POST` | `/api/query` | Full agent query (blocking) |
| `POST` | `/api/chat` | SSE streaming chat |
| `POST` | `/api/analyze` | RDKit molecular analysis |
| `POST` | `/api/analyze-batch` | Batch molecular analysis |

**Swagger UI:** http://localhost:8000/docs

---

## 📁 Project Structure

```
chem-agent/
├── src/
│   ├── backend/
│   │   ├── main.py              # FastAPI app (6 endpoints)
│   │   ├── agent.py             # LangGraph 5-node pipeline
│   │   ├── rag.py               # FAISS + document ingestion
│   │   └── config.py            # AWS Bedrock config
│   └── frontend/reactome-ui/    # Angular 21 app
├── standalone/                  # Dioxus WASM (molecular analysis)
├── standalone-desktop/          # Dioxus desktop (full app)
├── data/
│   ├── papers/                  # 33 research PDFs
│   ├── lnp_data/                # Reactions, rules, CSVs
│   └── faiss_lnp_index/         # Persisted FAISS index
├── docs/
│   ├── technical_summary_v1.pdf # Full technical documentation
│   └── generate_pdf_v1.py       # PDF generator
└── notes/                       # Jupyter notebooks
```

---

## 🧪 Reaction Templates

13 SMARTS-based reaction templates for ionizable lipid synthesis:

- ✅ Amide formation
- ✅ Ester formation
- ✅ Amine alkylation
- ✅ Thioether formation
- ✅ Epoxide opening
- ✅ Michael addition (acrylate/acrylamide)
- ✅ Phosphate formation
- ✅ Imine formation
- ✅ Reductive amination
- ⚠️ N-methylation (flagged as invalid)
- ⚠️ Amide reverse (flagged as invalid)

---

## 📚 Data Sources

| Source | Type | Count | Description |
|--------|------|-------|-------------|
| Research Papers | PDF | 3 | Core lipid generation papers |
| Related Papers | PDF | 30 | LNP design, ML, diffusion models |
| Design Rules | PDF/MD | 2 | MCTS constraints, action space |
| Reaction Templates | Python | 13 | SMARTS-based reactions |
| Liver Scores | CSV | 293 | SMILES with targeting scores |
| Building Blocks | CSV | 217K | Head group building blocks |

---

## 🎯 Use Cases

1. **Synthesis Planning** - Generate step-by-step synthesis routes for target lipids
2. **Reaction Analysis** - Identify applicable SMARTS templates and conditions
3. **Design Validation** - Check against LNP structural constraints
4. **Property Scoring** - Calculate QED, SA Score, LogP, TPSA, etc.
5. **Literature Search** - RAG-powered retrieval from 33 research papers

---

## 🔧 Development

### Remote Development (VS Code)

1. Forward ports 8000 and 4200
2. Run `./run.sh` on remote server
3. Access via `http://localhost:4200` on local machine

### Build Desktop Apps

```bash
# Standalone WASM
cd standalone && trunk build --release

# Desktop app
cd standalone-desktop && ./build.sh
```

---

## 📖 Documentation

- **Technical Summary:** [`docs/technical_summary_v1.pdf`](docs/technical_summary_v1.pdf)
- **API Docs:** http://localhost:8000/docs (Swagger UI)
- **Desktop README:** [`standalone-desktop/README.md`](standalone-desktop/README.md)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **AWS Bedrock** - Foundation models (Claude Sonnet 4.5, Titan Embeddings)
- **LangChain/LangGraph** - Multi-agent orchestration framework
- **RDKit** - Molecular property calculations
- **Dioxus** - Cross-platform Rust UI framework
- **MOGAM Research Team** - Domain expertise and validation

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

<div align="center">

**Built with ❤️ for the LNP research community**

[![GitHub](https://img.shields.io/badge/GitHub-hermee%2Fchem--agent-181717?style=for-the-badge&logo=github)](https://github.com/hermee/chem-agent)

</div>
