use dioxus::prelude::*;
use crate::api::{self, API_BASE};
use crate::storage;
use crate::types::*;

#[component]
pub fn ChatPage() -> Element {
    let mut conversations = use_signal(|| storage::load_conversations());
    let mut current_id = use_signal(|| {
        let convs = storage::load_conversations();
        if convs.is_empty() { String::new() } else { convs[0].id.clone() }
    });
    let mut input_text = use_signal(String::new);
    let mut loading = use_signal(|| false);
    let mut status_msg = use_signal(|| "Thinking...".to_string());
    let mut expanded_detail = use_signal(|| -1i32);

    // Ensure at least one conversation
    if conversations().is_empty() {
        let c = storage::new_conversation();
        current_id.set(c.id.clone());
        conversations.set(vec![c]);
    } else if current_id().is_empty() {
        current_id.set(conversations()[0].id.clone());
    }

    let current_messages = {
        let convs = conversations();
        let id = current_id();
        convs.iter().find(|c| c.id == id).map(|c| c.messages.clone()).unwrap_or_default()
    };

    let mut send_message = move |text: String| {
        if text.trim().is_empty() || loading() { return; }
        let mut convs = conversations();
        let id = current_id();
        if let Some(conv) = convs.iter_mut().find(|c| c.id == id) {
            conv.messages.push(ChatMessage { role: "user".into(), content: text.clone(), details: None });
            storage::update_conversation_messages(conv, conv.messages.clone());
        }
        storage::save_conversations(&convs);
        conversations.set(convs.clone());
        input_text.set(String::new());
        loading.set(true);
        status_msg.set("Thinking...".into());

        let history = convs.iter().find(|c| c.id == id)
            .map(|c| build_chat_history(&c.messages)).unwrap_or_default();
        let cid = id.clone();

        spawn(async move {
            let mut answer = String::new();
            let mut details: Option<ChatDetails> = None;
            let mut err_msg: Option<String> = None;

            let body = serde_json::json!({ "message": text, "chat_history": history });
            match reqwest::Client::new().post(format!("{API_BASE}/chat")).json(&body).send().await {
                Ok(resp) => match resp.text().await {
                    Ok(full) => {
                        let mut buf = String::new();
                        for ev in api::parse_sse_lines(&mut buf, &full) {
                            match ev {
                                SseEvent::Status { message } => { status_msg.set(message); }
                                SseEvent::Answer { content } => { answer = content; }
                                SseEvent::Details { reaction_analysis, lipid_design_analysis, generative_analysis, prediction_analysis, literature_context, web_context } => {
                                    details = Some(ChatDetails { reaction_analysis, lipid_design_analysis, generative_analysis, prediction_analysis, literature_context, web_context });
                                }
                                SseEvent::Error { message } => { err_msg = Some(message); }
                            }
                        }
                    }
                    Err(e) => { err_msg = Some(format!("Read failed: {e}")); }
                },
                Err(e) => { err_msg = Some(format!("Connection failed: {e}")); }
            }

            let mut convs = conversations();
            if let Some(conv) = convs.iter_mut().find(|c| c.id == cid) {
                if let Some(e) = err_msg {
                    conv.messages.push(ChatMessage { role: "assistant".into(), content: format!("⚠️ {e}"), details: None });
                } else {
                    conv.messages.push(ChatMessage { role: "assistant".into(), content: answer, details });
                }
                storage::update_conversation_messages(conv, conv.messages.clone());
            }
            storage::save_conversations(&convs);
            conversations.set(convs);
            loading.set(false);
        });
    };

    rsx! {
        div { class: "chat-container",
            div { class: "chat-history",
                div { class: "history-header",
                    h3 { "History" }
                    button { class: "btn-new",
                        onclick: move |_| {
                            let c = storage::new_conversation();
                            current_id.set(c.id.clone());
                            let mut convs = conversations();
                            convs.insert(0, c);
                            storage::save_conversations(&convs);
                            conversations.set(convs);
                        },
                        "+ New"
                    }
                }
                div { class: "history-list",
                    for conv in conversations().iter() {
                        div {
                            class: if conv.id == current_id() { "history-item active" } else { "history-item" },
                            onclick: { let id = conv.id.clone(); move |_| current_id.set(id.clone()) },
                            div { class: "history-title", "💬 {conv.title}" }
                            div { class: "history-date", "{format_timestamp(conv.timestamp)}" }
                        }
                    }
                }
            }
            div { class: "chat-main",
                div { style: "padding: 16px 24px; border-bottom: 1px solid #e2e8f0; background: white;",
                    h2 { style: "font-size: 18px; font-weight: 700; color: #1e293b;", "🧬 Ionizable Lipid Design Assistant" }
                    p { style: "font-size: 13px; color: #94a3b8;", "Ask about reaction templates, design rules, and synthesis routes" }
                }
                div { class: "messages-container",
                    if current_messages.is_empty() && !loading() {
                        div { class: "empty-state",
                            div { class: "empty-icon", "🧪" }
                            div { class: "empty-title", "Start a conversation" }
                            div { class: "empty-text", "Ask about ionizable lipid design, reaction templates, MCTS strategies, or synthesis planning." }
                            div { style: "display: grid; grid-template-columns: 1fr 1fr; gap: 12px; max-width: 500px; margin-top: 24px;",
                                for &q in SAMPLE_QUERIES {
                                    button {
                                        style: "text-align: left; font-size: 13px; padding: 12px 16px; border-radius: 12px; border: 1px solid #e2e8f0; background: white; cursor: pointer; color: #475569;",
                                        onclick: move |_| send_message(q.to_string()),
                                        "{q}"
                                    }
                                }
                            }
                        }
                    }
                    for (idx, msg) in current_messages.iter().enumerate() {
                        div { class: format!("message {}", msg.role),
                            div { class: "message-bubble", dangerous_inner_html: "{render_markdown(&msg.content)}" }
                        }
                        if msg.role == "assistant" {
                            if let Some(ref det) = msg.details {
                                div { style: "margin: -8px 0 16px 0; padding: 0 16px;",
                                    button {
                                        style: "font-size: 12px; font-weight: 600; color: #059669; cursor: pointer; background: none; border: none;",
                                        onclick: { let i = idx as i32; move |_| { let c = expanded_detail(); expanded_detail.set(if c == i { -1 } else { i }); } },
                                        if expanded_detail() == idx as i32 { "▼ Hide details" } else { "▶ Show expert analyses" }
                                    }
                                    if expanded_detail() == idx as i32 {
                                        div { style: "margin-top: 8px; display: flex; flex-direction: column; gap: 8px;",
                                            for &(key, title) in DETAIL_SECTIONS {
                                                { let val = get_detail_value(det, key);
                                                  if !val.is_empty() { rsx! {
                                                    details { style: "background: #f8fafc; border-radius: 10px; padding: 12px; font-size: 12px;",
                                                        summary { style: "font-weight: 600; color: #475569; cursor: pointer;", "{title}" }
                                                        div { style: "margin-top: 8px; color: #64748b; white-space: pre-wrap;", dangerous_inner_html: "{render_markdown(&val)}" }
                                                    }
                                                  }} else { rsx! {} }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    if loading() {
                        div { class: "loading",
                            div { class: "loading-dots",
                                div { class: "loading-dot" }
                                div { class: "loading-dot" }
                                div { class: "loading-dot" }
                            }
                            span { "{status_msg}" }
                        }
                    }
                }
                div { class: "message-input-container",
                    div { class: "message-input-row",
                        input {
                            class: "message-input", value: "{input_text}",
                            placeholder: "Ask about ionizable lipid design...", disabled: loading(),
                            oninput: move |e| input_text.set(e.value()),
                            onkeypress: move |e: KeyboardEvent| {
                                if e.key() == Key::Enter { let t = input_text(); if !t.is_empty() { send_message(t); } }
                            },
                        }
                        button { class: "btn-send", disabled: loading() || input_text().trim().is_empty(),
                            onclick: move |_| { let t = input_text(); if !t.is_empty() { send_message(t); } },
                            "Send"
                        }
                    }
                }
            }
        }
    }
}
