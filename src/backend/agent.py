"""LangGraph Reactome agent v3 — 6-agent Supervisor/Worker with YAML prompts."""
from typing import TypedDict
from langchain_aws import ChatBedrock
from langgraph.graph import StateGraph, START, END
from .config import AWS_REGION, BEDROCK_MODEL_ID, BEDROCK_FAST_MODEL_ID
from .rag import retriever
from .tools import search_pubmed, search_pubchem, search_web
from ..agents import get_system_prompt

llm = ChatBedrock(model_id=BEDROCK_MODEL_ID, region_name=AWS_REGION, streaming=True)
llm_fast = ChatBedrock(model_id=BEDROCK_FAST_MODEL_ID or BEDROCK_MODEL_ID, region_name=AWS_REGION,
                       streaming=True, model_kwargs={"max_tokens": 1024})

QUERY_TYPES = ["synthesis", "lookup", "general"]


class ReactomeState(TypedDict):
    query: str
    chat_history: str
    rewritten_query: str
    query_type: str
    retrieved_context: str
    reaction_analysis: str
    lipid_design_analysis: str
    generative_analysis: str
    prediction_analysis: str
    literature_context: str
    web_context: str
    final_answer: str
    error: str


def _safe_llm_call(llm_instance, prompt: str, fallback: str = "") -> str:
    try:
        return llm_instance.invoke(prompt).content
    except Exception as e:
        return fallback or f"[Error: {type(e).__name__}: {str(e)[:200]}]"


def _prompt(agent_id: str) -> str:
    """Load system prompt from YAML with global constraints."""
    try:
        return get_system_prompt(agent_id)
    except Exception:
        return ""


# ── Node 1: Rewrite query ──
def rewrite_query_node(state: ReactomeState) -> dict:
    history = state.get("chat_history", "")
    query = state["query"]
    if not history.strip():
        return {"rewritten_query": query}
    prompt = f"""Rewrite this question to be self-contained for a chemistry database search. Output ONLY the rewritten query.

History:
{history[-2000:]}

Question: {query}

Rewritten:"""
    rewritten = _safe_llm_call(llm_fast, prompt, fallback=query).strip()
    return {"rewritten_query": rewritten if len(rewritten) > 5 else query}


# ── Node 2: Router ──
def router_node(state: ReactomeState) -> dict:
    query = state.get("rewritten_query") or state["query"]
    prompt = f"""{_prompt('router')}

Question: {query}

Category:"""
    result = _safe_llm_call(llm_fast, prompt, fallback="synthesis").strip().lower()
    for qt in QUERY_TYPES:
        if qt in result:
            return {"query_type": qt}
    return {"query_type": "synthesis"}


# ── Node 3: Retrieve + rerank ──
def retrieval_node(state: ReactomeState) -> dict:
    q = state.get("rewritten_query") or state["query"]
    try:
        docs = retriever.invoke(q)
    except Exception as e:
        return {"retrieved_context": f"[Retrieval failed: {e}]"}
    if not docs:
        return {"retrieved_context": "[No documents found]"}

    candidates = docs[:8]
    summaries = "\n".join(f"[{i}] {d.page_content[:300]}" for i, d in enumerate(candidates))
    ranked = _safe_llm_call(llm_fast, f"Return comma-separated doc indices by relevance (max 4).\n\nQuery: {q}\n\nDocs:\n{summaries}\n\nIndices:", fallback="")
    try:
        idx = [int(x.strip()) for x in ranked.split(",") if x.strip().isdigit()]
        idx = [i for i in idx if 0 <= i < len(candidates)][:4]
    except Exception:
        idx = []
    if len(idx) < 2:
        idx = list(range(min(4, len(candidates))))
    ctx = "\n\n---\n\n".join(f"[{d.metadata.get('source_type', '')}] {d.page_content}" for d in [candidates[i] for i in idx])
    return {"retrieved_context": ctx}


# ── Conditional routing ──
def route_after_retrieval(state: ReactomeState) -> list[str]:
    qt = state.get("query_type", "synthesis")
    if qt == "synthesis":
        return ["reaction_expert", "lipid_design_expert", "generative_ai_expert", "property_prediction_expert", "literature_search"]
    elif qt == "lookup":
        return ["literature_search"]
    else:
        return ["web_search", "literature_search"]


# ── Expert Workers (parallel, independent) ──

def reaction_expert_node(state: ReactomeState) -> dict:
    prompt = f"""{_prompt('reaction_expert')}

Context:
{state['retrieved_context']}

Question: {state['query']}

Analysis:"""
    return {"reaction_analysis": _safe_llm_call(llm_fast, prompt)}


def lipid_design_expert_node(state: ReactomeState) -> dict:
    prompt = f"""{_prompt('lipid_design_expert')}

Context:
{state['retrieved_context']}

Question: {state['query']}

Analysis:"""
    return {"lipid_design_analysis": _safe_llm_call(llm, prompt)}


def generative_ai_expert_node(state: ReactomeState) -> dict:
    prompt = f"""{_prompt('generative_ai_expert')}

Context:
{state['retrieved_context']}

Question: {state['query']}

Analysis:"""
    return {"generative_analysis": _safe_llm_call(llm_fast, prompt)}


def property_prediction_expert_node(state: ReactomeState) -> dict:
    prompt = f"""{_prompt('property_prediction_expert')}

Context:
{state['retrieved_context']}

Question: {state['query']}

Analysis:"""
    return {"prediction_analysis": _safe_llm_call(llm_fast, prompt)}


def literature_search_node(state: ReactomeState) -> dict:
    q = state.get("rewritten_query") or state["query"]
    parts = []
    try:
        parts.append(f"## PubMed\n{search_pubmed(q, max_results=3)}")
    except Exception as e:
        parts.append(f"## PubMed\n[Failed: {e}]")
    try:
        parts.append(f"## PubChem\n{search_pubchem(q, max_results=3)}")
    except Exception as e:
        parts.append(f"## PubChem\n[Failed: {e}]")
    return {"literature_context": "\n\n".join(parts)}


def web_search_node(state: ReactomeState) -> dict:
    q = state.get("rewritten_query") or state["query"]
    try:
        return {"web_context": search_web(f"{q} lipid nanoparticle", max_results=5)}
    except Exception as e:
        return {"web_context": f"[Web search failed: {e}]"}


# ── Lead Agent (Supervisor) ──

def lead_agent_node(state: ReactomeState) -> dict:
    qt = state.get("query_type", "synthesis")
    history = f"\nChat history:\n{state['chat_history'][-2000:]}\n" if state.get("chat_history", "").strip() else ""

    evidence = []
    for label, key in [
        ("Reaction Compatibility Analysis", "reaction_analysis"),
        ("Lipid Design Analysis (Retrosynthesis + SAR + Rules)", "lipid_design_analysis"),
        ("Generative AI Recommendations", "generative_analysis"),
        ("Property Prediction Recommendations", "prediction_analysis"),
        ("External Literature (PubMed/PubChem)", "literature_context"),
        ("Web Search Results", "web_context"),
    ]:
        val = state.get(key, "")
        if val and val.strip():
            evidence.append(f"### {label}\n{val}")

    evidence_text = "\n\n".join(evidence) if evidence else "No expert evidence available."

    prompt = f"""{_prompt('lead_agent')}
{history}
**Query type:** {qt}
**User question:** {state['query']}

## Expert Evidence
{evidence_text}

Your response:"""
    return {"final_answer": _safe_llm_call(llm, prompt)}


# ── Graph ──

def build_graph():
    wf = StateGraph(ReactomeState)

    wf.add_node("rewrite_query", rewrite_query_node)
    wf.add_node("router", router_node)
    wf.add_node("retrieve", retrieval_node)
    wf.add_node("reaction_expert", reaction_expert_node)
    wf.add_node("lipid_design_expert", lipid_design_expert_node)
    wf.add_node("generative_ai_expert", generative_ai_expert_node)
    wf.add_node("property_prediction_expert", property_prediction_expert_node)
    wf.add_node("literature_search", literature_search_node)
    wf.add_node("web_search", web_search_node)
    wf.add_node("lead_agent", lead_agent_node)

    wf.add_edge(START, "rewrite_query")
    wf.add_edge("rewrite_query", "router")
    wf.add_edge("router", "retrieve")

    wf.add_conditional_edges("retrieve", route_after_retrieval,
                             ["reaction_expert", "lipid_design_expert", "generative_ai_expert",
                              "property_prediction_expert", "literature_search", "web_search"])

    for node in ["reaction_expert", "lipid_design_expert", "generative_ai_expert",
                 "property_prediction_expert", "literature_search", "web_search"]:
        wf.add_edge(node, "lead_agent")

    wf.add_edge("lead_agent", END)
    return wf.compile()


graph = build_graph()


def run_agent(query: str, chat_history: str = "") -> dict:
    return graph.invoke({
        "query": query, "chat_history": chat_history, "rewritten_query": "",
        "query_type": "", "retrieved_context": "",
        "reaction_analysis": "", "lipid_design_analysis": "",
        "generative_analysis": "", "prediction_analysis": "",
        "literature_context": "", "web_context": "",
        "final_answer": "", "error": "",
    })
