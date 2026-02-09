"""LangGraph Reactome agent for ionizable lipid design."""
from typing import TypedDict
from langchain_aws import ChatBedrock
from langgraph.graph import StateGraph, START, END
from .config import AWS_REGION, BEDROCK_MODEL_ID
from .rag import retriever

llm = ChatBedrock(model_id=BEDROCK_MODEL_ID, region_name=AWS_REGION, streaming=True)


class ReactomeState(TypedDict):
    query: str
    retrieved_context: str
    reaction_analysis: str
    design_rules_check: str
    synthesis_plan: str
    final_answer: str


def retrieval_node(state: ReactomeState) -> dict:
    docs = retriever.invoke(state["query"])
    ctx = "\n\n---\n\n".join(f"[{d.metadata.get('source_type','')}] {d.page_content}" for d in docs)
    return {"retrieved_context": ctx}


def reaction_expert_node(state: ReactomeState) -> dict:
    prompt = f"""You are an expert in ionizable lipid synthesis reactions.
"Mogam reaction templates" refers to our custom set of 13 SMARTS-based reaction templates for ionizable lipid synthesis (IDs 10001-10017).

Context:
{state['retrieved_context']}

Question: {state['query']}

Analyze applicable Mogam reaction templates (SMARTS). For each:
1. Reaction ID and type
2. Reactant requirements
3. Expected product
4. Known issues
5. Recommended conditions"""
    return {"reaction_analysis": llm.invoke(prompt).content}


def design_rules_node(state: ReactomeState) -> dict:
    prompt = f"""You are an expert in ionizable lipid design rules for LNP formulations.
Context:
{state['retrieved_context']}

Question: {state['query']}

Evaluate against LNP design constraints:
1. Tail configuration (2-4 tails, max 2 distinct, symmetry preferred)
2. MCTS tree structure compatibility
3. Head-tail compatibility
4. Synthesizability
5. Rule violations or warnings"""
    return {"design_rules_check": llm.invoke(prompt).content}


def synthesis_planner_node(state: ReactomeState) -> dict:
    prompt = f"""You are a synthesis planning expert for ionizable lipids.
"Mogam reaction templates" refers to our custom set of 13 SMARTS-based reaction templates (IDs 10001-10017).

Reaction Analysis:
{state['reaction_analysis']}

Design Rules Check:
{state['design_rules_check']}

Question: {state['query']}

Provide:
1. Step-by-step synthesis route with Mogam reaction IDs
2. Building block selection criteria
3. Expected intermediates and final products
4. MCTS-compatible action sequence
5. Optimization points"""
    return {"synthesis_plan": llm.invoke(prompt).content}


def final_answer_node(state: ReactomeState) -> dict:
    prompt = f"""Synthesize these expert analyses into a clear answer.

Question: {state['query']}

Reaction Analysis:
{state['reaction_analysis']}

Design Rules Check:
{state['design_rules_check']}

Synthesis Plan:
{state['synthesis_plan']}

Provide:
1. Direct answer
2. Recommended reaction templates with IDs
3. Design rule compliance
4. Actionable synthesis route
5. Caveats and next steps"""
    return {"final_answer": llm.invoke(prompt).content}


def build_graph():
    wf = StateGraph(ReactomeState)
    wf.add_node("retrieve", retrieval_node)
    wf.add_node("reaction_expert", reaction_expert_node)
    wf.add_node("design_rules", design_rules_node)
    wf.add_node("synthesis_planner", synthesis_planner_node)
    wf.add_node("final_answer", final_answer_node)

    wf.add_edge(START, "retrieve")
    wf.add_edge("retrieve", "reaction_expert")
    wf.add_edge("retrieve", "design_rules")
    wf.add_edge("reaction_expert", "synthesis_planner")
    wf.add_edge("design_rules", "synthesis_planner")
    wf.add_edge("synthesis_planner", "final_answer")
    wf.add_edge("final_answer", END)
    return wf.compile()


graph = build_graph()


def run_agent(query: str) -> dict:
    return graph.invoke({
        "query": query,
        "retrieved_context": "",
        "reaction_analysis": "",
        "design_rules_check": "",
        "synthesis_plan": "",
        "final_answer": "",
    })
