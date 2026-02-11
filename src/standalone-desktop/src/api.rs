use crate::types::*;
use std::collections::HashMap;

pub const API_BASE: &str = "http://localhost:8000/api";

pub async fn fetch_health() -> Result<HealthResponse, String> {
    reqwest::get(format!("{API_BASE}/health")).await.map_err(|e| e.to_string())?
        .json().await.map_err(|e| e.to_string())
}

pub async fn fetch_reactions() -> Result<Vec<Reaction>, String> {
    let r: ReactionsResponse = reqwest::get(format!("{API_BASE}/reactions"))
        .await.map_err(|e| e.to_string())?.json().await.map_err(|e| e.to_string())?;
    Ok(r.reactions)
}

pub fn reaction_svg_url(id: i32) -> String { format!("{API_BASE}/reactions/{id}/svg") }

pub async fn fetch_analysis(smiles: &str) -> Result<AnalysisResult, String> {
    let mut body = HashMap::new();
    body.insert("smiles", smiles);
    let resp = reqwest::Client::new().post(format!("{API_BASE}/analyze-smiles"))
        .json(&body).send().await.map_err(|e| format!("Request failed: {e}"))?;
    let text = resp.text().await.map_err(|e| format!("Read failed: {e}"))?;
    if let Ok(err) = serde_json::from_str::<AnalysisError>(&text) {
        if let Some(e) = err.error { return Err(e); }
    }
    serde_json::from_str(&text).map_err(|e| format!("Parse failed: {e}"))
}

pub fn parse_sse_lines(buffer: &mut String, chunk: &str) -> Vec<SseEvent> {
    buffer.push_str(chunk);
    let mut events = Vec::new();
    while let Some(pos) = buffer.find('\n') {
        let line: String = buffer.drain(..=pos).collect();
        let line = line.trim();
        if !line.starts_with("data: ") { continue; }
        let data = &line[6..];
        if data == "[DONE]" { continue; }
        if let Ok(event) = serde_json::from_str::<SseEvent>(data) { events.push(event); }
    }
    events
}
