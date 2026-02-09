use dioxus::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

const API_BASE: &str = "http://localhost:8000/api";

// ============================================================================
// TYPES
// ============================================================================

#[derive(Clone, PartialEq)]
enum Page {
    Chat,
    Reactions,
    Workflow,
    MolecularAnalysis,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ChatMessage {
    role: String,
    content: String,
    details: Option<ChatDetails>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ChatDetails {
    reaction_analysis: Option<String>,
    design_rules_check: Option<String>,
    synthesis_plan: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Conversation {
    id: String,
    title: String,
    messages: Vec<ChatMessage>,
    timestamp: f64,
}

#[derive(Debug, Clone, Deserialize)]
struct Reaction {
    id: i32,
    name: String,
    reactants: String,
    smarts_reactants: Option<String>,
    smarts_product: Option<String>,
    warning: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
struct AnalysisResult {
    smiles: String,
    scores: HashMap<String, f64>,
    svg: String,
}

// ============================================================================
// MAIN APP
// ============================================================================

fn main() {
    dioxus::launch(App);
}

#[component]
fn App() -> Element {
    let mut current_page = use_signal(|| Page::Chat);
    let mut show_sidebar = use_signal(|| true);

    rsx! {
        div { class: "app-container",
            // Sidebar
            if show_sidebar() {
                Sidebar { current_page, on_page_change: move |page| current_page.set(page) }
            }
            
            // Main content
            div { class: "main-content",
                // Header
                Header { 
                    show_sidebar,
                    page_title: match current_page() {
                        Page::Chat => "💬 Chat",
                        Page::Reactions => "⚗️ Reactions",
                        Page::Workflow => "🔄 Workflow",
                        Page::MolecularAnalysis => "🧪 Molecular Analysis",
                    }
                }
                
                // Page content
                div { class: "page-content",
                    match current_page() {
                        Page::Chat => rsx! { ChatPage {} },
                        Page::Reactions => rsx! { ReactionsPage {} },
                        Page::Workflow => rsx! { WorkflowPage {} },
                        Page::MolecularAnalysis => rsx! { MolecularAnalysisPage {} },
                    }
                }
            }
        }
    }
}

// ============================================================================
// COMPONENTS
// ============================================================================

#[component]
fn Sidebar(current_page: Signal<Page>, on_page_change: EventHandler<Page>) -> Element {
    rsx! {
        div { class: "sidebar",
            div { class: "sidebar-header",
                h1 { "🧬 Reactome" }
                p { "LNP Agent" }
            }
            nav { class: "sidebar-nav",
                NavItem { 
                    icon: "💬", 
                    label: "Chat", 
                    active: matches!(current_page(), Page::Chat),
                    onclick: move |_| on_page_change.call(Page::Chat)
                }
                NavItem { 
                    icon: "⚗️", 
                    label: "Reactions", 
                    active: matches!(current_page(), Page::Reactions),
                    onclick: move |_| on_page_change.call(Page::Reactions)
                }
                NavItem { 
                    icon: "🔄", 
                    label: "Workflow", 
                    active: matches!(current_page(), Page::Workflow),
                    onclick: move |_| on_page_change.call(Page::Workflow)
                }
                NavItem { 
                    icon: "🧪", 
                    label: "Molecular Analysis", 
                    active: matches!(current_page(), Page::MolecularAnalysis),
                    onclick: move |_| on_page_change.call(Page::MolecularAnalysis)
                }
            }
        }
    }
}

#[component]
fn NavItem(icon: &'static str, label: &'static str, active: bool, onclick: EventHandler<MouseEvent>) -> Element {
    let class = if active { "nav-item active" } else { "nav-item" };
    rsx! {
        div { class, onclick,
            span { class: "nav-icon", "{icon}" }
            span { class: "nav-label", "{label}" }
        }
    }
}

#[component]
fn Header(show_sidebar: Signal<bool>, page_title: &'static str) -> Element {
    rsx! {
        div { class: "header",
            button { 
                class: "sidebar-toggle",
                onclick: move |_| show_sidebar.set(!show_sidebar()),
                if show_sidebar() { "◀" } else { "☰" }
            }
            h2 { "{page_title}" }
        }
    }
}

// ============================================================================
// PAGES
// ============================================================================

#[component]
fn ChatPage() -> Element {
    rsx! {
        div { class: "chat-page",
            "Chat page - Coming soon"
        }
    }
}

#[component]
fn ReactionsPage() -> Element {
    rsx! {
        div { class: "reactions-page",
            "Reactions page - Coming soon"
        }
    }
}

#[component]
fn WorkflowPage() -> Element {
    rsx! {
        div { class: "workflow-page",
            "Workflow page - Coming soon"
        }
    }
}

#[component]
fn MolecularAnalysisPage() -> Element {
    rsx! {
        div { class: "molecular-page",
            "Molecular Analysis page - Coming soon"
        }
    }
}
