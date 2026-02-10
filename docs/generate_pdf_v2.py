"""Generate technical_summary_v2.pdf — updated for 6-agent architecture."""
import os, re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                 Table, TableStyle, PageBreak, Preformatted)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

OUT = "docs/technical_summary_v2.pdf"
IMG = "docs"

doc = SimpleDocTemplate(OUT, pagesize=A4,
    topMargin=0.7*inch, bottomMargin=0.7*inch,
    leftMargin=0.8*inch, rightMargin=0.8*inch)

styles = getSampleStyleSheet()

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

# Table cell styles — wrapping Paragraphs
S["th"] = ParagraphStyle("Th", fontName="Helvetica-Bold", fontSize=9, leading=11,
    textColor=black, alignment=TA_LEFT)
S["td"] = ParagraphStyle("Td", fontName="Helvetica", fontSize=9, leading=11,
    textColor=HexColor("#222"), alignment=TA_LEFT)

story = []
W = A4[0] - 1.6*inch

# ── Syntax highlighting colors ──
C_KW   = "#0000cc"   # keywords (class, def, import, from, etc.)
C_STR  = "#008800"   # strings
C_COM  = "#888888"   # comments
C_TYPE = "#aa5500"   # types / builtins
C_DECO = "#aa00aa"   # decorators / special

PY_KEYWORDS = {
    "class", "def", "import", "from", "return", "if", "else", "elif", "for",
    "in", "while", "try", "except", "with", "as", "not", "and", "or", "is",
    "None", "True", "False", "yield", "raise", "pass", "lambda", "async", "await",
}
PY_TYPES = {"str", "int", "float", "dict", "list", "tuple", "bool", "set", "TypedDict", "Optional"}

YAML_KEYWORDS = {"true", "false", "null", "yes", "no"}


def _esc(t):
    """Escape XML entities for ReportLab Paragraph."""
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _color(text, color):
    return f'<font color="{color}">{text}</font>'


def _highlight_python(code: str) -> str:
    """Syntax-highlight Python code for ReportLab Paragraph."""
    lines = code.split("\n")
    out = []
    for line in lines:
        # Preserve leading whitespace as non-breaking spaces
        stripped = line.lstrip(" ")
        indent = "&nbsp;" * (len(line) - len(stripped))

        # Comment line
        if stripped.startswith("#"):
            out.append(indent + _color(_esc(stripped), C_COM))
            continue

        result = ""
        i = 0
        s = stripped
        while i < len(s):
            # Strings
            if s[i] in ('"', "'"):
                q = s[i]
                # Triple quote
                if s[i:i+3] in ('"""', "'''"):
                    end = s.find(q*3, i+3)
                    if end == -1: end = len(s) - 3
                    tok = s[i:end+3]
                    result += _color(_esc(tok), C_STR)
                    i = end + 3
                    continue
                end = s.find(q, i+1)
                if end == -1: end = len(s) - 1
                tok = s[i:end+1]
                result += _color(_esc(tok), C_STR)
                i = end + 1
                continue
            # Inline comment
            if s[i] == "#":
                result += _color(_esc(s[i:]), C_COM)
                break
            # Word tokens
            m = re.match(r'[A-Za-z_]\w*', s[i:])
            if m:
                word = m.group()
                if word in PY_KEYWORDS:
                    result += _color(_esc(word), C_KW)
                elif word in PY_TYPES:
                    result += _color(_esc(word), C_TYPE)
                else:
                    result += _esc(word)
                i += len(word)
                continue
            result += _esc(s[i])
            i += 1

        out.append(indent + result)
    return "<br/>".join(out)


def _highlight_yaml(code: str) -> str:
    """Syntax-highlight YAML code for ReportLab Paragraph."""
    lines = code.split("\n")
    out = []
    for line in lines:
        stripped = line.lstrip(" ")
        indent = "&nbsp;" * (len(line) - len(stripped))

        if stripped.startswith("#"):
            out.append(indent + _color(_esc(stripped), C_COM))
            continue

        # key: value
        m = re.match(r'^([\w_.-]+)(\s*:\s*)(.*)', stripped)
        if m:
            key, sep, val = m.group(1), m.group(2), m.group(3)
            colored_val = _esc(val)
            if val.startswith('"') or val.startswith("'"):
                colored_val = _color(_esc(val), C_STR)
            elif val.startswith("[") or val.startswith("{"):
                colored_val = _color(_esc(val), C_TYPE)
            elif val.strip().lower() in YAML_KEYWORDS:
                colored_val = _color(_esc(val), C_KW)
            out.append(indent + _color(_esc(key), C_KW) + _esc(sep) + colored_val)
            continue

        # List items
        if stripped.startswith("- "):
            item = stripped[2:]
            if item.startswith('"') or item.startswith("'"):
                out.append(indent + _esc("- ") + _color(_esc(item), C_STR))
            else:
                out.append(indent + _esc("- ") + _esc(item))
            continue

        out.append(indent + _esc(stripped))
    return "<br/>".join(out)


def _highlight_shell(code: str) -> str:
    """Syntax-highlight shell commands."""
    lines = code.split("\n")
    out = []
    for line in lines:
        stripped = line.lstrip(" ")
        indent = "&nbsp;" * (len(line) - len(stripped))
        if stripped.startswith("#"):
            out.append(indent + _color(_esc(stripped), C_COM))
        else:
            out.append(indent + _esc(stripped))
    return "<br/>".join(out)


def _highlight_sse(code: str) -> str:
    """Syntax-highlight SSE protocol examples."""
    lines = code.split("\n")
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("data:"):
            prefix = _color("data:", C_KW)
            rest = stripped[5:]
            # Color JSON keys
            rest = re.sub(r'"(\w+)"(\s*:)', lambda m: _color(f'"{m.group(1)}"', C_TYPE) + m.group(2), _esc(rest))
            # Color string values
            rest = re.sub(r':\s*"([^"]*)"', lambda m: ': ' + _color(f'"{m.group(1)}"', C_STR), rest)
            out.append(prefix + rest)
        else:
            out.append(_esc(stripped))
    return "<br/>".join(out)


def _highlight_tree(code: str) -> str:
    """Syntax-highlight directory tree."""
    lines = code.split("\n")
    out = []
    for line in lines:
        # Comments after #
        if "#" in line:
            parts = line.split("#", 1)
            out.append(_esc(parts[0]) + _color("#" + _esc(parts[1]), C_COM))
        elif line.strip().endswith("/"):
            out.append(_color(_esc(line), C_KW))
        else:
            out.append(_esc(line))
    return "<br/>".join(out)


def code_block(code: str, lang: str = "python"):
    """Add a syntax-highlighted code block."""
    highlighters = {
        "python": _highlight_python,
        "yaml": _highlight_yaml,
        "shell": _highlight_shell,
        "sse": _highlight_sse,
        "tree": _highlight_tree,
    }
    hl = highlighters.get(lang, _highlight_shell)
    html = hl(code.strip())

    code_style = ParagraphStyle("CodeBlock", fontName="Courier", fontSize=7.5,
        leading=10.5, textColor=HexColor("#222"), backColor=HexColor("#f6f8fa"),
        borderWidth=0.5, borderColor=HexColor("#d0d7de"), borderPadding=8,
        spaceBefore=4, spaceAfter=10, leftIndent=0)
    story.append(Paragraph(html, code_style))


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
    """Table with Paragraph-wrapped cells for proper text wrapping."""
    cw = cw or [W / len(data[0])] * len(data[0])
    # Convert strings to Paragraphs
    wrapped = []
    for r, row in enumerate(data):
        style = S["th"] if r == 0 else S["td"]
        wrapped.append([Paragraph(str(cell), style) for cell in row])
    t = Table(wrapped, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 1.2, black),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, black),
        ("LINEBELOW", (0, -1), (-1, -1), 1.2, black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 0), (-1, -1), white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, HexColor("#fafafa")]),
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
story.append(Paragraph("A LangGraph-based Multi-Agent System for Ionizable Lipid<br/>Design, Synthesis Planning, and Property Prediction", S["auth"]))
story.append(Spacer(1, 0.3 * inch))
story.append(Paragraph("Version 2.0 \u2014 February 2026", S["cap"]))
story.append(Spacer(1, 0.4 * inch))

story.append(Paragraph("<b>Abstract.</b> This document describes the architecture and implementation of the Reactome LNP Agent v2, a full-stack web application for AI-assisted ionizable lipid design. Version 2 introduces a 6-agent supervisor/worker architecture with YAML-driven prompt configuration, replacing the previous 3-expert pipeline. The system now features a query router for intelligent classification, five parallel domain experts (Reaction Compatibility, Lipid Design, Generative AI, Property Prediction, and Literature Scout), and a Lead Reasoning Agent that critically evaluates and synthesizes all expert outputs. External tool integration adds live PubMed, PubChem, and web search capabilities. The system combines Retrieval-Augmented Generation (RAG) with a FAISS vector store (33 research papers, 454 chunks) and Amazon Bedrock foundation models (Claude Sonnet 4.5 + Titan Embeddings). The frontend has been updated with conversation persistence, expanded expert detail panels, and a revised workflow visualization reflecting the new pipeline.", S["body"]))

story.append(Spacer(1, 0.2 * inch))
tbl([
    ["Component", "Technology", "Details"],
    ["Frontend", "Angular 21 + Tailwind CSS v4", "SPA with SSE streaming, conversation persistence"],
    ["Backend", "FastAPI (Python 3.12)", "REST + SSE, 7 endpoints"],
    ["Orchestration", "LangGraph", "10-node DAG, 5 parallel workers + supervisor"],
    ["Agent Config", "YAML definitions", "6 agents + system config + router"],
    ["Mol. Analysis", "RDKit", "QED, SA Score, LogP, TPSA, 2D SVG"],
    ["Vector DB", "FAISS (local)", "454 chunks, 1024-dim embeddings"],
    ["Embeddings", "Titan Embed Text v2", "Amazon Bedrock"],
    ["LLM", "Claude Sonnet 4.5", "Amazon Bedrock, us-west-2"],
    ["External Tools", "PubMed, PubChem, Web", "Live search via NCBI E-utils, PUG REST, DDG"],
    ["Data", "PDFs + CSV + SMARTS", "33 papers, 13 reactions, 217K blocks"],
    ["Standalone Web", "Dioxus 0.6 (WASM)", "Trunk-built, Python-served, RDKit analysis"],
    ["Desktop App", "wry 0.47 + tao (Rust)", "Native webview, embedded Angular build"],
], [1.3 * inch, 1.8 * inch, 3 * inch])
story.append(Paragraph("<i>Table 1: Technology stack overview.</i>", S["cap"]))
story.append(PageBreak())

# ============================================================
# 1. SYSTEM ARCHITECTURE
# ============================================================
story.append(Paragraph("1. System Architecture", S["h1"]))
story.append(Paragraph("The Reactome LNP Agent v2 follows a three-tier architecture: an Angular single-page application communicates with a FastAPI backend via REST and Server-Sent Events (SSE), which orchestrates a LangGraph workflow leveraging both a local FAISS vector store and remote Amazon Bedrock foundation models. Version 2 introduces a fundamental architectural change: the agent pipeline is now driven by YAML configuration files (src/agents/*.yaml) that define each agent's identity, system prompt, model parameters, and tool access. A Python loader module (src/agents/__init__.py) reads these configs at startup and injects global constraints from the system.yaml master configuration into each agent's prompt.", S["body"]))
story.append(Paragraph("The choice of YAML-driven configuration enables rapid iteration on agent behavior without code changes\u2014modifying a prompt, adjusting temperature, or adding a new agent requires only editing a YAML file. The system.yaml file serves as the master configuration, defining the agent roster, routing rules, and six global constraints that are automatically appended to every agent's system prompt.", S["body"]))
add_img(f"{IMG}/diagram_architecture.png", "Figure 1. System architecture showing the three-tier design: Angular client, FastAPI backend with LangGraph and FAISS, and AWS Bedrock cloud services.")
story.append(PageBreak())


# ============================================================
# 2. AGENT SYSTEM
# ============================================================
story.append(Paragraph("2. Agent System Architecture", S["h1"]))
story.append(Paragraph("Version 2 replaces the previous 3-expert pipeline with a 6-agent supervisor/worker system. Each agent is defined in a dedicated YAML file under src/agents/, specifying its role, system prompt, model parameters, output field, and available tools. The system.yaml master config defines global constraints, the agent roster with positions, and routing rules that map query types to expert subsets.", S["body"]))

story.append(Paragraph("2.1 Agent Roster", S["h2"]))
tbl([
    ["Agent", "Role", "Position", "Output Field"],
    ["Router", "Query classifier (synthesis / lookup / general)", "Node 2", "query_type"],
    ["Reaction Expert", "SMARTS template matching, feasibility assessment", "Parallel worker", "reaction_analysis"],
    ["Lipid Design Expert", "Retrosynthesis + SAR + design rule validation", "Parallel worker", "lipid_design_analysis"],
    ["Generative AI Expert", "De novo generation + RL optimization", "Parallel worker", "generative_analysis"],
    ["Property Prediction Expert", "ML model recommendations + uncertainty quantification", "Parallel worker", "prediction_analysis"],
    ["Literature Scout", "PubMed, PubChem, web search", "Parallel worker", "literature_context"],
    ["Lead Agent", "Supervisor \u2014 critically evaluates all expert outputs", "Supervisor", "final_answer"],
], [1.4*inch, 2.1*inch, 1.1*inch, 1.5*inch])
story.append(Paragraph("<i>Table 2: Agent roster. Five parallel workers feed into the Lead Agent supervisor.</i>", S["cap"]))

story.append(Paragraph("2.2 YAML Configuration", S["h2"]))
story.append(Paragraph("Each agent YAML file follows a consistent schema. The system.yaml master config defines global constraints that are automatically prepended to every agent's system prompt at load time:", S["body"]))

code_block("""# system.yaml (excerpt)
system:
  name: "Reactome LNP Agent"
  version: "3.0"
  default_model: "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

  global_constraints:
    - "Never fabricate SMILES - only use validated structures"
    - "Always cite Mogam reaction template IDs (10001-10017)"
    - "Flag any compound with SA Score > 6 as difficult to synthesize"
    - "Use IUPAC nomenclature for chemical names"
    - "Express uncertainty explicitly"
    - "Distinguish computational predictions from experimental evidence"

  routes:
    synthesis:
      experts: [reaction_expert, lipid_design_expert,
               generative_ai_expert, property_prediction_expert,
               literature_scout]
    lookup:
      experts: [literature_scout]
    general:
      experts: [literature_scout]""", "yaml")

story.append(Paragraph("2.3 Agent Merging Rationale", S["h2"]))
story.append(Paragraph("The v2 agent design consolidates related capabilities into fewer, more capable agents. The Lipid Design Expert merges three previously separate concerns (retrosynthesis planning, structure-activity relationships, and design rule validation) because a senior lipid chemist evaluates route, properties, and constraints simultaneously\u2014they are inseparable aspects of design evaluation. Similarly, the Generative AI Expert merges molecular generation and RL optimization because generation and fine-tuning are two halves of the same pipeline. The Reaction Expert remains standalone because SMARTS pattern matching is a distinct technical skill requiring focused analysis.", S["body"]))

story.append(Paragraph("2.4 Query Routing", S["h2"]))
story.append(Paragraph("The Router agent classifies each query into one of three categories, determining which experts are activated:", S["body"]))
tbl([
    ["Category", "Description", "Experts Activated"],
    ["synthesis", "Design, build, optimize, or generate lipids", "All 5 parallel workers"],
    ["lookup", "Specific fact about a known compound or reaction", "Literature Scout only"],
    ["general", "Broad concepts, comparisons, recent research", "Literature Scout + Web Search"],
], [1*inch, 2.5*inch, 2.6*inch])
story.append(Paragraph("<i>Table 3: Query routing rules. Synthesis queries activate the full expert panel.</i>", S["cap"]))
story.append(PageBreak())


# ============================================================
# 3. LANGGRAPH PIPELINE
# ============================================================
story.append(Paragraph("3. LangGraph Agent Pipeline", S["h1"]))
story.append(Paragraph("The core intelligence is implemented as a LangGraph StateGraph with 10 nodes. The pipeline begins with query rewriting (making questions self-contained using chat history), followed by routing classification, FAISS retrieval with LLM-based reranking, parallel expert execution, and final synthesis by the Lead Agent. For synthesis queries, all five expert workers execute in parallel, reducing latency compared to sequential execution. Lookup and general queries activate only the relevant subset of experts.", S["body"]))
add_img(f"{IMG}/diagram_pipeline.png", "Figure 2. LangGraph pipeline. After retrieval, up to 5 expert workers execute in parallel before converging into the Lead Agent.")

story.append(Paragraph("3.1 State Schema", S["h2"]))
story.append(Paragraph("The shared state carries data between all nodes. Each node reads from and writes to specific fields:", S["body"]))

code_block("""class ReactomeState(TypedDict):
    query: str                  # User's question
    chat_history: str           # Previous conversation turns
    rewritten_query: str        # Self-contained rewrite
    query_type: str             # synthesis | lookup | general
    retrieved_context: str      # Top-4 reranked FAISS chunks
    reaction_analysis: str      # Reaction expert output
    lipid_design_analysis: str  # Lipid design expert output
    generative_analysis: str    # Generative AI expert output
    prediction_analysis: str    # Property prediction expert output
    literature_context: str     # PubMed + PubChem results
    web_context: str            # Web search results
    final_answer: str           # Lead agent's synthesized response
    error: str                  # Error capture""", "python")

story.append(Paragraph("3.2 Node Specifications", S["h2"]))
tbl([
    ["Node", "Input Fields", "Output Field", "LLM Calls"],
    ["rewrite_query", "query, chat_history", "rewritten_query", "0\u20131"],
    ["router", "rewritten_query", "query_type", "1 (fast)"],
    ["retrieve + rerank", "rewritten_query", "retrieved_context", "1 (rerank)"],
    ["reaction_expert", "query, retrieved_context", "reaction_analysis", "1"],
    ["lipid_design_expert", "query, retrieved_context", "lipid_design_analysis", "1"],
    ["generative_ai_expert", "query, retrieved_context", "generative_analysis", "1"],
    ["property_prediction_expert", "query, retrieved_context", "prediction_analysis", "1"],
    ["literature_search", "rewritten_query", "literature_context", "0 (API)"],
    ["web_search", "rewritten_query", "web_context", "0 (API)"],
    ["lead_agent", "all analysis fields", "final_answer", "1"],
], [1.5*inch, 1.5*inch, 1.3*inch, 0.8*inch])
story.append(Paragraph("<i>Table 4: Node specifications. Synthesis queries make up to 8 LLM calls (5 parallel + 3 sequential).</i>", S["cap"]))

story.append(Paragraph("3.3 Retrieval and Reranking", S["h2"]))
story.append(Paragraph("The retrieval node fetches the top-8 candidates from FAISS, then uses an LLM call to rerank them by relevance, selecting the top-4 chunks. This two-stage approach improves precision over raw vector similarity alone, as the LLM can assess semantic relevance that embedding distance may miss. The reranked chunks are concatenated with source type metadata and passed to all expert nodes.", S["body"]))

story.append(Paragraph("3.4 Conditional Routing", S["h2"]))
story.append(Paragraph("After retrieval, a conditional edge dispatches to different expert subsets based on query_type. This avoids unnecessary LLM calls for simple lookups:", S["body"]))
bul("<b>synthesis</b> \u2192 reaction_expert + lipid_design_expert + generative_ai_expert + property_prediction_expert + literature_search (5 parallel)")
bul("<b>lookup</b> \u2192 literature_search only (1 node)")
bul("<b>general</b> \u2192 web_search + literature_search (2 parallel)")
story.append(PageBreak())


# ============================================================
# 4. EXPERT AGENTS
# ============================================================
story.append(Paragraph("4. Expert Agent Details", S["h1"]))

story.append(Paragraph("4.1 Reaction Compatibility Expert", S["h2"]))
story.append(Paragraph("Specializes in SMARTS template matching and reaction feasibility assessment. For each applicable template, it reports the reaction ID, functional group match, compatibility level (HIGH/MEDIUM/LOW), conditions, competing reactions, and known issues. It enforces the critical rule of never using reactions 10012 or 10017 (flagged as invalid).", S["body"]))

story.append(Paragraph("4.2 Lipid Design Expert", S["h2"]))
story.append(Paragraph("Merges retrosynthesis planning, structure-activity relationships, and design rule validation into a single senior chemist perspective. Outputs include synthesis routes with reaction IDs, property profiles (pKa, LogP, MW, TPSA, SA Score), design rule compliance tables (PASS/FAIL per constraint), and comparisons to reference lipids (DLin-MC3-DMA, ALC-0315, SM-102).", S["body"]))

story.append(Paragraph("4.3 Generative AI Expert", S["h2"]))
story.append(Paragraph("Covers de novo molecular generation (REINVENT, JT-VAE, MoLeR, diffusion models) and RL optimization (REINFORCE, PPO, DPO, MCTS). Provides a multi-objective reward function specification for ionizable lipids with hard constraints (valid SMILES, ionizable nitrogen, MW 500\u20131200, synthesizable via Mogam templates) and soft objectives (pKa, SA Score, LogP, liver targeting, novelty, diversity) with specific weights.", S["body"]))

story.append(Paragraph("4.4 Property Prediction Expert", S["h2"]))
story.append(Paragraph("Recommends ML models for molecular property prediction based on data size and property type. Covers molecular representations (SMILES, fingerprints, graphs, 3D), model architectures (GNN, Transformers, RF/XGBoost, Gaussian Process), and transfer learning pipelines. Always requires uncertainty quantification for novel structures.", S["body"]))

story.append(Paragraph("4.5 Literature Scout", S["h2"]))
story.append(Paragraph("Retrieves external evidence from three sources using live API calls:", S["body"]))
tbl([
    ["Source", "API", "Output"],
    ["PubMed", "NCBI E-utilities (esearch + esummary)", "Title, journal, year, PMID"],
    ["PubChem", "PUG REST (compound/name/property)", "IUPAC name, SMILES, MW, formula"],
    ["Web", "DuckDuckGo HTML scraping", "Title, snippet, URL"],
], [1*inch, 2.5*inch, 2.6*inch])
story.append(Paragraph("<i>Table 5: External search tools available to the Literature Scout.</i>", S["cap"]))

story.append(Paragraph("4.6 Lead Reasoning Agent", S["h2"]))
story.append(Paragraph("The supervisor agent receives all expert outputs and produces the final user-facing response. It applies critical evaluation rules: reaction expert overrides design expert on compatibility conflicts, design rule violations are treated as critical rejections, AI recommendations are presented as computational suggestions requiring validation, and confidence levels (HIGH/MEDIUM/LOW) are assigned based on evidence strength.", S["body"]))
story.append(PageBreak())

# ============================================================
# 5. RAG SYSTEM
# ============================================================
story.append(Paragraph("5. RAG System", S["h1"]))
story.append(Paragraph("The Retrieval-Augmented Generation system ingests domain-specific documents from five source types, processes them through a chunking pipeline, and stores the resulting vectors in a FAISS index. At query time, the user's question is embedded using the same Titan model and the top-8 most similar chunks are retrieved, then reranked by the LLM to select the top-4. Each chunk carries metadata (source_type) that helps the LLM understand provenance.", S["body"]))
add_img(f"{IMG}/diagram_rag.png", "Figure 3. RAG data flow: five source types are loaded, chunked, embedded via Titan, and indexed in FAISS.")

story.append(Paragraph("5.1 Data Sources", S["h2"]))
tbl([
    ["Source", "Type", "Size", "Content"],
    ["Research Papers", "PDF", "3 files", "Lipid generation, SyntheMol-RL, MCTS approaches"],
    ["Related Papers", "PDF", "30 files", "LNP design, ML for lipids, diffusion models, transfection"],
    ["LNP Design Rules", "PDF + MD", "2 files", "MCTS tree structure, tail constraints, action space definitions"],
    ["Reaction Templates", "Python", "1 file", "13 Mogam SMARTS-based reaction definitions"],
    ["Liver Scores", "CSV", "293 rows", "SMILES with liver targeting scores"],
    ["Building Blocks", "CSV", "217K rows", "Head group building blocks (summary indexed)"],
], [1.4*inch, 0.8*inch, 1*inch, 3*inch])
story.append(Paragraph("<i>Table 6: Data sources ingested into the RAG system.</i>", S["cap"]))

story.append(Paragraph("5.2 Index Parameters", S["h2"]))
tbl([
    ["Parameter", "Value"],
    ["Text splitter", "RecursiveCharacterTextSplitter"],
    ["Chunk size / overlap", "1,000 / 200 characters"],
    ["Total documents \u2192 chunks", "152 \u2192 454"],
    ["Embedding model", "amazon.titan-embed-text-v2:0 (1,024-dim)"],
    ["Index type", "FAISS Flat L2"],
    ["Initial retrieval k", "8 (reranked to top 4)"],
    ["Persisted index size", "1.8 MB (index.faiss) + 477 KB (index.pkl)"],
], [2.2*inch, 4*inch])
story.append(Paragraph("<i>Table 7: FAISS index configuration. Retrieval now uses 8+rerank strategy.</i>", S["cap"]))
story.append(PageBreak())


# ============================================================
# 6. AWS BEDROCK
# ============================================================
story.append(Paragraph("6. AWS Bedrock Integration", S["h1"]))
story.append(Paragraph("Amazon Bedrock serves as the inference backbone. The application uses two models: Claude Sonnet 4.5 for all reasoning tasks and Titan Embed Text v2 for vector embeddings. Both are accessed through langchain-aws wrappers. Two LLM instances are configured: a standard instance (max_tokens=4096, temperature=0.2) for the Lead Agent and Lipid Design Expert, and a fast instance (max_tokens=1024) for the Router, Reaction Expert, and other workers.", S["body"]))
add_img(f"{IMG}/diagram_bedrock.png", "Figure 4. AWS Bedrock integration showing foundation models and optional managed agents.")

story.append(Paragraph("6.1 Foundation Models", S["h2"]))
tbl([
    ["Model", "Model ID", "Usage"],
    ["Claude Sonnet 4.5", "us.anthropic.claude-sonnet-4-5-20250929-v1:0", "All agent reasoning (router, experts, lead)"],
    ["Titan Embed Text v2", "amazon.titan-embed-text-v2:0", "Document + query embeddings (1024-dim)"],
], [1.5*inch, 2.8*inch, 1.8*inch])
story.append(Paragraph("<i>Table 8: Bedrock foundation models.</i>", S["cap"]))

story.append(Paragraph("6.2 Managed Bedrock Agents", S["h2"]))
story.append(Paragraph("Five domain-specific agents are pre-configured in Bedrock for the multi-agent meeting workflow:", S["body"]))
tbl([
    ["Agent", "ID", "Role"],
    ["MOGAM-Chem-Agent", "0IPX1MMI2D", "Chemical structure and synthesis expert"],
    ["MOGAM-AI-Agent", "KQ9FJVLHQE", "AI/ML methodology and model design"],
    ["MOGAM-LNP-Agent", "Q8GN0FK7NV", "LNP formulation and delivery optimization"],
    ["MOGAM-BI-Agent", "XDPBOQN8YT", "Bioinformatics and data analysis"],
    ["MOGAM-Lead-Agent", "RHUTNOTET1", "Team lead, synthesis of expert inputs"],
], [1.5*inch, 1.2*inch, 3.5*inch])
story.append(Paragraph("<i>Table 9: Managed Bedrock Agents for the MOGAM research team.</i>", S["cap"]))
story.append(PageBreak())

# ============================================================
# 7. BACKEND API
# ============================================================
story.append(Paragraph("7. Backend API", S["h1"]))
story.append(Paragraph("The FastAPI backend exposes seven endpoints. The /api/chat endpoint streams status messages as each pipeline node begins execution, including the new agent names (lipid_design_expert, generative_ai_expert, property_prediction_expert). The details SSE event now includes all six expert output fields.", S["body"]))
add_img(f"{IMG}/diagram_api.png", "Figure 5. FastAPI endpoint structure.")

story.append(Paragraph("7.1 Endpoint Specifications", S["h2"]))
tbl([
    ["Method", "Path", "Description", "Response"],
    ["GET", "/api/health", "Health check", '{"status", "model", "region"}'],
    ["GET", "/api/reactions", "List 13 reaction templates", '{"reactions": [...]}'],
    ["GET", "/api/reactions/{id}/svg", "Reaction SVG diagram", "image/svg+xml"],
    ["POST", "/api/query", "Full agent query (blocking)", "All 6 expert analyses + final answer"],
    ["POST", "/api/chat", "SSE streaming chat", "status \u2192 answer \u2192 details \u2192 [DONE]"],
    ["POST", "/api/chat-with-files", "SSE chat with file uploads", "Same SSE protocol as /api/chat"],
    ["POST", "/api/analyze-smiles", "RDKit molecular analysis", '{"smiles", "scores", "svg"}'],
], [0.6*inch, 1.5*inch, 1.5*inch, 2.5*inch])
story.append(Paragraph("<i>Table 10: API endpoint specifications.</i>", S["cap"]))

story.append(Paragraph("7.2 SSE Stream Protocol (Updated)", S["h2"]))
story.append(Paragraph("The chat endpoint now emits status events for all 10 pipeline nodes and sends 6 expert fields in the details event:", S["body"]))

code_block("""data: {"type":"status","step":"rewrite_query","message":"Understanding..."}
data: {"type":"status","step":"router","message":"Classifying..."}
data: {"type":"status","step":"retrieve","message":"Retrieving..."}
data: {"type":"status","step":"reaction_expert","message":"Analyzing..."}
data: {"type":"status","step":"lipid_design_expert","message":"Evaluating..."}
data: {"type":"status","step":"generative_ai_expert","message":"Assessing..."}
data: {"type":"status","step":"property_prediction_expert","message":"Predicting..."}
data: {"type":"status","step":"literature_search","message":"Searching..."}
data: {"type":"status","step":"lead_agent","message":"Reasoning..."}
data: {"type":"answer","content":"...final answer..."}
data: {"type":"details","reaction_analysis":"...","lipid_design_analysis":"...",
       "generative_analysis":"...","prediction_analysis":"...",
       "literature_context":"...","web_context":"..."}
data: [DONE]""", "sse")

story.append(Paragraph("7.3 Reaction Templates", S["h2"]))
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
], [0.5*inch, 1.7*inch, 2*inch, 1*inch])
story.append(Paragraph("<i>Table 11: All 13 reaction templates with validation status.</i>", S["cap"]))
story.append(PageBreak())


# ============================================================
# 8. FRONTEND
# ============================================================
story.append(Paragraph("8. Frontend Application", S["h1"]))
story.append(Paragraph("The frontend is built with Angular 21 (standalone components) and Tailwind CSS v4. Version 2 updates include: conversation persistence via localStorage (up to 20 conversations), expanded expert detail panels showing all 6 agent outputs, file upload support for PDF/TXT/MD/CSV/DOCX attachments, and a revised workflow visualization reflecting the 10-node pipeline.", S["body"]))
add_img(f"{IMG}/diagram_frontend.png", "Figure 6. Angular component tree with services.")

story.append(Paragraph("8.1 Component Summary", S["h2"]))
tbl([
    ["Component", "Route", "Key Features"],
    ["App (root)", "\u2014", "Shell layout: sidebar + router-outlet"],
    ["Sidebar", "\u2014", "Conversation list with new/delete/select, date grouping (Today, Yesterday, N days ago)"],
    ["Chat", "/", "SSE streaming, file upload (PDF/TXT/MD/CSV/DOCX), 6 expert detail panels, markdown rendering"],
    ["Reactions", "/reactions", "13 reaction cards with warning badges, SVG diagrams via backend API"],
    ["Workflow", "/workflow", "10-step pipeline visualization with parallel execution indicators"],
], [1.1*inch, 0.7*inch, 4.3*inch])
story.append(Paragraph("<i>Table 12: Frontend components.</i>", S["cap"]))

story.append(Paragraph("8.2 Expert Detail Panels", S["h2"]))
story.append(Paragraph("Each assistant response includes an expandable 'Show expert analyses' section with 6 collapsible panels:", S["body"]))
tbl([
    ["Panel", "Source Agent", "Content"],
    ["\u2697\ufe0f Reaction Analysis", "reaction_expert", "SMARTS matches, feasibility, conditions, competing reactions"],
    ["\ud83e\uddec Lipid Design", "lipid_design_expert", "Retrosynthesis routes, SAR insights, design rule compliance table"],
    ["\ud83e\udd16 Generative AI", "generative_ai_expert", "Model recommendations, reward functions, training plans"],
    ["\ud83d\udcca Property Prediction", "property_prediction_expert", "ML models, uncertainty quantification, applicability domain"],
    ["\ud83d\udcda Literature", "literature_scout", "PubMed articles with PMIDs, PubChem compound data"],
    ["\ud83c\udf10 Web Search", "literature_scout", "Web search results with titles, snippets, URLs"],
], [1.3*inch, 1.5*inch, 3.3*inch])
story.append(Paragraph("<i>Table 13: Expert detail panels in the chat interface.</i>", S["cap"]))

story.append(Paragraph("8.3 Conversation Management", S["h2"]))
story.append(Paragraph("The ConversationService provides localStorage-backed conversation persistence. Conversations are auto-titled from the first user message, sorted by recency, and limited to 20 entries. The sidebar displays conversations grouped by date (Today, Yesterday, N days ago). Each conversation stores the full message array including expert details, enabling review of past analyses.", S["body"]))
story.append(PageBreak())

# ============================================================
# 9. STANDALONE & DESKTOP
# ============================================================
story.append(Paragraph("9. Standalone and Desktop Applications", S["h1"]))
story.append(Paragraph("The standalone Dioxus WASM app and wry desktop app remain unchanged from v1. The Dioxus app provides focused molecular property analysis via RDKit, while the desktop app embeds the full Angular build as a native executable.", S["body"]))

story.append(Paragraph("9.1 Deployment Comparison", S["h2"]))
tbl([
    ["Feature", "Angular Web", "Dioxus Standalone", "Desktop (wry)"],
    ["Runtime", "Browser + Node.js", "Browser only", "Native (no browser)"],
    ["Backend Dependency", "Required (port 8000)", "Required (port 8000)", "Required (port 8000)"],
    ["Build Size", "~1 MB (dist/)", "~200 KB (WASM)", "~8 MB (binary)"],
    ["Functionality", "Full (chat + analysis)", "Molecular analysis only", "Full (chat + analysis)"],
    ["Installation", "npm install + ng serve", "trunk build + Python", "Single binary"],
], [1.2*inch, 1.2*inch, 1.2*inch, 2.6*inch])
story.append(Paragraph("<i>Table 14: Deployment comparison.</i>", S["cap"]))
story.append(PageBreak())


# ============================================================
# 10. PROJECT STRUCTURE
# ============================================================
story.append(Paragraph("10. Project Structure and Deployment", S["h1"]))

code_block("""chem-agent/
├── .env                         # AWS Bedrock configuration
├── pyproject.toml               # Python dependencies (uv)
├── run.sh                       # Start both servers
├── data/
│   ├── papers/                  # Research PDFs (3 + 30 files)
│   ├── lnp_data/                # Rules, reactions, CSVs
│   └── faiss_lnp_index/         # Persisted FAISS index
├── src/
│   ├── agents/                  # NEW: YAML agent definitions
│   │   ├── __init__.py          # Agent config loader
│   │   ├── system.yaml          # Master config + global constraints
│   │   ├── router.yaml          # Query classifier
│   │   ├── reaction_expert.yaml # SMARTS template matching
│   │   ├── lipid_design_expert.yaml  # Retrosynthesis + SAR + rules
│   │   ├── generative_ai_expert.yaml # Generation + RL
│   │   ├── property_prediction_expert.yaml # ML prediction + UQ
│   │   ├── literature_scout.yaml    # PubMed/PubChem/web
│   │   └── lead_agent.yaml      # Supervisor agent
│   ├── backend/
│   │   ├── config.py            # .env loader
│   │   ├── rag.py               # FAISS + document ingestion
│   │   ├── tools.py             # PubMed, PubChem, web search
│   │   ├── agent.py             # LangGraph 10-node workflow
│   │   └── main.py              # FastAPI (7 endpoints)
│   └── frontend/reactome-ui/    # Angular 21 project
├── standalone/                  # Dioxus WASM app
├── standalone-desktop/          # wry desktop app
├── notes/                       # Jupyter notebooks
└── docs/                        # Technical documentation""", "tree")

story.append(Paragraph("10.1 Running the Application", S["h2"]))

code_block("""# Backend (port 8000)
.venv/bin/uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (port 4200) — requires Node.js 22+
cd src/frontend/reactome-ui && ng serve --host 0.0.0.0 --port 4200

# Or both at once
./run.sh

# Standalone Dioxus app (port 8001)
cd standalone && trunk build --release && python serve.py

# Desktop app (requires backend on port 8000)
cd standalone-desktop && ./build.sh && ./target/release/lnp-desktop""", "shell")

story.append(Paragraph("10.2 Remote Access via VS Code", S["h2"]))
bul("Forward ports <b>8000</b> and <b>4200</b> in the VS Code Ports panel")
bul("Access frontend at <b>http://localhost:4200</b> in local browser")
bul("Backend Swagger UI available at <b>http://localhost:8000/docs</b>")

# ============================================================
# 11. CHANGELOG
# ============================================================
story.append(Paragraph("11. Changelog: v1 \u2192 v2", S["h1"]))
tbl([
    ["Area", "v1", "v2"],
    ["Agent pipeline", "5-node, 3 experts", "10-node, 6 agents (5 parallel workers + supervisor)"],
    ["Agent config", "Hardcoded prompts in agent.py", "YAML files in src/agents/ with global constraints"],
    ["Query routing", "None (all queries \u2192 full pipeline)", "Router classifies synthesis / lookup / general"],
    ["Query rewriting", "None", "LLM rewrites using chat history for self-contained queries"],
    ["Retrieval", "Top-6 FAISS", "Top-8 FAISS + LLM reranking \u2192 top-4"],
    ["Expert: Design", "Separate design_rules + synthesis_planner", "Merged Lipid Design Expert (retrosynthesis + SAR + rules)"],
    ["Expert: Gen AI", "None", "NEW: Generative AI Expert (generation + RL optimization)"],
    ["Expert: Prediction", "None", "NEW: Property Prediction Expert (ML + uncertainty quantification)"],
    ["External tools", "None", "PubMed, PubChem, web search (live API calls)"],
    ["Lead Agent", "Final answer node", "Supervisor with conflict resolution + confidence levels"],
    ["SSE details", "3 fields", "6 fields (all expert outputs)"],
    ["Frontend details", "3 panels", "6 collapsible expert panels"],
    ["Conversations", "None (ephemeral)", "localStorage persistence, sidebar management"],
    ["File upload", "None", "PDF, TXT, MD, CSV, DOCX support via /api/chat-with-files"],
    ["Workflow viz", "6 steps (3 experts)", "10 steps (5 parallel workers + supervisor)"],
], [1.3*inch, 2*inch, 2.8*inch])
story.append(Paragraph("<i>Table 15: Summary of changes from v1 to v2.</i>", S["cap"]))

doc.build(story)
print(f"Done: {OUT} ({os.path.getsize(OUT) // 1024} KB)")

