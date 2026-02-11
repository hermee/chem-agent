use dioxus::prelude::*;
use crate::types::WORKFLOW_STEPS;

#[component]
pub fn WorkflowPage() -> Element {
    rsx! {
        div { class: "workflow-container",
            h2 { style: "font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 4px;", "🔄 Agent Workflow" }
            p { style: "font-size: 13px; color: #94a3b8; margin-bottom: 24px;", "LangGraph pipeline for ionizable lipid analysis" }
            div { class: "workflow-diagram",
                div { style: "max-width: 640px; margin: 0 auto; display: flex; flex-direction: column; gap: 16px;",
                    for (i, step) in WORKFLOW_STEPS.iter().enumerate() {
                        div { style: "display: flex; align-items: flex-start; gap: 16px;",
                            div { style: "display: flex; flex-direction: column; align-items: center;",
                                div { style: "width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; color: white; background: {step.color};", "{step.icon}" }
                                if i < WORKFLOW_STEPS.len() - 1 {
                                    div { style: "width: 2px; height: 32px; background: #e2e8f0; margin-top: 8px;" }
                                }
                            }
                            div { style: "flex: 1; background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px;",
                                h3 { style: "font-size: 15px; font-weight: 600; color: #1e293b;", "{step.title}" }
                                p { style: "font-size: 13px; color: #94a3b8; margin-top: 4px;", "{step.description}" }
                                if step.parallel {
                                    span { style: "display: inline-block; margin-top: 8px; font-size: 12px; padding: 4px 10px; border-radius: 6px; background: #f5f3ff; color: #7c3aed; font-weight: 500;", "⚡ Runs in parallel" }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
