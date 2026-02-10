"""Shared fixtures for backend tests."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def mock_bedrock():
    """Mock all Bedrock LLM calls."""
    mock_response = MagicMock()
    mock_response.content = "Mocked LLM response"

    with patch("src.backend.agent.llm") as mock_llm, \
         patch("src.backend.agent.llm_fast") as mock_llm_fast:
        mock_llm.invoke.return_value = mock_response
        mock_llm_fast.invoke.return_value = mock_response
        yield {"llm": mock_llm, "llm_fast": mock_llm_fast}


@pytest.fixture
def mock_retriever():
    """Mock FAISS retriever."""
    mock_doc = MagicMock()
    mock_doc.page_content = "Ionizable lipids with amine head groups show improved endosomal escape."
    mock_doc.metadata = {"source_type": "paper"}

    with patch("src.backend.agent.retriever") as mock_ret:
        mock_ret.invoke.return_value = [mock_doc] * 4
        yield mock_ret


@pytest.fixture
def mock_tools():
    """Mock all external search tools."""
    with patch("src.backend.agent.search_pubmed", return_value="- Mocked paper [PMID:123]"), \
         patch("src.backend.agent.search_pubchem", return_value="- Mocked compound"), \
         patch("src.backend.agent.search_web", return_value="- Mocked web result"):
        yield


@pytest.fixture
def client(mock_bedrock, mock_retriever, mock_tools):
    """FastAPI test client with mocked dependencies."""
    from src.backend.main import app
    yield TestClient(app)
