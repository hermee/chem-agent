"""FastAPI backend for Reactome LNP Agent."""
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from rdkit import Chem
from rdkit.Chem import QED, Descriptors, Crippen, rdMolDescriptors, rdChemReactions, RDConfig
from rdkit.Chem.Draw import rdMolDraw2D
import os, sys
sys.path.append(os.path.join(RDConfig.RDContribDir, 'SA_Score'))
import sascorer

from .agent import run_agent, graph, ReactomeState
from .config import BEDROCK_MODEL_ID, AWS_REGION

app = FastAPI(title="Reactome LNP Agent API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

REACTIONS = [
    {"id": 10001, "name": "Amide formation", "reactants": "Amine + Carboxylic acid", "smarts_reactants": "[*:1][#7:2]([H])[H,*:3] + [OH,O-][C:4]([*:5])=[O:6]", "smarts_product": "[*:5][C:4](=[O:6])[#7:2]([*:1])[H,*:3]"},
    {"id": 10003, "name": "Ester formation", "reactants": "Carboxylic acid + Hydroxyl", "smarts_reactants": "[OH,O-][C:1]([*:2])=[O:3] + [*:4][OH:5]", "smarts_product": "[*:2][C:1](=[O:3])[O:5][*:4]"},
    {"id": 10005, "name": "Amine alkylation", "reactants": "Amine + Alcohol", "smarts_reactants": "[*:1][#7:2]([H])[H,*:3] + [*:4][CH2:5][OH:6]", "smarts_product": "[*:1][#7:2]([*:3])[C:5][*:4]"},
    {"id": 10007, "name": "Thioether formation", "reactants": "Amine + Thiol", "smarts_reactants": "[*:1][#7:2]([H])[H,*:3] + [*:4][CH2:5][SH:6]", "smarts_product": "[*:1][#7:2]([*:3])[C:5][*:4]"},
    {"id": 10009, "name": "Epoxide opening", "reactants": "Amine + Epoxide", "smarts_reactants": "[*:1][#7:2]([H])[H,*:3] + [*:4][CH:5]1[O:6][CH2:7]1", "smarts_product": "[*:1][#7:2]([*:3])[C:7][C:5]([OH])[*:4]"},
    {"id": 10010, "name": "Michael addition (acrylate)", "reactants": "Amine + Alkyl acrylate", "smarts_reactants": "[*:1][#7:2]([H])[H,*:3] + [*:4][O:5][C:6](=[O:7])[CH:8]=[CH2:9]", "smarts_product": "[*:1][#7:2]([*:3])[C:9][C:8][C:6](=[O:7])[O:5][*:4]"},
    {"id": 10011, "name": "Michael addition (acrylamide)", "reactants": "Amine + Alkyl acrylamide", "smarts_reactants": "[*:1][#7:2]([H])[H,*:3] + [*:4][#7:5]([H])[C:6](=[O:7])[CH:8]=[CH2:9]", "smarts_product": "[*:1][#7:2]([*:3])[C:9][C:8][C:6](=[O:7])[#7:5]([H])[*:4]"},
    {"id": 10012, "name": "N-methylation", "reactants": "Amine + Methyl", "smarts_reactants": "[*:1][#7:2]([H])[H,*:3] + [*:4][CH3:5]", "smarts_product": "[*:1][#7:2]([*:3])[C:5]", "warning": "Invalid leaving group"},
    {"id": 10013, "name": "Phosphate formation", "reactants": "Tertiary amine + Dioxaphospholane", "smarts_reactants": "[*:1][N:2]([*:3])[*:4] + [*:5][O:6][P:7]1(=[O:8])[O:9][CH2:10][CH2:11][O:12]1", "smarts_product": "[*:1][N+:2]([*:3])([*:4])[C:10][C:11][O:12][P:7]([O:9])([O:6][*:5])=[O:8]"},
    {"id": 10014, "name": "Phosphate formation (alt)", "reactants": "Tertiary amine + Dioxaphospholane", "smarts_reactants": "[*:1][#7:2]([*:3])[*:4] + [*:5][O:6][P:7](=[O:8])[O:9][CH2:10][CH2:11][O:12]", "smarts_product": "[*:1][#7+:2]([*:3])([*:4])[C:10][C:11][O:12][P:7]([O-:9])([O:6][*:5])=[O:8]"},
    {"id": 10015, "name": "Imine formation", "reactants": "Primary amine + Aldehyde", "smarts_reactants": "[*:1][#7:2]([H])[H] + [*:4][CH:5]=[O:6]", "smarts_product": "[*:1][#7:2]=[C:5][*:4]"},
    {"id": 10016, "name": "Reductive amination", "reactants": "Secondary amine + Aldehyde", "smarts_reactants": "[*:1][#7:2]([H])[*:3] + [*:4][CH:5]=[O:6]", "smarts_product": "[*:1][#7:2]([*:3])[C:5][*:4]"},
    {"id": 10017, "name": "Amide (reverse)", "reactants": "Primary amine + Aldehyde", "smarts_reactants": "[*:1][#7:2]([H])[H] + [*:4][CH:5]=[O:6]", "smarts_product": "[*:4][C:5](=[O:6])[#7:2]([*:1])[H]", "warning": "Chemically invalid"},
]


class ChatRequest(BaseModel):
    message: str


class QueryRequest(BaseModel):
    query: str


class SmilesRequest(BaseModel):
    smiles: str


@app.get("/api/health")
def health():
    return {"status": "ok", "model": BEDROCK_MODEL_ID, "region": AWS_REGION}


@app.get("/api/reactions")
def get_reactions():
    return {"reactions": REACTIONS}


@app.get("/api/reactions/{reaction_id}/svg")
def get_reaction_svg(reaction_id: int):
    rxn_data = next((r for r in REACTIONS if r["id"] == reaction_id), None)
    if not rxn_data:
        return Response("Not found", status_code=404)
    smarts = rxn_data["smarts_reactants"].replace(" + ", ".") + ">>" + rxn_data["smarts_product"]
    rxn = rdChemReactions.ReactionFromSmarts(smarts)
    if not rxn:
        return Response("Invalid SMARTS", status_code=400)
    d = rdMolDraw2D.MolDraw2DSVG(1200, 350)
    d.drawOptions().padding = 0.15
    d.DrawReaction(rxn)
    d.FinishDrawing()
    return Response(d.GetDrawingText(), media_type="image/svg+xml")


@app.post("/api/analyze-smiles")
def analyze_smiles(req: SmilesRequest):
    mol = Chem.MolFromSmiles(req.smiles)
    if not mol:
        return {"error": "Invalid SMILES"}
    scores = {
        "qed": round(QED.qed(mol), 4),
        "sa_score": round(sascorer.calculateScore(mol), 4),
        "mol_weight": round(Descriptors.MolWt(mol), 2),
        "logp": round(Crippen.MolLogP(mol), 2),
        "tpsa": round(Descriptors.TPSA(mol), 2),
        "hba": rdMolDescriptors.CalcNumHBA(mol),
        "hbd": rdMolDescriptors.CalcNumHBD(mol),
        "rotatable_bonds": rdMolDescriptors.CalcNumRotatableBonds(mol),
        "num_rings": rdMolDescriptors.CalcNumRings(mol),
        "heavy_atoms": mol.GetNumHeavyAtoms(),
    }
    d = rdMolDraw2D.MolDraw2DSVG(600, 300)
    d.drawOptions().padding = 0.1
    d.DrawMolecule(mol)
    d.FinishDrawing()
    return {"smiles": req.smiles, "scores": scores, "svg": d.GetDrawingText()}


@app.post("/api/query")
def query_agent(req: QueryRequest):
    result = run_agent(req.query)
    return {
        "query": req.query,
        "reaction_analysis": result["reaction_analysis"],
        "design_rules_check": result["design_rules_check"],
        "synthesis_plan": result["synthesis_plan"],
        "final_answer": result["final_answer"],
    }


@app.post("/api/chat")
def chat_stream(req: ChatRequest):
    """SSE streaming chat endpoint with real node-by-node progress."""
    def generate():
        node_status = {
            "retrieve": "🔍 Retrieving relevant documents...",
            "reaction_expert": "⚗️ Analyzing reaction templates...",
            "design_rules": "📏 Checking design rules...",
            "synthesis_planner": "🧪 Planning synthesis route...",
            "final_answer": "📋 Generating final answer...",
        }

        state = {
            "query": req.message,
            "retrieved_context": "",
            "reaction_analysis": "",
            "design_rules_check": "",
            "synthesis_plan": "",
            "final_answer": "",
        }

        # Stream graph execution node-by-node
        for event in graph.stream(state, stream_mode="updates"):
            for node_name in event:
                if node_name in node_status:
                    yield f"data: {json.dumps({'type': 'status', 'step': node_name, 'message': node_status[node_name]})}\n\n"
                state.update(event[node_name])

        yield f"data: {json.dumps({'type': 'answer', 'content': state['final_answer']})}\n\n"
        yield f"data: {json.dumps({'type': 'details', 'reaction_analysis': state['reaction_analysis'], 'design_rules_check': state['design_rules_check'], 'synthesis_plan': state['synthesis_plan']})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
