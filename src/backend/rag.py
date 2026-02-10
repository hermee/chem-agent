"""FAISS RAG setup — loads or builds the vector index."""
import os, glob
import pandas as pd
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from .config import AWS_REGION, DATA_DIR, FAISS_INDEX_PATH


def _load_documents() -> list[Document]:
    docs = []
    for p in glob.glob(f"{DATA_DIR}/papers/**/*.pdf", recursive=True) + glob.glob(f"{DATA_DIR}/papers/*.pdf") + glob.glob(f"{DATA_DIR}/lnp_data/*.pdf"):
        for d in PyMuPDFLoader(p).load():
            d.metadata["source_type"] = "paper"
            docs.append(d)

    for md in glob.glob(f"{DATA_DIR}/**/*.md", recursive=True):
        docs.append(Document(page_content=open(md).read(), metadata={"source": md, "source_type": "rules"}))

    rxn_path = f"{DATA_DIR}/lnp_data/lnp_reaction.py"
    if os.path.exists(rxn_path):
        docs.append(Document(page_content=open(rxn_path).read(), metadata={"source": rxn_path, "source_type": "reaction_templates"}))

    liver_path = f"{DATA_DIR}/lnp_data/final_liver.csv"
    if os.path.exists(liver_path):
        df = pd.read_csv(liver_path)
        summary = f"# Liver Score Dataset\nTotal: {len(df)}\nTop 10:\n"
        for _, r in df.nlargest(10, "target").iterrows():
            summary += f"  {r['smiles'][:80]} | score={r['target']:.4f}\n"
        docs.append(Document(page_content=summary, metadata={"source": "final_liver.csv", "source_type": "data"}))

    bb_path = f"{DATA_DIR}/lnp_data/filtered_building_blocks.csv"
    if os.path.exists(bb_path):
        df = pd.read_csv(bb_path)
        summary = f"# Building Blocks\nTotal: {len(df)}\nSample:\n"
        for _, r in df.head(20).iterrows():
            summary += f"  {r['smiles']} (id={r['reagent_id']})\n"
        docs.append(Document(page_content=summary, metadata={"source": "filtered_building_blocks.csv", "source_type": "data"}))

    return docs


embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0", region_name=AWS_REGION)


def get_vectorstore() -> FAISS:
    if os.path.exists(FAISS_INDEX_PATH):
        return FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    docs = _load_documents()
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)
    vs = FAISS.from_documents(chunks, embeddings)
    vs.save_local(FAISS_INDEX_PATH)
    return vs


vectorstore = get_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
