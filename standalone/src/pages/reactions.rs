use dioxus::prelude::*;
use crate::api;

#[component]
pub fn ReactionsPage() -> Element {
    let mut reactions = use_signal(|| Vec::new());
    let mut loaded = use_signal(|| false);

    use_effect(move || {
        spawn(async move {
            if let Ok(rxns) = api::fetch_reactions().await { reactions.set(rxns); }
            loaded.set(true);
        });
    });

    rsx! {
        div { class: "reactions-container",
            h2 { style: "font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 4px;", "⚗️ Mogam Reaction Templates (LNP)" }
            p { style: "font-size: 13px; color: #94a3b8; margin-bottom: 24px;", "13 SMARTS-based Mogam reactions for ionizable lipid synthesis" }
            if !loaded() {
                div { style: "padding: 24px; text-align: center; color: #94a3b8;", "Loading reactions..." }
            }
            if !reactions().is_empty() {
                div { style: "overflow-x: auto; margin-bottom: 32px;",
                    table { style: "width: 100%; border-collapse: collapse; font-size: 13px; background: white; border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden;",
                        thead { tr { style: "background: #f8fafc;",
                            th { style: "padding: 12px 16px; text-align: left; font-weight: 600; color: #1e293b; border-bottom: 1px solid #e2e8f0;", "ID" }
                            th { style: "padding: 12px 16px; text-align: left; font-weight: 600; color: #1e293b; border-bottom: 1px solid #e2e8f0;", "Reaction" }
                            th { style: "padding: 12px 16px; text-align: left; font-weight: 600; color: #1e293b; border-bottom: 1px solid #e2e8f0;", "Reactants" }
                            th { style: "padding: 12px 16px; text-align: left; font-weight: 600; color: #1e293b; border-bottom: 1px solid #e2e8f0;", "Status" }
                        }}
                        tbody {
                            for rxn in reactions().iter() {
                                tr { style: "border-bottom: 1px solid #e2e8f0;",
                                    td { style: "padding: 10px 16px; color: #64748b;", "{rxn.id}" }
                                    td { style: "padding: 10px 16px; font-weight: 500; color: #1e293b;", "{rxn.name}" }
                                    td { style: "padding: 10px 16px; color: #64748b;", "{rxn.reactants}" }
                                    td { style: "padding: 10px 16px;",
                                        if let Some(ref w) = rxn.warning {
                                            span { class: "badge-warning", "⚠️ {w}" }
                                        } else {
                                            span { class: "badge-valid", "✅ Valid" }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                h2 { style: "font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 4px;", "🧬 Mogam Reaction Diagrams" }
                p { style: "font-size: 13px; color: #94a3b8; margin-bottom: 20px;", "RDKit-rendered structural diagrams for each Mogam reaction template" }
                div { style: "display: flex; flex-direction: column; gap: 20px; padding-bottom: 24px;",
                    for rxn in reactions().iter() {
                        div { class: "reaction-card",
                            div { class: "reaction-header",
                                span { class: "reaction-name", "{rxn.name}" }
                                if let Some(ref w) = rxn.warning {
                                    span { class: "reaction-badge badge-warning", "⚠️ {w}" }
                                } else {
                                    span { class: "reaction-badge badge-valid", "✅ Valid" }
                                }
                            }
                            div { class: "reaction-reactants", "{rxn.reactants}" }
                            img { src: "{api::reaction_svg_url(rxn.id)}", alt: "{rxn.name}", style: "width: 100%; border-radius: 10px; background: white;" }
                        }
                    }
                }
            }
        }
    }
}
