use crate::types::*;
use std::collections::HashMap;
use wasm_bindgen::prelude::*;
use wasm_bindgen_futures::JsFuture;

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

/// Stream SSE from /api/chat using web_sys fetch + ReadableStream for real-time updates.
pub async fn stream_chat(message: &str, chat_history: &str) -> Result<Vec<SseEvent>, String> {
    use web_sys::{Request, RequestInit, RequestMode, Headers, Response as WsResponse};

    let opts = RequestInit::new();
    opts.set_method("POST");
    opts.set_mode(RequestMode::Cors);
    let headers = Headers::new().map_err(|e| format!("{e:?}"))?;
    headers.set("Content-Type", "application/json").map_err(|e| format!("{e:?}"))?;
    opts.set_headers(&headers);
    let body = serde_json::json!({"message": message, "chat_history": chat_history});
    opts.set_body(&JsValue::from_str(&body.to_string()));

    let request = Request::new_with_str_and_init(&format!("{API_BASE}/chat"), &opts).map_err(|e| format!("{e:?}"))?;
    read_sse_stream(request).await
}

/// Stream SSE from /api/chat-with-files using FormData for file upload.
pub async fn stream_chat_with_files(message: &str, chat_history: &str, files: &[web_sys::File]) -> Result<Vec<SseEvent>, String> {
    use web_sys::{Request, RequestInit, RequestMode, FormData as WsFormData};

    let form = WsFormData::new().map_err(|e| format!("{e:?}"))?;
    form.append_with_str("message", message).map_err(|e| format!("{e:?}"))?;
    form.append_with_str("chat_history", chat_history).map_err(|e| format!("{e:?}"))?;
    for f in files {
        form.append_with_blob_and_filename("files", f, &f.name()).map_err(|e| format!("{e:?}"))?;
    }

    let opts = RequestInit::new();
    opts.set_method("POST");
    opts.set_mode(RequestMode::Cors);
    opts.set_body(&form);

    let request = Request::new_with_str_and_init(&format!("{API_BASE}/chat-with-files"), &opts).map_err(|e| format!("{e:?}"))?;
    read_sse_stream(request).await
}

async fn read_sse_stream(request: web_sys::Request) -> Result<Vec<SseEvent>, String> {
    use web_sys::Response as WsResponse;

    let window = web_sys::window().ok_or("no window")?;
    let resp_val = JsFuture::from(window.fetch_with_request(&request)).await.map_err(|e| format!("{e:?}"))?;
    let resp: WsResponse = resp_val.dyn_into().map_err(|_| "not a Response")?;
    if !resp.ok() { return Err(format!("Server error: {}", resp.status())); }

    let body_stream = resp.body().ok_or("no body")?;
    let reader = body_stream.get_reader().dyn_into::<web_sys::ReadableStreamDefaultReader>().map_err(|_| "not a reader")?;
    let mut buffer = String::new();
    let mut all_events = Vec::new();

    loop {
        let chunk = JsFuture::from(reader.read()).await.map_err(|e| format!("{e:?}"))?;
        let done = js_sys::Reflect::get(&chunk, &JsValue::from_str("done"))
            .map_err(|e| format!("{e:?}"))?.as_bool().unwrap_or(true);
        if done { break; }
        let value = js_sys::Reflect::get(&chunk, &JsValue::from_str("value")).map_err(|e| format!("{e:?}"))?;
        // Decode Uint8Array to string
        let arr = js_sys::Uint8Array::new(&value);
        let bytes = arr.to_vec();
        let text = String::from_utf8_lossy(&bytes);
        for event in parse_sse_lines(&mut buffer, &text) {
            all_events.push(event);
        }
    }
    Ok(all_events)
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_reaction_svg_url() {
        assert_eq!(reaction_svg_url(10001), "http://localhost:8000/api/reactions/10001/svg");
    }

    #[test]
    fn test_parse_sse_status() {
        let mut b = String::new();
        let e = parse_sse_lines(&mut b, "data: {\"type\":\"status\",\"message\":\"ok\"}\n\n");
        assert_eq!(e.len(), 1);
        match &e[0] { SseEvent::Status { message } => assert_eq!(message, "ok"), _ => panic!() }
    }

    #[test]
    fn test_parse_sse_done() {
        let mut b = String::new();
        assert!(parse_sse_lines(&mut b, "data: [DONE]\n\n").is_empty());
    }

    #[test]
    fn test_parse_sse_partial() {
        let mut b = String::new();
        assert!(parse_sse_lines(&mut b, "data: {\"type\":\"status\"").is_empty());
        assert_eq!(parse_sse_lines(&mut b, ",\"message\":\"ok\"}\n\n").len(), 1);
    }

    #[test]
    fn test_parse_sse_multiple() {
        let mut b = String::new();
        let e = parse_sse_lines(&mut b, "data: {\"type\":\"status\",\"message\":\"a\"}\ndata: {\"type\":\"answer\",\"content\":\"b\"}\n");
        assert_eq!(e.len(), 2);
    }

    #[test]
    fn test_parse_sse_ignores_non_data() {
        let mut b = String::new();
        let e = parse_sse_lines(&mut b, "event: ping\ndata: {\"type\":\"status\",\"message\":\"ok\"}\n");
        assert_eq!(e.len(), 1);
    }
}
