mod api;
mod pages;
mod storage;
mod types;

use dioxus::prelude::*;
use types::Page;

fn main() {
    LaunchBuilder::desktop()
        .with_cfg(dioxus::desktop::Config::new()
            .with_window(dioxus::desktop::WindowBuilder::new()
                .with_title("🧬 Reactome LNP Agent")
                .with_inner_size(dioxus::desktop::LogicalSize::new(1400.0, 900.0))))
        .launch(App);
}

#[component]
fn App() -> Element {
    let mut current_page = use_signal(|| Page::Chat);
    let mut show_sidebar = use_signal(|| true);
    let mut connected = use_signal(|| false);

    use_effect(move || { spawn(async move { connected.set(api::fetch_health().await.is_ok()); }); });

    rsx! {
        style { {include_str!("../assets/app.css")} }
        div { class: "app-container",
            if show_sidebar() {
                nav { class: "sidebar",
                    div { class: "sidebar-header",
                        div { style: "display: flex; align-items: center; gap: 12px; cursor: pointer;",
                            onclick: move |_| current_page.set(Page::Chat),
                            div { style: "width: 40px; height: 40px; border-radius: 12px; background: linear-gradient(135deg, #10b981, #06b6d4); display: flex; align-items: center; justify-content: center; font-size: 18px;", "🧬" }
                            div { h1 { "Reactome" } p { "LNP Agent" } }
                        }
                    }
                    div { class: "sidebar-nav",
                        NavItem { icon: "💬", label: "Chat", active: matches!(current_page(), Page::Chat), onclick: move |_| current_page.set(Page::Chat) }
                        NavItem { icon: "⚗️", label: "Reactions", active: matches!(current_page(), Page::Reactions), onclick: move |_| current_page.set(Page::Reactions) }
                        NavItem { icon: "🔄", label: "Workflow", active: matches!(current_page(), Page::Workflow), onclick: move |_| current_page.set(Page::Workflow) }
                        NavItem { icon: "🧪", label: "Molecular Analysis", active: matches!(current_page(), Page::MolecularAnalysis), onclick: move |_| current_page.set(Page::MolecularAnalysis) }
                    }
                    div { style: "padding: 16px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: auto;",
                        div { style: "display: flex; align-items: center; gap: 8px; padding: 8px 12px;",
                            div { style: if connected() { "width: 8px; height: 8px; border-radius: 50%; background: #10b981;" } else { "width: 8px; height: 8px; border-radius: 50%; background: #ef4444;" } }
                            span { style: "font-size: 12px; color: #94a3b8;", if connected() { "Bedrock Connected" } else { "Disconnected" } }
                        }
                    }
                }
            }
            div { class: "main-content",
                div { class: "header",
                    button { class: "sidebar-toggle", onclick: move |_| show_sidebar.set(!show_sidebar()),
                        if show_sidebar() { "◀" } else { "☰" }
                    }
                    h2 { match current_page() {
                        Page::Chat => "💬 Chat",
                        Page::Reactions => "⚗️ Reactions",
                        Page::Workflow => "🔄 Workflow",
                        Page::MolecularAnalysis => "🧪 Molecular Analysis",
                    }}
                }
                div { class: "page-content",
                    match current_page() {
                        Page::Chat => rsx! { pages::chat::ChatPage {} },
                        Page::Reactions => rsx! { pages::reactions::ReactionsPage {} },
                        Page::Workflow => rsx! { pages::workflow::WorkflowPage {} },
                        Page::MolecularAnalysis => rsx! { pages::molecular::MolecularAnalysisPage {} },
                    }
                }
            }
        }
    }
}

#[component]
fn NavItem(icon: &'static str, label: &'static str, active: bool, onclick: EventHandler<MouseEvent>) -> Element {
    rsx! { div { class: if active { "nav-item active" } else { "nav-item" }, onclick,
        span { class: "nav-icon", "{icon}" }
        span { class: "nav-label", "{label}" }
    }}
}
