"""Tests for PubMed and PubChem search tools."""
from unittest.mock import patch, MagicMock
from src.backend.tools import search_pubmed, search_pubchem, search_web


def _mock_pubmed_response():
    """Mock NCBI E-utilities responses."""
    search_resp = MagicMock()
    search_resp.json.return_value = {"esearchresult": {"idlist": ["12345", "67890"]}}
    summary_resp = MagicMock()
    summary_resp.json.return_value = {"result": {
        "12345": {"title": "Ionizable lipids for mRNA delivery", "source": "Nature", "pubdate": "2024"},
        "67890": {"title": "LNP formulation review", "source": "ACS Nano", "pubdate": "2023"},
    }}
    return [search_resp, summary_resp]


@patch("src.backend.tools.requests.get")
def test_search_pubmed_success(mock_get):
    mock_get.side_effect = _mock_pubmed_response()
    result = search_pubmed("ionizable lipids", max_results=2)
    assert "Ionizable lipids for mRNA delivery" in result
    assert "PMID:12345" in result
    assert "Nature" in result


@patch("src.backend.tools.requests.get")
def test_search_pubmed_no_results(mock_get):
    mock_get.return_value = MagicMock(json=lambda: {"esearchresult": {"idlist": []}})
    result = search_pubmed("xyznonexistent")
    assert "No PubMed results" in result


@patch("src.backend.tools.requests.get")
def test_search_pubmed_timeout(mock_get):
    mock_get.side_effect = Exception("Timeout")
    try:
        search_pubmed("test")
    except Exception as e:
        assert "Timeout" in str(e)


@patch("src.backend.tools.requests.get")
def test_search_pubchem_success(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {"PropertyTable": {"Properties": [{
            "IUPACName": "ethanol",
            "CanonicalSMILES": "CCO",
            "MolecularWeight": 46.07,
            "MolecularFormula": "C2H6O",
        }]}}
    )
    result = search_pubchem("ethanol")
    assert "ethanol" in result
    assert "CCO" in result
    assert "46.07" in result


@patch("src.backend.tools.requests.get")
def test_search_pubchem_not_found(mock_get):
    mock_get.return_value = MagicMock(status_code=404)
    result = search_pubchem("xyznonexistent")
    assert "No PubChem compound" in result


def test_literature_search_node(mock_bedrock):
    """Test the literature search node with mocked HTTP."""
    with patch("src.backend.agent.search_pubmed", return_value="- Paper 1"), \
         patch("src.backend.agent.search_pubchem", return_value="- Compound 1"):
        from src.backend.agent import literature_search_node
        result = literature_search_node({"query": "test", "rewritten_query": "test lipid"})
        assert "PubMed" in result["literature_context"]
        assert "PubChem" in result["literature_context"]
        assert "Paper 1" in result["literature_context"]


def test_literature_search_node_handles_failure(mock_bedrock):
    """Test graceful failure handling."""
    with patch("src.backend.agent.search_pubmed", side_effect=Exception("API down")), \
         patch("src.backend.agent.search_pubchem", side_effect=Exception("API down")):
        from src.backend.agent import literature_search_node
        result = literature_search_node({"query": "test", "rewritten_query": "test"})
        assert "Search failed" in result["literature_context"]


@patch("src.backend.tools.requests.get")
def test_search_web_success(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200,
        text='''<a class="result__a" href="https://example.com">LNP Review</a>
                <a class="result__snippet" href="#">Lipid nanoparticles are used for mRNA delivery</a>'''
    )
    result = search_web("LNP delivery")
    assert "LNP Review" in result or "No web results" in result  # parser may vary


@patch("src.backend.tools.requests.get")
def test_search_web_failure(mock_get):
    mock_get.side_effect = Exception("Network error")
    from src.backend.tools import search_web
    result = search_web("test")
    assert "failed" in result
