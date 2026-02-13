use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Clone, PartialEq)]
pub enum Page { Chat, Reactions, Workflow, MolecularAnalysis }

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ChatDetails {
    pub reaction_analysis: Option<String>,
    pub lipid_design_analysis: Option<String>,
    pub generative_analysis: Option<String>,
    pub prediction_analysis: Option<String>,
    pub literature_context: Option<String>,
    pub web_context: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatMessage {
    pub role: String,
    pub content: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub details: Option<ChatDetails>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Conversation {
    pub id: String,
    pub title: String,
    pub messages: Vec<ChatMessage>,
    pub timestamp: f64,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(tag = "type")]
pub enum SseEvent {
    #[serde(rename = "status")]
    Status { message: String },
    #[serde(rename = "answer")]
    Answer { content: String },
    #[serde(rename = "details")]
    Details {
        reaction_analysis: Option<String>,
        lipid_design_analysis: Option<String>,
        generative_analysis: Option<String>,
        prediction_analysis: Option<String>,
        literature_context: Option<String>,
        web_context: Option<String>,
    },
    #[serde(rename = "error")]
    Error { message: String },
}

#[derive(Debug, Clone, Deserialize)]
pub struct Reaction {
    pub id: i32,
    pub name: String,
    pub reactants: String,
    pub smarts_reactants: Option<String>,
    pub smarts_product: Option<String>,
    pub warning: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ReactionsResponse { pub reactions: Vec<Reaction> }

#[derive(Debug, Clone, Deserialize)]
pub struct AnalysisResult {
    pub smiles: String,
    pub scores: HashMap<String, f64>,
    pub svg: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct AnalysisError { pub error: Option<String> }

#[derive(Debug, Clone, Deserialize)]
pub struct HealthResponse {
    pub status: String,
    pub model: Option<String>,
    pub fast_model: Option<String>,
    pub region: Option<String>,
}

pub struct WorkflowStep {
    pub icon: &'static str,
    pub title: &'static str,
    pub description: &'static str,
    pub color: &'static str,
    pub parallel: bool,
}

pub const WORKFLOW_STEPS: &[WorkflowStep] = &[
    WorkflowStep { icon: "❓", title: "User Query", description: "Natural language question about ionizable lipid design", color: "linear-gradient(135deg, #10b981, #06b6d4)", parallel: false },
    WorkflowStep { icon: "🔄", title: "Query Rewrite", description: "Rewrites question to be self-contained using chat history (Claude 3.5 Haiku)", color: "linear-gradient(135deg, #64748b, #94a3b8)", parallel: false },
    WorkflowStep { icon: "🧭", title: "Router", description: "Classifies query as synthesis, lookup, or general (Claude 3.5 Haiku)", color: "linear-gradient(135deg, #3b82f6, #6366f1)", parallel: false },
    WorkflowStep { icon: "🔍", title: "FAISS Retrieval + Rerank", description: "454 vectors searched + LLM reranking (Claude 3.5 Haiku)", color: "linear-gradient(135deg, #3b82f6, #6366f1)", parallel: false },
    WorkflowStep { icon: "⚗️", title: "Reaction Expert", description: "SMARTS template matching, functional group analysis, feasibility", color: "linear-gradient(135deg, #8b5cf6, #a855f7)", parallel: true },
    WorkflowStep { icon: "🧬", title: "Lipid Design Expert", description: "Retrosynthesis routes, SAR analysis, design rule compliance", color: "linear-gradient(135deg, #8b5cf6, #a855f7)", parallel: true },
    WorkflowStep { icon: "🤖", title: "Generative AI Expert", description: "De novo generation models, RL optimization, reward functions", color: "linear-gradient(135deg, #8b5cf6, #a855f7)", parallel: true },
    WorkflowStep { icon: "📊", title: "Property Prediction Expert", description: "ML model recommendations, uncertainty quantification", color: "linear-gradient(135deg, #8b5cf6, #a855f7)", parallel: true },
    WorkflowStep { icon: "📚", title: "Literature Scout", description: "PubMed, PubChem, and web search for external evidence", color: "linear-gradient(135deg, #8b5cf6, #a855f7)", parallel: true },
    WorkflowStep { icon: "🧠", title: "Lead Agent", description: "Supervisor — critically evaluates all expert outputs, resolves conflicts, produces final answer", color: "linear-gradient(135deg, #10b981, #059669)", parallel: false },
];

pub const SCORE_KEYS: &[(&str, &str)] = &[
    ("qed", "QED (Drug-likeness)"), ("sa_score", "SA Score"), ("mol_weight", "Mol. Weight"),
    ("logp", "LogP"), ("tpsa", "TPSA (Å²)"), ("hba", "H-Bond Acc."),
    ("hbd", "H-Bond Don."), ("rotatable_bonds", "Rot. Bonds"),
    ("num_rings", "Rings"), ("heavy_atoms", "Heavy Atoms"),
];

pub const EXAMPLE_MOLECULES: &[(&str, &str)] = &[
    ("DLin-MC3-DMA", "CCCCCCCC/C=C\\CCCCCCCC(=O)OCC(CN(C)C)OC(=O)CCCCCCCC/C=C\\CCCCCCCC"),
    ("ALC-0315-like", "CCCCCCCCCCOC(=O)CC(CC(=O)OCCCCCCCCCC)N(C)C"),
    ("SM-102-like", "CCCCCCCCCCOC(=O)CCCN(C)CCCC(=O)OCCCCCCCCCC"),
];

pub const SAMPLE_QUERIES: &[&str] = &[
    "Design a 3-tail ionizable lipid with amine heads",
    "Which reactions work for epoxide-based tails?",
    "What are the issues with reaction 10012?",
    "Explain the MCTS tree structure for LNP design",
];

pub const DETAIL_SECTIONS: &[(&str, &str)] = &[
    ("reaction_analysis", "⚗️ Reaction Analysis"),
    ("lipid_design_analysis", "🧬 Lipid Design (Retrosynthesis + SAR + Rules)"),
    ("generative_analysis", "🤖 Generative AI Recommendations"),
    ("prediction_analysis", "📊 Property Prediction"),
    ("literature_context", "📚 Literature (PubMed/PubChem)"),
    ("web_context", "🌐 Web Search"),
];

pub fn score_class(key: &str, val: f64) -> &'static str {
    match key {
        "qed" if val > 0.5 => "score-good",
        "qed" if val > 0.3 => "score-warn",
        "qed" => "score-bad",
        "sa_score" if val < 3.0 => "score-good",
        "sa_score" if val < 5.0 => "score-warn",
        "sa_score" => "score-bad",
        _ => "",
    }
}

pub fn fmt_val(val: f64) -> String {
    if val.fract() == 0.0 && val.abs() < 1e6 { format!("{}", val as i64) }
    else { format!("{:.2}", val) }
}

pub fn render_markdown(text: &str) -> String {
    use pulldown_cmark::{html, Parser};
    let mut out = String::new();
    html::push_html(&mut out, Parser::new(text));
    out
}

pub fn build_chat_history(messages: &[ChatMessage]) -> String {
    messages.iter()
        .filter(|m| m.role == "user" || m.role == "assistant")
        .rev().take(10).collect::<Vec<_>>().into_iter().rev()
        .map(|m| {
            let role = if m.role == "user" { "User" } else { "Assistant" };
            let content: String = m.content.chars().take(500).collect();
            format!("{role}: {content}")
        })
        .collect::<Vec<_>>().join("\n")
}

pub fn format_timestamp(ts: f64) -> String {
    let days = ((js_sys::Date::now() - ts) / 86_400_000.0).floor() as i32;
    match days {
        0 => "Today".into(),
        1 => "Yesterday".into(),
        2..=6 => format!("{days}d ago"),
        _ => {
            let d = js_sys::Date::new(&wasm_bindgen::JsValue::from_f64(ts));
            format!("{}/{}/{}", d.get_month() + 1, d.get_date(), d.get_full_year())
        }
    }
}

pub fn get_detail_value(details: &ChatDetails, key: &str) -> String {
    match key {
        "reaction_analysis" => details.reaction_analysis.clone(),
        "lipid_design_analysis" => details.lipid_design_analysis.clone(),
        "generative_analysis" => details.generative_analysis.clone(),
        "prediction_analysis" => details.prediction_analysis.clone(),
        "literature_context" => details.literature_context.clone(),
        "web_context" => details.web_context.clone(),
        _ => None,
    }.unwrap_or_default()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_score_class() {
        assert_eq!(score_class("qed", 0.7), "score-good");
        assert_eq!(score_class("qed", 0.4), "score-warn");
        assert_eq!(score_class("qed", 0.1), "score-bad");
        assert_eq!(score_class("sa_score", 2.0), "score-good");
        assert_eq!(score_class("sa_score", 4.0), "score-warn");
        assert_eq!(score_class("sa_score", 6.0), "score-bad");
        assert_eq!(score_class("logp", 3.0), "");
    }

    #[test]
    fn test_fmt_val() {
        assert_eq!(fmt_val(5.0), "5");
        assert_eq!(fmt_val(3.14159), "3.14");
        assert_eq!(fmt_val(0.0), "0");
    }

    #[test]
    fn test_render_markdown() {
        let html = render_markdown("**bold** text");
        assert!(html.contains("<strong>bold</strong>"));
    }

    #[test]
    fn test_build_chat_history_empty() { assert_eq!(build_chat_history(&[]), ""); }

    #[test]
    fn test_build_chat_history_filters_status() {
        let msgs = vec![
            ChatMessage { role: "user".into(), content: "hello".into(), details: None },
            ChatMessage { role: "status".into(), content: "thinking".into(), details: None },
            ChatMessage { role: "assistant".into(), content: "hi".into(), details: None },
        ];
        let h = build_chat_history(&msgs);
        assert!(h.contains("User: hello"));
        assert!(h.contains("Assistant: hi"));
        assert!(!h.contains("thinking"));
    }

    #[test]
    fn test_build_chat_history_truncates() {
        let msgs = vec![ChatMessage { role: "user".into(), content: "x".repeat(600), details: None }];
        assert!(build_chat_history(&msgs).len() <= 510);
    }

    #[test]
    fn test_get_detail_value() {
        let d = ChatDetails { reaction_analysis: Some("rxn".into()), ..Default::default() };
        assert_eq!(get_detail_value(&d, "reaction_analysis"), "rxn");
        assert_eq!(get_detail_value(&d, "lipid_design_analysis"), "");
        assert_eq!(get_detail_value(&d, "unknown"), "");
    }

    #[test]
    fn test_conversation_serialization() {
        let c = Conversation { id: "1".into(), title: "T".into(), messages: vec![], timestamp: 1.0 };
        let j = serde_json::to_string(&c).unwrap();
        let p: Conversation = serde_json::from_str(&j).unwrap();
        assert_eq!(p.id, "1");
    }

    #[test]
    fn test_sse_event_parsing() {
        let e: SseEvent = serde_json::from_str(r#"{"type":"status","message":"ok"}"#).unwrap();
        match e { SseEvent::Status { message } => assert_eq!(message, "ok"), _ => panic!() }
        let e: SseEvent = serde_json::from_str(r#"{"type":"answer","content":"done"}"#).unwrap();
        match e { SseEvent::Answer { content } => assert_eq!(content, "done"), _ => panic!() }
        let e: SseEvent = serde_json::from_str(r#"{"type":"error","message":"fail"}"#).unwrap();
        match e { SseEvent::Error { message } => assert_eq!(message, "fail"), _ => panic!() }
    }

    #[test]
    fn test_sse_details_parsing() {
        let j = r#"{"type":"details","reaction_analysis":"r","lipid_design_analysis":null,"generative_analysis":"g","prediction_analysis":null,"literature_context":"l","web_context":null}"#;
        let e: SseEvent = serde_json::from_str(j).unwrap();
        match e {
            SseEvent::Details { reaction_analysis, generative_analysis, literature_context, .. } => {
                assert_eq!(reaction_analysis.unwrap(), "r");
                assert_eq!(generative_analysis.unwrap(), "g");
                assert_eq!(literature_context.unwrap(), "l");
            }
            _ => panic!()
        }
    }

    #[test]
    fn test_reaction_deserialization() {
        let r: Reaction = serde_json::from_str(r#"{"id":10001,"name":"Amide","reactants":"A+B"}"#).unwrap();
        assert_eq!(r.id, 10001);
        assert!(r.warning.is_none());
    }

    #[test]
    fn test_reaction_with_warning() {
        let r: Reaction = serde_json::from_str(r#"{"id":10012,"name":"N-meth","reactants":"A+B","warning":"Invalid"}"#).unwrap();
        assert_eq!(r.warning.as_deref(), Some("Invalid"));
    }

    #[test]
    fn test_analysis_result() {
        let r: AnalysisResult = serde_json::from_str(r#"{"smiles":"CCO","scores":{"qed":0.5},"svg":"<svg/>"}"#).unwrap();
        assert_eq!(r.scores.get("qed"), Some(&0.5));
    }

    #[test]
    fn test_health_response() {
        let h: HealthResponse = serde_json::from_str(r#"{"status":"ok","model":"c","region":"r"}"#).unwrap();
        assert_eq!(h.status, "ok");
    }

    #[test]
    fn test_constants() {
        assert_eq!(SCORE_KEYS.len(), 10);
        assert_eq!(EXAMPLE_MOLECULES.len(), 3);
        assert_eq!(SAMPLE_QUERIES.len(), 4);
        assert_eq!(DETAIL_SECTIONS.len(), 6);
        assert_eq!(WORKFLOW_STEPS.len(), 10);
    }

    #[test]
    fn test_workflow_parallel_steps() {
        let p: Vec<_> = WORKFLOW_STEPS.iter().filter(|s| s.parallel).collect();
        assert_eq!(p.len(), 5);
    }
}
