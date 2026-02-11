"""Generate agent_architecture_report.pdf — Multi-Agent Architecture Analysis."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, PageBreak)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

OUT = "docs/agent_architecture_report.pdf"

doc = SimpleDocTemplate(OUT, pagesize=A4,
    topMargin=0.7*inch, bottomMargin=0.7*inch,
    leftMargin=0.8*inch, rightMargin=0.8*inch)

styles = getSampleStyleSheet()
W = A4[0] - 1.6*inch

# ── Color palette ──
EMERALD = HexColor("#059669")
CYAN = HexColor("#0891b2")
SLATE_800 = HexColor("#1e293b")
SLATE_600 = HexColor("#475569")
SLATE_400 = HexColor("#94a3b8")
SLATE_100 = HexColor("#f1f5f9")
PURPLE = HexColor("#7c3aed")
AMBER = HexColor("#d97706")
RED = HexColor("#dc2626")
GREEN_BG = HexColor("#ecfdf5")
RED_BG = HexColor("#fef2f2")
AMBER_BG = HexColor("#fffbeb")
PURPLE_BG = HexColor("#f5f3ff")

# ── Styles ──
S = {}
S["title"] = ParagraphStyle("T", parent=styles["Title"], fontSize=24, textColor=SLATE_800,
    spaceAfter=2, fontName="Helvetica-Bold", alignment=TA_CENTER)
S["subtitle"] = ParagraphStyle("St", parent=styles["Normal"], fontSize=13, textColor=SLATE_600,
    alignment=TA_CENTER, spaceAfter=6)
S["meta"] = ParagraphStyle("Mt", parent=styles["Normal"], fontSize=10, textColor=SLATE_400,
    alignment=TA_CENTER, spaceAfter=4)
S["h1"] = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=16, textColor=SLATE_800,
    spaceBefore=22, spaceAfter=10, fontName="Helvetica-Bold",
    borderWidth=0, borderPadding=0, borderColor=None)
S["h2"] = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, textColor=SLATE_800,
    spaceBefore=14, spaceAfter=8, fontName="Helvetica-Bold")
S["h3"] = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11, textColor=SLATE_600,
    spaceBefore=10, spaceAfter=6, fontName="Helvetica-Bold")
S["body"] = ParagraphStyle("Bd", parent=styles["Normal"], fontSize=10, textColor=HexColor("#222"),
    spaceAfter=8, leading=14, alignment=TA_JUSTIFY)
S["bul"] = ParagraphStyle("Bl", parent=styles["Normal"], fontSize=10, textColor=HexColor("#222"),
    leftIndent=18, bulletIndent=8, spaceAfter=3, leading=13)
S["bul2"] = ParagraphStyle("Bl2", parent=styles["Normal"], fontSize=9.5, textColor=SLATE_600,
    leftIndent=36, bulletIndent=26, spaceAfter=2, leading=12)
S["th"] = ParagraphStyle("Th", fontName="Helvetica-Bold", fontSize=9, leading=11,
    textColor=white, alignment=TA_LEFT)
S["td"] = ParagraphStyle("Td", fontName="Helvetica", fontSize=9, leading=11,
    textColor=HexColor("#222"), alignment=TA_LEFT)
S["td_mono"] = ParagraphStyle("Tdm", fontName="Courier", fontSize=8.5, leading=11,
    textColor=SLATE_600, alignment=TA_LEFT)
S["callout"] = ParagraphStyle("Co", parent=styles["Normal"], fontSize=10, textColor=EMERALD,
    spaceAfter=8, leading=14, fontName="Helvetica-BoldOblique")
S["footer"] = ParagraphStyle("Ft", parent=styles["Normal"], fontSize=8, textColor=SLATE_400,
    alignment=TA_CENTER)

story = []


def heading_bar(text, level=1):
    """Add a colored bar before section headings."""
    if level == 1:
        story.append(Spacer(1, 6))
        bar = Table([[""]], colWidths=[W], rowHeights=[3])
        bar.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), EMERALD),
                                  ("LINEBELOW", (0,0), (-1,-1), 0, white)]))
        story.append(bar)
        story.append(Spacer(1, 4))
        story.append(Paragraph(text, S["h1"]))
    elif level == 2:
        story.append(Paragraph(text, S["h2"]))
    else:
        story.append(Paragraph(text, S["h3"]))


def make_table(headers, rows, col_widths=None):
    """Create a styled table."""
    header_cells = [Paragraph(h, S["th"]) for h in headers]
    data = [header_cells]
    for row in rows:
        data.append([Paragraph(str(c), S["td"]) for c in row])
    if col_widths is None:
        col_widths = [W / len(headers)] * len(headers)
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), SLATE_800),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, SLATE_100]),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
    ]
    t.setStyle(TableStyle(style))
    story.append(t)
    story.append(Spacer(1, 12))


def callout_box(text, bg=GREEN_BG, border=EMERALD):
    """Colored callout box."""
    p = Paragraph(text, S["body"])
    t = Table([[p]], colWidths=[W - 16])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("BOX", (0,0), (-1,-1), 1.5, border),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))


# ============================================================================
# TITLE PAGE
# ============================================================================
story.append(Spacer(1, 80))

# Title bar
title_bar = Table([[""]], colWidths=[W], rowHeights=[4])
title_bar.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), EMERALD)]))
story.append(title_bar)
story.append(Spacer(1, 16))

story.append(Paragraph("Multi-Agent Architecture Analysis", S["title"]))
story.append(Paragraph("Reactome LNP Agent — Model Strategy &amp; Industry Comparison", S["subtitle"]))
story.append(Spacer(1, 12))

title_bar2 = Table([[""]], colWidths=[W], rowHeights=[2])
title_bar2.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), CYAN)]))
story.append(title_bar2)
story.append(Spacer(1, 20))

story.append(Paragraph("Reactome LNP Agent v3.0", S["meta"]))
story.append(Paragraph("February 2026", S["meta"]))
story.append(Paragraph("LangGraph · AWS Bedrock · Claude Sonnet 4.5", S["meta"]))

story.append(Spacer(1, 40))

# Abstract box
abstract = (
    "This report analyzes the multi-agent architecture of the Reactome LNP Agent system, "
    "a 7-agent LangGraph pipeline for ionizable lipid design. It documents the current "
    "single-model configuration (Claude Sonnet 4.5 for all agents), compares it against "
    "industry-standard mixed-model approaches, and provides actionable recommendations "
    "for cost optimization, latency reduction, and architectural resilience."
)
callout_box(abstract)

story.append(PageBreak())


# ============================================================================
# SECTION 1: CURRENT ARCHITECTURE
# ============================================================================
heading_bar("1. Current Agent Architecture")

story.append(Paragraph(
    "The Reactome LNP Agent uses a <b>10-node LangGraph StateGraph</b> with 7 YAML-configured agents. "
    "All agents are powered by <b>Claude Sonnet 4.5</b> (<font face='Courier' size='9'>"
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0</font>) via AWS Bedrock in <b>us-west-2</b>.",
    S["body"]))

heading_bar("1.1 Pipeline Flow", 2)

story.append(Paragraph(
    "The pipeline executes as a directed acyclic graph (DAG) with conditional branching based on query type:",
    S["body"]))

flow_data = [
    ["1", "Query Rewrite", "Rewrites question using chat history", "llm_fast", "0.0"],
    ["2", "Router", "Classifies → synthesis / lookup / general", "llm_fast", "0.0"],
    ["3", "FAISS Retrieval + Rerank", "454 vectors searched, LLM-based reranking", "llm_fast", "0.0"],
    ["4-8", "5 Expert Workers (parallel)", "Domain-specific analysis", "llm", "0.1-0.2"],
    ["9", "Lead Agent", "Supervisor — conflict resolution, final answer", "llm", "0.2"],
]
make_table(["Node", "Agent", "Role", "LLM Instance", "Temp"],
           flow_data, [0.06*W, 0.22*W, 0.38*W, 0.17*W, 0.07*W])

heading_bar("1.2 Agent Configuration Summary", 2)

agent_data = [
    ["Router", "Query classifier", "64", "0.0", "Always", "Infrastructure"],
    ["Reaction Expert", "SMARTS template matching, feasibility", "1,024", "0.1", "Synthesis", "Chemistry"],
    ["Lipid Design Expert", "Retrosynthesis + SAR + design rules", "2,048", "0.15", "Synthesis", "Chemistry"],
    ["Generative AI Expert", "De novo generation + RL optimization", "1,536", "0.2", "Synthesis", "AI/ML"],
    ["Property Prediction", "ML models + uncertainty quantification", "1,536", "0.1", "Synthesis", "AI/ML"],
    ["Literature Scout", "PubMed, PubChem, web search", "512", "0.0", "All paths", "Search"],
    ["Lead Agent", "Supervisor — final answer authority", "4,096", "0.2", "Always", "Infrastructure"],
]
make_table(["Agent", "Role", "Max Tokens", "Temp", "Trigger", "Type"],
           agent_data, [0.14*W, 0.30*W, 0.10*W, 0.06*W, 0.12*W, 0.12*W])

heading_bar("1.3 Model Configuration", 2)

story.append(Paragraph(
    "Two LLM instances are created in <font face='Courier' size='9'>agent.py</font>, "
    "both pointing to the same Sonnet 4.5 model:",
    S["body"]))

story.append(Paragraph("• <b>llm</b> — Default instance for expert workers and lead agent", S["bul"]))
story.append(Paragraph("• <b>llm_fast</b> — Same model, capped at 1,024 tokens for router, rewrite, and reranking", S["bul"]))

callout_box(
    "<b>Key observation:</b> Every node in the pipeline hits the same Claude Sonnet 4.5 endpoint. "
    "The only variation is <font face='Courier' size='9'>max_tokens</font> and "
    "<font face='Courier' size='9'>temperature</font> per agent.",
    AMBER_BG, AMBER)

story.append(PageBreak())


# ============================================================================
# SECTION 2: INDUSTRY STANDARD APPROACHES
# ============================================================================
heading_bar("2. Industry Standard: Multi-Model Architectures")

story.append(Paragraph(
    "Production multi-agent systems in pharma, biotech, and AI research typically employ "
    "<b>tiered model assignment</b> — matching model capability to task complexity. "
    "This section surveys common patterns and their rationale.",
    S["body"]))

heading_bar("2.1 Tiered Model Assignment", 2)

story.append(Paragraph(
    "The industry consensus is to use the <b>cheapest model that meets quality requirements</b> "
    "for each agent role:",
    S["body"]))

tier_data = [
    ["Router / Classifier", "Small/fast (Haiku, GPT-4o-mini)", "Speed critical. 10-50ms matters. Simple classification."],
    ["Domain Experts", "Strong reasoning (Sonnet, GPT-4o)", "Needs domain knowledge + structured output."],
    ["Supervisor / Lead", "Strongest available (Opus, o1, Sonnet)", "Critical thinking, conflict resolution."],
    ["Retrieval Reranker", "Embedding model or small LLM", "Just scoring relevance — no generation needed."],
    ["Code / SMILES Gen", "Code-specialized (Codex, DeepSeek)", "Better at structured pattern generation."],
]
make_table(["Agent Type", "Typical Model", "Rationale"],
           tier_data, [0.20*W, 0.30*W, 0.42*W])

heading_bar("2.2 Mixed-Provider Architectures", 2)

story.append(Paragraph(
    "Some organizations go further and mix providers to optimize for different strengths:",
    S["body"]))

mixed_data = [
    ["Anthropic (Claude)", "Complex reasoning, safety-critical analysis, long context"],
    ["OpenAI (GPT-4o)", "Code generation, function calling, structured output"],
    ["Google (Gemini)", "Multimodal analysis, very long context (1M+ tokens)"],
    ["Open-source (Llama, Mistral)", "Cost-sensitive tasks, on-premise requirements, fine-tuning"],
    ["Specialized (ChemBERTa, MoLFormer)", "Domain-specific tasks (SMILES validation, property prediction)"],
]
make_table(["Provider", "Typical Use Case"],
           mixed_data, [0.30*W, 0.62*W])

heading_bar("2.3 Real-World Examples", 2)

story.append(Paragraph("<b>Pharmaceutical AI platforms</b> (e.g., Insilico Medicine, Recursion):", S["body"]))
story.append(Paragraph("• Use specialized chemistry models for molecular generation", S["bul"]))
story.append(Paragraph("• General-purpose LLMs only for natural language interface and report generation", S["bul"]))
story.append(Paragraph("• GNN/Transformer ensembles for property prediction (not LLM-based)", S["bul"]))

story.append(Spacer(1, 6))
story.append(Paragraph("<b>Enterprise AI agent frameworks</b> (e.g., LangChain, CrewAI, AutoGen):", S["body"]))
story.append(Paragraph("• Default recommendation: use smaller models for routing and tool selection", S["bul"]))
story.append(Paragraph("• Reserve large models for synthesis and final output generation", S["bul"]))
story.append(Paragraph("• Support model-per-agent configuration as a first-class feature", S["bul"]))

story.append(PageBreak())


# ============================================================================
# SECTION 3: PROS AND CONS
# ============================================================================
heading_bar("3. Comparative Analysis: Single-Model vs. Mixed-Model")

heading_bar("3.1 Current Approach — Single Model (Sonnet 4.5 Everywhere)", 2)

# Pros
heading_bar("Advantages", 3)
pros = [
    ("<b>Operational simplicity</b> — One API key, one provider, one billing stream. "
     "No cross-provider auth or version management."),
    ("<b>Consistent output style</b> — All agents produce similarly structured responses. "
     "The lead agent doesn't need to reconcile different formatting conventions."),
    ("<b>Simplified debugging</b> — Same model behavior everywhere. When output is wrong, "
     "the issue is always in the prompt, not model-specific quirks."),
    ("<b>Quality floor</b> — Sonnet 4.5 is genuinely capable enough for all tasks in this pipeline. "
     "No risk of a weak model degrading the chain."),
    ("<b>Prompt portability</b> — YAML prompts work identically across all nodes. "
     "No per-model prompt engineering required."),
]
for p in pros:
    story.append(Paragraph(f"✅ {p}", S["bul"]))

story.append(Spacer(1, 8))

# Cons
heading_bar("Disadvantages", 3)
cons = [
    ("<b>Cost inefficiency</b> — The router uses 64 output tokens for a 3-class classification. "
     "Haiku could do this at ~10× lower cost with equivalent accuracy."),
    ("<b>Latency overhead</b> — 5 parallel Sonnet calls have higher cold-start and TTFT than "
     "5 parallel Haiku calls for simple tasks."),
    ("<b>Single point of failure</b> — If Bedrock throttles Sonnet 4.5 (rate limits, outage), "
     "the entire pipeline stops. No fallback path."),
    ("<b>No specialization</b> — A chemistry-fine-tuned model (e.g., ChemBERTa for SMILES validation) "
     "could outperform a general-purpose LLM on specific subtasks."),
    ("<b>Wasted capacity</b> — The reranker node just picks 4 indices from 8 candidates. "
     "This doesn't need a 200B+ parameter model."),
]
for c in cons:
    story.append(Paragraph(f"❌ {c}", S["bul"]))

story.append(Spacer(1, 12))

heading_bar("3.2 Mixed-Model Approach (Industry Standard)", 2)

heading_bar("Advantages", 3)
mixed_pros = [
    ("<b>40-70% cost reduction</b> — Router + reranker on cheap models saves significantly. "
     "At scale (1000s of queries/day), this is substantial."),
    ("<b>Lower latency</b> — Router classification: ~100ms on Haiku vs ~500ms on Sonnet. "
     "This compounds across the pipeline."),
    ("<b>Provider redundancy</b> — If one provider has an outage, others still function. "
     "Critical for production SLA requirements."),
    ("<b>Task-optimized models</b> — Chemistry-tuned models for SMILES, code models for "
     "SMARTS patterns, embedding models for reranking."),
    ("<b>Scalability</b> — Different rate limits per model means higher aggregate throughput."),
]
for p in mixed_pros:
    story.append(Paragraph(f"✅ {p}", S["bul"]))

story.append(Spacer(1, 8))

heading_bar("Disadvantages", 3)
mixed_cons = [
    ("<b>Operational complexity</b> — Multiple API keys, rate limits, billing streams, "
     "and version pinning across providers."),
    ("<b>Output inconsistency</b> — Different models structure responses differently. "
     "The lead agent must handle varied formatting and reasoning styles."),
    ("<b>Harder debugging</b> — 'Which model caused this bad output?' becomes a real question "
     "when 3+ models are in the pipeline."),
    ("<b>Per-model prompt engineering</b> — What works on Claude may fail on GPT-4o. "
     "Each model needs its own prompt tuning and testing."),
    ("<b>Integration testing burden</b> — Model updates from different providers happen "
     "independently, requiring continuous regression testing."),
]
for c in mixed_cons:
    story.append(Paragraph(f"❌ {c}", S["bul"]))

story.append(PageBreak())


# ============================================================================
# SECTION 4: SIDE-BY-SIDE COMPARISON TABLE
# ============================================================================
heading_bar("4. Side-by-Side Comparison")

comp_data = [
    ["Cost (per 1K queries)", "$$$$", "$$", "Mixed model uses Haiku for 3 high-frequency nodes"],
    ["Avg. Latency", "~3-5s", "~2-3s", "Router + reranker 3-5× faster on small models"],
    ["Debugging", "Simple", "Complex", "Single model = one behavior to understand"],
    ["Prompt Management", "1 set", "N sets", "Each model may need different prompts"],
    ["Provider Resilience", "Low", "High", "Mixed model survives single-provider outage"],
    ["Output Consistency", "High", "Medium", "Same model = same style across agents"],
    ["Quality Floor", "High", "Variable", "Weak model in chain can degrade output"],
    ["Specialization", "None", "High", "Can use domain-specific models"],
    ["Ops Complexity", "Low", "High", "More providers = more moving parts"],
    ["Scalability", "Limited", "High", "Different rate limits = higher throughput"],
]
make_table(["Dimension", "Single Model", "Mixed Model", "Notes"],
           comp_data, [0.18*W, 0.12*W, 0.12*W, 0.50*W])


# ============================================================================
# SECTION 5: RECOMMENDATION
# ============================================================================
heading_bar("5. Recommendation")

story.append(Paragraph(
    "A <b>pragmatic middle ground</b> that stays within AWS Bedrock (no new providers) "
    "while optimizing cost and latency on high-frequency nodes:",
    S["body"]))

rec_data = [
    ["Router / Rewrite / Reranker", "Claude Haiku 3.5", "Fast, cheap, sufficient for classification and ranking"],
    ["5 Expert Workers", "Claude Sonnet 4.5 (keep)", "Strong reasoning needed for domain analysis"],
    ["Lead Agent", "Claude Sonnet 4.5 (keep)", "Best reasoning for conflict resolution and synthesis"],
]
make_table(["Agent Group", "Recommended Model", "Rationale"],
           rec_data, [0.25*W, 0.22*W, 0.45*W])

heading_bar("5.1 Expected Impact", 2)

impact_data = [
    ["Router node cost", "~80% reduction", "64 tokens on Haiku vs Sonnet"],
    ["Rewrite node cost", "~80% reduction", "Simple paraphrasing task"],
    ["Reranker node cost", "~80% reduction", "Index selection, not generation"],
    ["Pipeline latency", "~20-30% reduction", "3 fast nodes on Haiku"],
    ["Quality impact", "Negligible", "Classification accuracy equivalent on Haiku"],
    ["Implementation effort", "~2 hours", "Add model_id to YAML, update agent.py loader"],
]
make_table(["Metric", "Change", "Notes"],
           impact_data, [0.22*W, 0.18*W, 0.52*W])

story.append(Spacer(1, 12))

callout_box(
    "<b>Implementation:</b> Add a <font face='Courier' size='9'>model_id</font> field to each agent YAML. "
    "Update <font face='Courier' size='9'>agent.py</font> to read per-agent model IDs and instantiate "
    "separate <font face='Courier' size='9'>ChatBedrock</font> clients. The router alone fires on every "
    "query — making it Haiku saves ~80% on that node with zero quality loss for a 3-class classification.",
    GREEN_BG, EMERALD)

heading_bar("5.2 Future Considerations", 2)

story.append(Paragraph("• <b>Phase 2:</b> Add fallback model chains (Sonnet → Haiku) for resilience during throttling", S["bul"]))
story.append(Paragraph("• <b>Phase 3:</b> Evaluate chemistry-specific models (ChemBERTa, MoLFormer) for SMILES validation", S["bul"]))
story.append(Paragraph("• <b>Phase 4:</b> Consider Bedrock Guardrails for automated output validation across all agents", S["bul"]))
story.append(Paragraph("• <b>Phase 5:</b> Benchmark Haiku vs Sonnet on router accuracy with production query logs", S["bul"]))

story.append(Spacer(1, 30))

# Footer
footer_bar = Table([[""]], colWidths=[W], rowHeights=[2])
footer_bar.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), SLATE_400)]))
story.append(footer_bar)
story.append(Spacer(1, 8))
story.append(Paragraph("Reactome LNP Agent — Multi-Agent Architecture Report — February 2026", S["footer"]))
story.append(Paragraph("Generated with ReportLab · AWS Bedrock · LangGraph", S["footer"]))


# ============================================================================
# BUILD
# ============================================================================
doc.build(story)
print(f"✅ Generated: {OUT}")
