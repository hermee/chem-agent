"""Generate reactome_lnp_agent_workflow_v3.pdf — Dual-model architecture with Graphviz.
Icons rendered as text labels (no emoji) to avoid font rendering issues in Graphviz PDF output."""
import graphviz
import os

g = graphviz.Digraph(
    'ReactomeLNPAgentV3',
    format='pdf',
    engine='dot',
    graph_attr={
        'rankdir': 'TB', 'bgcolor': '#FAFAFA', 'fontname': 'Helvetica',
        'pad': '0.5', 'nodesep': '0.6', 'ranksep': '0.9',
        'label': 'Reactome LNP Agent v3 — Dual-Model Pipeline\nClaude Haiku 3.5 (fast) + Claude Sonnet 4.5 (reasoning) | LangGraph + FAISS + AWS Bedrock',
        'labelloc': 't', 'fontsize': '18', 'fontcolor': '#1a1a2e',
    },
    node_attr={'fontname': 'Helvetica', 'fontsize': '11', 'style': 'filled', 'penwidth': '1.5'},
    edge_attr={'fontname': 'Helvetica', 'fontsize': '9', 'color': '#555555', 'arrowsize': '0.8'},
)

# --- User Input ---
with g.subgraph(name='cluster_input') as c:
    c.attr(label='User Input', style='rounded,dashed', color='#888888', fontcolor='#555555', fontsize='12')
    c.node('start', 'START', shape='circle', fillcolor='#2ecc71', fontcolor='white', width='0.9', fixedsize='true')
    c.node('query', 'User Query\n"Design a 3-tail ionizable\nlipid with amine heads..."',
           shape='note', fillcolor='#fff9c4', color='#f9a825', fontcolor='#333333')

# --- Fast Nodes (Haiku 3.5) ---
with g.subgraph(name='cluster_fast') as c:
    c.attr(label='Infrastructure Nodes (Claude 3.5 Haiku — fast, low cost)',
           style='rounded,filled', color='#0891b2', fillcolor='#ecfeff', fontcolor='#0891b2', fontsize='12')
    c.node('rewrite', 'Query Rewrite\n(self-contained rewrite\nusing chat history)',
           shape='box', fillcolor='#a5f3fc', color='#0891b2', fontcolor='#164e63')
    c.node('router', 'Router\n(synthesis / lookup / general)',
           shape='diamond', fillcolor='#a5f3fc', color='#0891b2', fontcolor='#164e63', width='2.8', height='1')
    c.node('retrieve', 'FAISS Retrieval + LLM Rerank\n(454 vectors, top-8 -> rerank -> top-4)',
           shape='box', fillcolor='#a5f3fc', color='#0891b2', fontcolor='#164e63')

# --- RAG Data Sources ---
with g.subgraph(name='cluster_data') as c:
    c.attr(label='RAG Data Sources', style='rounded,filled',
           color='#1565c0', fillcolor='#e3f2fd', fontcolor='#1565c0', fontsize='12')
    c.node('ds_papers', 'Research Papers\n(33 PDFs)', shape='cylinder', fillcolor='#e8eaf6', color='#5c6bc0', fontcolor='#283593', fontsize='9')
    c.node('ds_rules', 'LNP Design Rules\n(MCTS, constraints)', shape='cylinder', fillcolor='#e8eaf6', color='#5c6bc0', fontcolor='#283593', fontsize='9')
    c.node('ds_rxn', 'Reaction Templates\n(13 SMARTS)', shape='cylinder', fillcolor='#e8eaf6', color='#5c6bc0', fontcolor='#283593', fontsize='9')
    c.node('ds_data', 'Compound Data\n(217K blocks, 293 scores)', shape='cylinder', fillcolor='#e8eaf6', color='#5c6bc0', fontcolor='#283593', fontsize='9')

# --- Expert Workers (Sonnet 4.5) ---
with g.subgraph(name='cluster_experts') as c:
    c.attr(label='Parallel Expert Workers (Claude Sonnet 4.5 — strong reasoning)',
           style='rounded,filled', color='#6a1b9a', fillcolor='#f3e5f5', fontcolor='#6a1b9a', fontsize='12')
    c.node('rxn', 'Reaction Expert\n\n* SMARTS template matching\n* Functional group analysis\n* Feasibility assessment',
           shape='box', fillcolor='#ce93d8', color='#6a1b9a', fontcolor='#1a1a2e')
    c.node('lipid', 'Lipid Design Expert\n\n* Retrosynthesis routes\n* SAR analysis\n* Design rule compliance',
           shape='box', fillcolor='#ce93d8', color='#6a1b9a', fontcolor='#1a1a2e')
    c.node('genai', 'Generative AI Expert\n\n* De novo generation\n* RL optimization\n* Reward functions',
           shape='box', fillcolor='#ce93d8', color='#6a1b9a', fontcolor='#1a1a2e')
    c.node('pred', 'Property Prediction Expert\n\n* ML model recommendations\n* Uncertainty quantification',
           shape='box', fillcolor='#ce93d8', color='#6a1b9a', fontcolor='#1a1a2e')
    c.node('lit', 'Literature Scout\n\n* PubMed search\n* PubChem lookup\n* Web search',
           shape='box', fillcolor='#ce93d8', color='#6a1b9a', fontcolor='#1a1a2e')

# --- Lead Agent (Sonnet 4.5) ---
with g.subgraph(name='cluster_lead') as c:
    c.attr(label='Supervisor (Claude Sonnet 4.5)', style='rounded,filled',
           color='#059669', fillcolor='#ecfdf5', fontcolor='#059669', fontsize='12')
    c.node('lead', 'Lead Reasoning Agent\n\n* Critical evaluation of all experts\n* Conflict resolution\n* Confidence levels (HIGH/MED/LOW)\n* Final synthesized answer',
           shape='box', fillcolor='#a7f3d0', color='#059669', fontcolor='#064e3b')

# --- Output ---
with g.subgraph(name='cluster_output') as c:
    c.attr(label='Output', style='rounded,dashed', color='#888888', fontcolor='#555555', fontsize='12')
    c.node('answer', 'Final Answer\n(SSE streamed to client)',
           shape='box', fillcolor='#a5d6a7', color='#2e7d32', fontcolor='#1a1a2e')
    c.node('end', 'END', shape='circle', fillcolor='#e74c3c', fontcolor='white', width='0.9', fixedsize='true')

# --- Tech Stack ---
g.node('tech',
    'Model Assignment\n' + chr(0x2500)*25 + '\n'
    'Fast nodes:  Claude 3.5 Haiku\n'
    'Experts:     Claude Sonnet 4.5\n'
    'Lead Agent:  Claude Sonnet 4.5\n'
    'Embeddings:  Titan Embed v2\n'
    'Vector DB:   FAISS (local)\n'
    'Framework:   LangGraph\n'
    'Cloud:       AWS Bedrock (us-west-2)',
    shape='note', fillcolor='#eceff1', color='#90a4ae', fontcolor='#37474f', fontsize='10')

# --- Edges ---
g.edge('start', 'query')
g.edge('query', 'rewrite', label='  input')
g.edge('rewrite', 'router', label='  rewritten query', color='#0891b2', penwidth='2')
g.edge('router', 'retrieve', label='  query type', color='#0891b2', penwidth='2')

for ds in ['ds_papers', 'ds_rules', 'ds_rxn', 'ds_data']:
    g.edge(ds, 'retrieve', style='dashed', color='#90a4ae', arrowsize='0.6')

# Conditional routing label
g.edge('retrieve', 'rxn', label='  synthesis\n  queries', color='#1565c0', penwidth='2')
g.edge('retrieve', 'lipid', color='#1565c0', penwidth='2')
g.edge('retrieve', 'genai', color='#1565c0', penwidth='2')
g.edge('retrieve', 'pred', color='#1565c0', penwidth='2')
g.edge('retrieve', 'lit', label='  all queries', color='#1565c0', penwidth='2')

for expert in ['rxn', 'lipid', 'genai', 'pred', 'lit']:
    g.edge(expert, 'lead', color='#6a1b9a', penwidth='2')

g.edge('lead', 'answer', label='  final answer', color='#059669', penwidth='2')
g.edge('answer', 'end')

# Render
out_base = 'docs/reactome_lnp_agent_workflow_v3'
g.render(out_base, cleanup=True)
# Also render SVG and PNG
g.format = 'svg'
g.render(out_base, cleanup=True)
g.format = 'png'
g.render(out_base, cleanup=True)
print(f"Generated: {out_base}.pdf, .svg, .png")
