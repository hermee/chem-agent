"""External search tools — PubMed, PubChem, and web search."""
import requests


def search_pubmed(query: str, max_results: int = 3) -> str:
    """Search PubMed via NCBI E-utilities and return article summaries."""
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    r = requests.get(f"{base}/esearch.fcgi", params={
        "db": "pubmed", "term": query, "retmax": max_results, "retmode": "json",
    }, timeout=10)
    ids = r.json().get("esearchresult", {}).get("idlist", [])
    if not ids:
        return "No PubMed results found."

    r = requests.get(f"{base}/esummary.fcgi", params={
        "db": "pubmed", "id": ",".join(ids), "retmode": "json",
    }, timeout=10)
    result_data = r.json().get("result", {})
    lines = []
    for uid in ids:
        doc = result_data.get(uid, {})
        title = doc.get("title", "N/A")
        source = doc.get("source", "")
        date = doc.get("pubdate", "")
        lines.append(f"- **{title}** ({source}, {date}) [PMID:{uid}]")
    return "\n".join(lines)


def search_pubchem(query: str, max_results: int = 3) -> str:
    """Search PubChem PUG REST for compound properties by name."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{requests.utils.quote(query)}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES/JSON"
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return f"No PubChem compound found for '{query}'."
    props = r.json().get("PropertyTable", {}).get("Properties", [])[:max_results]
    if not props:
        return f"No PubChem compound found for '{query}'."
    lines = []
    for p in props:
        lines.append(
            f"- **{p.get('IUPACName', 'N/A')}** | SMILES: `{p.get('CanonicalSMILES', '')}` "
            f"| MW: {p.get('MolecularWeight', '')} | Formula: {p.get('MolecularFormula', '')}"
        )
    return "\n".join(lines)


def search_web(query: str, max_results: int = 5) -> str:
    """Search the web via DuckDuckGo HTML (no API key needed)."""
    try:
        r = requests.get("https://html.duckduckgo.com/html/", params={"q": query},
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code != 200:
            return f"[Web search failed: HTTP {r.status_code}]"
        from html.parser import HTMLParser

        class DDGParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.results = []
                self._in_result = False
                self._in_snippet = False
                self._current = {}
                self._text = ""

            def handle_starttag(self, tag, attrs):
                attrs_d = dict(attrs)
                if tag == "a" and "result__a" in attrs_d.get("class", ""):
                    self._in_result = True
                    self._current = {"url": attrs_d.get("href", ""), "title": ""}
                    self._text = ""
                if tag == "a" and "result__snippet" in attrs_d.get("class", ""):
                    self._in_snippet = True
                    self._text = ""

            def handle_data(self, data):
                if self._in_result or self._in_snippet:
                    self._text += data

            def handle_endtag(self, tag):
                if tag == "a" and self._in_result:
                    self._current["title"] = self._text.strip()
                    self._in_result = False
                if tag == "a" and self._in_snippet:
                    self._current["snippet"] = self._text.strip()
                    self.results.append(self._current)
                    self._current = {}
                    self._in_snippet = False

        parser = DDGParser()
        parser.feed(r.text)
        if not parser.results:
            return "No web results found."
        lines = []
        for res in parser.results[:max_results]:
            title = res.get("title", "N/A")
            snippet = res.get("snippet", "")
            url = res.get("url", "")
            lines.append(f"- **{title}**: {snippet} ({url})")
        return "\n".join(lines)
    except Exception as e:
        return f"[Web search failed: {e}]"
