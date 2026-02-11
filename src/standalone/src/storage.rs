use crate::types::*;
use web_sys::window;

const STORAGE_KEY: &str = "lnp_conversations";
const MAX_CONVERSATIONS: usize = 20;

pub fn load_conversations() -> Vec<Conversation> {
    window().and_then(|w| w.local_storage().ok().flatten())
        .and_then(|s| s.get_item(STORAGE_KEY).ok().flatten())
        .and_then(|data| serde_json::from_str::<Vec<Conversation>>(&data).ok())
        .map(|mut v| { v.truncate(MAX_CONVERSATIONS); v })
        .unwrap_or_default()
}

pub fn save_conversations(convs: &[Conversation]) {
    if let Some(storage) = window().and_then(|w| w.local_storage().ok().flatten()) {
        let slice = if convs.len() > MAX_CONVERSATIONS { &convs[..MAX_CONVERSATIONS] } else { convs };
        if let Ok(json) = serde_json::to_string(slice) { let _ = storage.set_item(STORAGE_KEY, &json); }
    }
}

pub fn new_conversation() -> Conversation {
    Conversation {
        id: format!("{}", js_sys::Date::now() as u64),
        title: "New Conversation".into(),
        messages: vec![],
        timestamp: js_sys::Date::now(),
    }
}

pub fn update_conversation_messages(conv: &mut Conversation, messages: Vec<ChatMessage>) {
    let title = messages.iter().find(|m| m.role == "user")
        .map(|m| {
            let t: String = m.content.chars().take(50).collect();
            if m.content.len() > 50 { format!("{t}...") } else { t }
        })
        .unwrap_or_else(|| conv.title.clone());
    conv.title = title;
    conv.messages = messages;
    conv.timestamp = js_sys::Date::now();
}
