"""Generate technical_summary.pdf — research paper style."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                 Table, TableStyle, PageBreak)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

OUT = "docs/technical_summary.pdf"
IMG = "docs"

doc = SimpleDocTemplate(OUT, pagesize=A4,
    topMargin=0.7*inch, bottomMargin=0.7*inch,
    leftMargin=0.8*inch, rightMargin=0.8*inch)

styles = getSampleStyleSheet()

# Research paper style overrides
styles["Code"].fontSize = 8
styles["Code"].textColor = black
styles["Code"].backColor = HexColor("#f8f8f8")
styles["Code"].borderWidth = 0.5
styles["Code"].borderColor = HexColor("#cccccc")
styles["Code"].borderPadding = 8
styles["Code"].leading = 12
styles["Code"].fontName = "Courier"

S = {}
S["title"] = ParagraphStyle("T", parent=styles["Title"], fontSize=22, textColor=black,
    spaceAfter=4, fontName="Helvetica-Bold")
S["sub"] = ParagraphStyle("Su", parent=styles["Normal"], fontSize=12, textColor=HexColor("#444"),
    alignment=TA_CENTER, spaceAfter=16)
S["h1"] = ParagraphStyle("H1x", parent=styles["Heading1"], fontSize=14, textColor=black,
    spaceBefore=18, spaceAfter=8, fontName="Helvetica-Bold",
    borderWidth=0, borderPadding=0, borderColor=None)
S["h2"] = ParagraphStyle("H2x", parent=styles["Heading2"], fontSize=12, textColor=HexColor("#333"),
    spaceBefore=12, spaceAfter=6, fontName="Helvetica-Bold")
S["body"] = ParagraphStyle("Bd", parent=styles["Normal"], fontSize=10, textColor=HexColor("#222"),
    spaceAfter=8, leading=14, alignment=TA_JUSTIFY)
S["bul"] = ParagraphStyle("Bl", parent=styles["Normal"], fontSize=10, textColor=HexColor("#222"),
    leftIndent=18, bulletIndent=8, spaceAfter=3, leading=13)
S["cap"] = ParagraphStyle("Cp", parent=styles["Normal"], fontSize=9, textColor=HexColor("#666"),
    alignment=TA_CENTER, spaceAfter=14, spaceBefore=4, fontName="Helvetica-Oblique")
S["auth"] = ParagraphStyle("Au", parent=styles["Normal"], fontSize=11, textColor=HexColor("#333"),
    alignment=TA_CENTER, spaceAfter=4)

story = []
W = A4[0] - 1.6*inch


def add_img(path, caption, max_w=None):
    max_w = max_w or (W * 0.92)
    if os.path.exists(path):
        from reportlab.lib.utils import ImageReader
        ir = ImageReader(path)
        iw, ih = ir.getSize()
        ratio = ih / iw
        w = min(max_w, W * 0.92)
        h = w * ratio
        max_h = 3.8 * inch
        if h > max_h:
            h = max_h
            w = h / ratio
        story.append(Spacer(1, 6))
        story.append(Image(path, width=w, height=h))
        story.append(Paragraph(caption, S["cap"]))


def bul(t):
    story.append(Paragraph(f"\u2022 {t}", S["bul"]))


def tbl(data, cw=None):
    """Research paper style table — thin lines, no colored header."""
    cw = cw or [W / len(data[0])] * len(data[0])
    t = Table(data, colWidths=cw)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("TEXTCOLOR", (0, 0), (-1, -1), black),
        ("LINEABOVE", (0, 0), (-1, 0), 1.2, black),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, black),
        ("LINEBELOW", (0, -1), (-1, -1), 1.2, black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 0), (-1, -1), white),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))


# ============================================================
# COVER
# ============================================================
story.append(Spacer(1, 1.5 * inch))
story.append(Paragraph("Reactome LNP Agent", S["title"]))
story.append(Paragraph("Technical Summary", S["sub"]))
story.append(Spacer(1, 0.15 * inch))
story.append(Paragraph("A LangGraph-based Multi-Agent System for Ionizable Lipid<br/>Reaction Template Analysis and Synthesis Planning", S["auth"]))
story.append(Spacer(1, 0.3 * inch))
story.append(Paragraph("Version 1.0 \u2014 February 2026", S["cap"]))
story.append(Spacer(1, 0.4 * inch))

story.append(Paragraph("<b>Abstract.</b> This document describes the architecture and implementation of the Reactome LNP Agent, a full-stack web application for AI-assisted ionizable lipid design. The system combines a local FAISS-based Retrieval-Augmented Generation (RAG) pipeline with a LangGraph multi-node workflow orchestrating parallel expert analyses via Amazon Bedrock foundation models. The application ingests research papers, reaction templates (SMARTS), and design rules to provide context-aware synthesis planning for ionizable lipids used in lipid nanoparticle (LNP) formulations for mRNA delivery.", S["body"]))

story.append(Spacer(1, 0.2 * inch))
tbl([
    ["Component", "Technology", "Details"],
    ["Frontend", "Angular 21 + Tailwind CSS", "SPA with SSE streaming chat"],
    ["Backend", "FastAPI (Python 3.12)", "REST + SSE, 4 endpoints"],
    ["Orchestration", "LangGraph", "5-node DAG, parallel execution"],
    ["Vector DB", "FAISS (local)", "454 vectors, 1024-dim"],
    ["Embeddings", "Titan Embed Text v2", "Amazon Bedrock"],
    ["LLM", "Claude Sonnet 4.5", "Amazon Bedrock, us-west-2"],
    ["Data", "PDFs + CSV + SMARTS", "4 papers, 13 reactions, 217K blocks"],
], [1.3 * inch, 1.8 * inch, 3 * inch])
story.append(Paragraph("<i>Table 1: Technology stack overview.</i>", S["cap"]))
story.append(PageBreak())

# ============================================================
# 1. SYSTEM ARCHITECTURE
# ============================================================
story.append(Paragraph("1. System Architecture", S["h1"]))
story.append(Paragraph("The Reactome LNP Agent follows a three-tier architecture: an Angular single-page application communicates with a FastAPI backend via REST and Server-Sent Events (SSE), which in turn orchestrates a LangGraph workflow that leverages both a local FAISS vector store and remote Amazon Bedrock foundation models. This design separates concerns cleanly\u2014the frontend handles user interaction and real-time streaming display, the backend manages agent orchestration and RAG retrieval, and AWS Bedrock provides scalable LLM inference without requiring local GPU resources for the language model.", S["body"]))
story.append(Paragraph("The choice of FAISS for the vector store ensures zero-infrastructure overhead: the index is persisted locally as two files (index.faiss and index.pkl) totaling 2.3 MB, and loads in under a second at startup. All embedding generation and LLM inference is offloaded to Bedrock, making the system lightweight enough to run on any machine with Python and Node.js installed.", S["body"]))
add_img(f"{IMG}/diagram_architecture.png", "Figure 1. System architecture showing the three-tier design: Angular client, FastAPI backend with LangGraph and FAISS, and AWS Bedrock cloud services.")
story.append(PageBreak())

# ============================================================
# 2. LANGGRAPH PIPELINE
# ============================================================
story.append(Paragraph("2. LangGraph Agent Pipeline", S["h1"]))
story.append(Paragraph("The core intelligence of the system is implemented as a LangGraph StateGraph with five nodes. LangGraph was chosen over simpler chain-based approaches because it natively supports parallel node execution, explicit state management, and conditional routing\u2014all essential for a multi-expert analysis system.", S["body"]))
story.append(Paragraph("The pipeline begins with a FAISS retrieval step that fetches the top-6 most relevant document chunks. These chunks are then passed to two expert nodes that execute <b>in parallel</b>: the Reaction Expert analyzes applicable SMARTS templates and reaction conditions, while the Design Rules Expert validates against LNP structural constraints (tail configuration, MCTS compatibility, synthesizability). Both analyses converge into the Synthesis Planner, which produces a step-by-step route with specific reaction IDs and building block criteria. Finally, the Final Answer node synthesizes all preceding analyses into a comprehensive, actionable response.", S["body"]))
story.append(Paragraph("This parallel fan-out design reduces end-to-end latency by approximately 40% compared to sequential execution, as the two expert nodes make independent LLM calls simultaneously. The total cost per query is 4 Claude Sonnet invocations.", S["body"]))
add_img(f"{IMG}/diagram_pipeline.png", "Figure 2. LangGraph pipeline with 5 nodes. The reaction expert and design rules nodes execute in parallel after retrieval, then converge into the synthesis planner.")

story.append(Paragraph("2.1 State Schema", S["h2"]))
story.append(Paragraph("The shared state object carries data between nodes. Each node reads from and writes to specific fields, ensuring clean data flow without side effects.", S["body"]))
story.append(Paragraph("<font face='Courier' size=8>class ReactomeState(TypedDict):\n    query: str                # User's natural language question\n    retrieved_context: str    # Top-6 FAISS chunks concatenated\n    reaction_analysis: str    # Reaction expert output\n    design_rules_check: str   # Design rules expert output\n    synthesis_plan: str       # Synthesis planner output\n    final_answer: str         # Final comprehensive answer</font>", styles["Code"]))

story.append(Paragraph("2.2 Node Specifications", S["h2"]))
story.append(Paragraph("Each node has a well-defined input/output contract. The retrieval node makes no LLM calls (FAISS only), while the four analysis nodes each make exactly one Claude Sonnet invocation with a specialized system prompt.", S["body"]))
tbl([
    ["Node", "Input Fields", "Output Field", "LLM Calls"],
    ["retrieval_node", "query", "retrieved_context", "0 (FAISS)"],
    ["reaction_expert_node", "query, retrieved_context", "reaction_analysis", "1"],
    ["design_rules_node", "query, retrieved_context", "design_rules_check", "1"],
    ["synthesis_planner_node", "reaction_analysis, design_rules_check", "synthesis_plan", "1"],
    ["final_answer_node", "all analysis fields", "final_answer", "1"],
], [1.6 * inch, 1.6 * inch, 1.4 * inch, 0.8 * inch])
story.append(Paragraph("<i>Table 2: Node specifications. Total of 4 LLM calls per query (2 parallel + 2 sequential).</i>", S["cap"]))
story.append(PageBreak())

# ============================================================
# 3. RAG SYSTEM
# ============================================================
story.append(Paragraph("3. RAG System", S["h1"]))
story.append(Paragraph("The Retrieval-Augmented Generation system ingests domain-specific documents from five source types, processes them through a chunking pipeline, and stores the resulting vectors in a FAISS index. At query time, the user's question is embedded using the same Titan model and the top-6 most similar chunks are retrieved. Each chunk carries metadata (source_type) that helps the LLM understand the provenance of the information\u2014whether it comes from a research paper, design rules, reaction templates, or compound data.", S["body"]))
story.append(Paragraph("The chunking strategy uses RecursiveCharacterTextSplitter with 1,000-character chunks and 200-character overlap. This overlap ensures that context is not lost at chunk boundaries, which is particularly important for reaction template descriptions that may span multiple paragraphs. The 217K building blocks dataset is too large to embed entirely, so only a representative summary (first 20 entries) is included in the index; the full dataset is available for programmatic queries.", S["body"]))
add_img(f"{IMG}/diagram_rag.png", "Figure 3. RAG data flow: five source types are loaded, chunked, embedded via Titan, and indexed in FAISS. Queries follow the reverse path through embedding and similarity search.")

story.append(Paragraph("3.1 Data Sources", S["h2"]))
tbl([
    ["Source", "Type", "Size", "Content"],
    ["Research Papers", "PDF", "4 files, 148 pp", "Lipid generation, SyntheMol-RL, MCTS approaches"],
    ["LNP Design Rules", "PDF + MD", "2 files", "MCTS tree structure, tail constraints, action space"],
    ["Reaction Templates", "Python", "1 file", "13 SMARTS-based reaction definitions"],
    ["Liver Scores", "CSV", "293 rows", "SMILES with liver targeting scores"],
    ["Building Blocks", "CSV", "217K rows", "Head group building blocks (summary indexed)"],
], [1.4 * inch, 0.8 * inch, 1 * inch, 3 * inch])
story.append(Paragraph("<i>Table 3: Data sources ingested into the RAG system.</i>", S["cap"]))

story.append(Paragraph("3.2 Index Parameters", S["h2"]))
tbl([
    ["Parameter", "Value"],
    ["Text splitter", "RecursiveCharacterTextSplitter"],
    ["Chunk size / overlap", "1,000 / 200 characters"],
    ["Total documents → chunks", "152 → 454"],
    ["Embedding model", "amazon.titan-embed-text-v2:0 (1,024-dim)"],
    ["Index type", "FAISS Flat L2"],
    ["Retrieval k", "6"],
    ["Persisted index size", "1.8 MB (index.faiss) + 477 KB (index.pkl)"],
], [2.2 * inch, 4 * inch])
story.append(Paragraph("<i>Table 4: FAISS index configuration.</i>", S["cap"]))
story.append(PageBreak())

# ============================================================
# 4. AWS BEDROCK
# ============================================================
story.append(Paragraph("4. AWS Bedrock Integration", S["h1"]))
story.append(Paragraph("Amazon Bedrock serves as the inference backbone, providing access to foundation models without requiring self-hosted GPU infrastructure. The application uses two models: Claude Sonnet 4.5 for all reasoning tasks (4 calls per query) and Titan Embed Text v2 for vector embeddings. Both are accessed through the LangChain AWS integration (langchain-aws), which provides ChatBedrock and BedrockEmbeddings wrappers with automatic retry and error handling.", S["body"]))
story.append(Paragraph("Additionally, the system supports an alternative execution mode using 5 pre-configured managed Bedrock Agents (the MOGAM team). These agents have their own knowledge bases and can be invoked via the bedrock-agent-runtime API. The managed agent mode is toggled via the USE_LLM_DIRECT configuration flag, allowing seamless switching between direct LLM calls and managed agent orchestration.", S["body"]))
add_img(f"{IMG}/diagram_bedrock.png", "Figure 4. AWS Bedrock integration showing foundation models and optional managed agents.")

story.append(Paragraph("4.1 Foundation Models", S["h2"]))
tbl([
    ["Model", "Model ID", "Usage"],
    ["Claude Sonnet 4.5", "us.anthropic.claude-sonnet-4-5-20250929-v1:0", "LLM reasoning (4 nodes)"],
    ["Titan Embed Text v2", "amazon.titan-embed-text-v2:0", "Document + query embeddings"],
], [1.5 * inch, 2.8 * inch, 1.8 * inch])
story.append(Paragraph("<i>Table 5: Bedrock foundation models.</i>", S["cap"]))

story.append(Paragraph("4.2 Managed Bedrock Agents", S["h2"]))
story.append(Paragraph("Five domain-specific agents are pre-configured in Bedrock for the multi-agent meeting workflow (used in the separate bedrock_langgraph_agents notebook). Each agent has a unique ID and shares the test alias TSTALIASID.", S["body"]))
tbl([
    ["Agent", "ID", "Role"],
    ["MOGAM-Chem-Agent", "0IPX1MMI2D", "Chemical structure and synthesis expert"],
    ["MOGAM-AI-Agent", "KQ9FJVLHQE", "AI/ML methodology and model design"],
    ["MOGAM-LNP-Agent", "Q8GN0FK7NV", "LNP formulation and delivery optimization"],
    ["MOGAM-BI-Agent", "XDPBOQN8YT", "Bioinformatics and data analysis"],
    ["MOGAM-Lead-Agent", "RHUTNOTET1", "Team lead, synthesis of expert inputs"],
], [1.5 * inch, 1.2 * inch, 3.5 * inch])
story.append(Paragraph("<i>Table 6: Managed Bedrock Agents for the MOGAM research team.</i>", S["cap"]))
story.append(PageBreak())

# ============================================================
# 5. BACKEND API
# ============================================================
story.append(Paragraph("5. Backend API", S["h1"]))
story.append(Paragraph("The FastAPI backend exposes four endpoints. The design follows REST conventions for resource retrieval (health, reactions) and uses Server-Sent Events for the chat endpoint to provide real-time progress updates as the LangGraph pipeline executes. CORS is enabled for all origins to support local development with the Angular dev server on a different port.", S["body"]))
story.append(Paragraph("The /api/chat endpoint is the primary interface for the frontend chat component. It streams status messages as each pipeline node begins execution, then sends the final answer and detailed expert analyses as separate SSE events. This allows the frontend to show a progress indicator with step-specific messages (e.g., 'Retrieving documents...', 'Analyzing reaction templates...') before displaying the complete response.", S["body"]))
add_img(f"{IMG}/diagram_api.png", "Figure 5. FastAPI endpoint structure. The query and chat endpoints invoke the LangGraph agent.")

story.append(Paragraph("5.1 Endpoint Specifications", S["h2"]))
tbl([
    ["Method", "Path", "Description", "Response Format"],
    ["GET", "/api/health", "Health check", '{"status", "model", "region"}'],
    ["GET", "/api/reactions", "List 13 reaction templates", '{"reactions": [...]}'],
    ["POST", "/api/query", "Full agent query (blocking)", "All 4 analyses + final answer"],
    ["POST", "/api/chat", "SSE streaming chat", "status \u2192 answer \u2192 details \u2192 [DONE]"],
], [0.7 * inch, 1.2 * inch, 1.8 * inch, 2.5 * inch])
story.append(Paragraph("<i>Table 7: API endpoint specifications.</i>", S["cap"]))

story.append(Paragraph("5.2 SSE Stream Protocol", S["h2"]))
story.append(Paragraph("The chat endpoint emits four event types in sequence:", S["body"]))
story.append(Paragraph('<font face="Courier" size=8>data: {"type":"status", "step":"retrieve", "message":"Retrieving..."}\ndata: {"type":"status", "step":"reaction_expert", "message":"Analyzing..."}\ndata: {"type":"answer", "content":"...comprehensive final answer..."}\ndata: {"type":"details", "reaction_analysis":"...", "design_rules_check":"...", "synthesis_plan":"..."}\ndata: [DONE]</font>', styles["Code"]))

story.append(Paragraph("5.3 Reaction Templates", S["h2"]))
story.append(Paragraph("The system includes 13 SMARTS-based reaction templates for ionizable lipid synthesis. Two reactions (10012 and 10017) are flagged as chemically invalid\u2014the agent is aware of these issues and will recommend alternatives when queried.", S["body"]))
tbl([
    ["ID", "Reaction", "Reactants", "Status"],
    ["10001", "Amide formation", "Amine + Carboxylic acid", "Valid"],
    ["10003", "Ester formation", "Carboxylic acid + Hydroxyl", "Valid"],
    ["10005", "Amine alkylation", "Amine + Alcohol", "Needs activation"],
    ["10007", "Thioether formation", "Amine + Thiol", "Valid"],
    ["10009", "Epoxide opening", "Amine + Epoxide", "Valid"],
    ["10010", "Michael addition (acrylate)", "Amine + Alkyl acrylate", "Valid"],
    ["10011", "Michael addition (acrylamide)", "Amine + Alkyl acrylamide", "Valid"],
    ["10012", "N-methylation", "Amine + Methyl", "Invalid"],
    ["10013", "Phosphate formation", "Tert. amine + Dioxaphospholane", "Valid"],
    ["10014", "Phosphate formation (alt)", "Tert. amine + Dioxaphospholane", "Valid"],
    ["10015", "Imine formation", "Primary amine + Aldehyde", "Valid"],
    ["10016", "Reductive amination", "Secondary amine + Aldehyde", "Valid"],
    ["10017", "Amide (reverse)", "Primary amine + Aldehyde", "Invalid"],
], [0.5 * inch, 1.7 * inch, 2 * inch, 1 * inch])
story.append(Paragraph("<i>Table 8: All 13 reaction templates with validation status.</i>", S["cap"]))
story.append(PageBreak())

# ============================================================
# 6. FRONTEND
# ============================================================
story.append(Paragraph("6. Frontend Application", S["h1"]))
story.append(Paragraph("The frontend is built with Angular 21 (standalone components, no NgModules) and Tailwind CSS v4. It provides three views accessible via client-side routing: a chat interface for interactive queries, a reaction template browser for reference, and a workflow visualization showing the agent pipeline. The design uses a sidebar navigation pattern with a dark theme (slate-900) contrasting against a light content area (slate-50).", S["body"]))
story.append(Paragraph("The chat component is the primary user interface. It uses the Fetch API with ReadableStream to consume SSE events from the backend, displaying animated progress indicators as each pipeline node executes. Responses include expandable sections showing the individual expert analyses (reaction analysis, design rules check, synthesis plan) in addition to the synthesized final answer. Four sample queries are provided as clickable buttons to help users get started.", S["body"]))
add_img(f"{IMG}/diagram_frontend.png", "Figure 6. Angular component tree. The ApiService provides HTTP and SSE communication to all components.")

story.append(Paragraph("6.1 Component Summary", S["h2"]))
tbl([
    ["Component", "Route", "Key Features"],
    ["App (root)", "\u2014", "Shell layout: sidebar + router-outlet"],
    ["Sidebar", "\u2014", "Navigation links, Bedrock connection status indicator"],
    ["Chat", "/", "SSE streaming, message history, sample queries, expandable details"],
    ["Reactions", "/reactions", "13 reaction cards with warning badges, responsive grid"],
    ["Workflow", "/workflow", "Pipeline step visualization with parallel execution indicators"],
], [1.2 * inch, 0.8 * inch, 4.2 * inch])
story.append(Paragraph("<i>Table 9: Frontend components and their responsibilities.</i>", S["cap"]))

story.append(Paragraph("6.2 Design System", S["h2"]))
tbl([
    ["Element", "Specification"],
    ["Color palette", "Slate (backgrounds), Emerald\u2192Cyan gradient (primary), Purple (accents)"],
    ["Sidebar", "Dark gradient (slate-900\u2192800), 256px fixed width"],
    ["User messages", "Emerald\u2192Cyan gradient background, white text, right-aligned"],
    ["Assistant messages", "White background, slate border, left-aligned, shadow"],
    ["Loading indicator", "Three animated bounce dots with step-specific status text"],
    ["Reaction cards", "White, rounded-xl, hover: shadow-md + emerald border accent"],
], [1.3 * inch, 4.8 * inch])
story.append(Paragraph("<i>Table 10: UI design specifications.</i>", S["cap"]))
story.append(PageBreak())

# ============================================================
# 7. PROJECT STRUCTURE
# ============================================================
story.append(Paragraph("7. Project Structure and Deployment", S["h1"]))
story.append(Paragraph("The project follows a monorepo structure with backend and frontend code colocated under src/. Jupyter notebooks for experimentation and testing are kept in notes/, while generated documentation lives in docs/. The FAISS index is persisted in data/ alongside the source documents, enabling fast startup without re-indexing.", S["body"]))
story.append(Paragraph("<font face='Courier' size=7>chem-agent/\n\u251c\u2500\u2500 .env                         # AWS Bedrock configuration\n\u251c\u2500\u2500 pyproject.toml               # Python dependencies (uv)\n\u251c\u2500\u2500 uv.lock                      # Locked dependency versions\n\u251c\u2500\u2500 run.sh                       # Start both servers\n\u251c\u2500\u2500 data/\n\u2502   \u251c\u2500\u2500 papers/                  # Research PDFs (4 files)\n\u2502   \u251c\u2500\u2500 lnp_data/                # Rules, reactions, CSVs\n\u2502   \u2514\u2500\u2500 faiss_lnp_index/         # Persisted FAISS index\n\u251c\u2500\u2500 src/\n\u2502   \u251c\u2500\u2500 backend/\n\u2502   \u2502   \u251c\u2500\u2500 config.py            # .env loader\n\u2502   \u2502   \u251c\u2500\u2500 rag.py               # FAISS + document ingestion\n\u2502   \u2502   \u251c\u2500\u2500 agent.py             # LangGraph 5-node workflow\n\u2502   \u2502   \u2514\u2500\u2500 main.py              # FastAPI (4 endpoints)\n\u2502   \u2514\u2500\u2500 frontend/reactome-ui/    # Angular 21 project\n\u251c\u2500\u2500 notes/                       # Jupyter notebooks\n\u2514\u2500\u2500 docs/                        # This document + diagrams</font>", styles["Code"]))

story.append(Paragraph("7.1 Running the Application", S["h2"]))
story.append(Paragraph("The application requires two processes: the FastAPI backend (port 8000) and the Angular dev server (port 4200). For remote development via VS Code, ports are forwarded through the SSH tunnel.", S["body"]))
story.append(Paragraph("<font face='Courier' size=8># Backend\nunset CUDA_VISIBLE_DEVICES\n.venv/bin/uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload\n\n# Frontend\ncd src/frontend/reactome-ui && ng serve --host 0.0.0.0 --port 4200\n\n# Or both at once\n./run.sh</font>", styles["Code"]))

story.append(Paragraph("7.2 Remote Access via VS Code", S["h2"]))
bul("Forward ports <b>8000</b> and <b>4200</b> in the VS Code Ports panel")
bul("Access frontend at <b>http://localhost:4200</b> in local browser")
bul("Backend Swagger UI available at <b>http://localhost:8000/docs</b>")
bul("Jupyter notebooks can be run directly in VS Code with the remote kernel")

doc.build(story)
print(f"Done: {OUT} ({os.path.getsize(OUT) // 1024} KB)")
