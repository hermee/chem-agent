use crate::types::*;
use std::path::PathBuf;

fn storage_path() -> PathBuf {
    let dir = dirs::data_local_dir().unwrap_or_else(|| PathBuf::from(".")).join("lnp-desktop");
    std::fs::create_dir_all(&dir).ok();
    dir.join("conversations.json")
}

pub fn load_conversations() -> Vec<Conversation> {
    std::fs::read_to_string(storage_path()).ok()
        .and_then(|data| serde_json::from_str::<Vec<Conversation>>(&data).ok())
        .map(|mut v| { v.truncate(20); v })
        .unwrap_or_default()
}

pub fn save_conversations(convs: &[Conversation]) {
    let slice = if convs.len() > 20 { &convs[..20] } else { convs };
    if let Ok(json) = serde_json::to_string(slice) {
        std::fs::write(storage_path(), json).ok();
    }
}

pub fn new_conversation() -> Conversation {
    Conversation {
        id: format!("{}", now_millis() as u64),
        title: "New Conversation".into(),
        messages: vec![],
        timestamp: now_millis(),
    }
}

pub fn update_conversation_messages(conv: &mut Conversation, messages: Vec<ChatMessage>) {
    conv.title = messages.iter().find(|m| m.role == "user")
        .map(|m| { let t: String = m.content.chars().take(50).collect(); if m.content.len() > 50 { format!("{t}...") } else { t } })
        .unwrap_or_else(|| conv.title.clone());
    conv.messages = messages;
    conv.timestamp = now_millis();
}
