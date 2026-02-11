use dioxus::prelude::*;
use crate::api;
use crate::types::*;

#[component]
pub fn MolecularAnalysisPage() -> Element {
    let mut smiles_input = use_signal(String::new);
    let mut result: Signal<Option<AnalysisResult>> = use_signal(|| None);
    let mut error = use_signal(String::new);
    let mut loading = use_signal(|| false);

    let mut run_analysis = move |smi: String| {
        if smi.is_empty() || loading() { return; }
        smiles_input.set(smi.clone());
        loading.set(true); error.set(String::new()); result.set(None);
        spawn(async move {
            match api::fetch_analysis(&smi).await {
                Ok(r) => result.set(Some(r)),
                Err(e) => error.set(e),
            }
            loading.set(false);
        });
    };

    rsx! {
        div { class: "molecular-container",
            h2 { style: "font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 4px;", "🧪 Molecular Analysis" }
            p { style: "font-size: 13px; color: #94a3b8; margin-bottom: 20px;", "RDKit molecular scoring & 2D visualization" }
            div { class: "input-section",
                div { class: "input-row",
                    input { value: "{smiles_input}", placeholder: "Enter SMILES string...", disabled: loading(),
                        oninput: move |e| smiles_input.set(e.value()),
                        onkeypress: move |e: KeyboardEvent| { if e.key() == Key::Enter { let s = smiles_input(); if !s.is_empty() { run_analysis(s); } } },
                    }
                    button { class: "btn-analyze", disabled: loading() || smiles_input().is_empty(),
                        onclick: move |_| { let s = smiles_input(); if !s.is_empty() { run_analysis(s); } }, "Analyze"
                    }
                }
                div { class: "examples",
                    for &(name, smi) in EXAMPLE_MOLECULES {
                        button { class: "example-btn", onclick: move |_| run_analysis(smi.to_string()), "{name}" }
                    }
                }
            }
            if loading() { div { style: "padding: 16px; background: white; border-radius: 12px; border: 1px solid #e2e8f0; color: #64748b; margin-bottom: 16px;", "⏳ Running RDKit analysis..." } }
            if !error().is_empty() { div { style: "padding: 16px; background: #fef2f2; border: 1px solid #fecaca; border-radius: 12px; color: #dc2626; margin-bottom: 16px;", "❌ {error}" } }
            if let Some(ref res) = *result.read() {
                div { class: "results-grid",
                    div { class: "result-card",
                        h3 { "📐 2D Structure" }
                        div { style: "display: flex; justify-content: center; background: #f8fafc; border-radius: 10px; padding: 16px;",
                            div { dangerous_inner_html: "{res.svg}" }
                        }
                        p { style: "margin-top: 12px; font-size: 12px; color: #94a3b8; font-family: monospace; word-break: break-all;", "{res.smiles}" }
                    }
                    div { class: "result-card",
                        h3 { "📊 Molecular Properties" }
                        div { class: "scores-grid",
                            for &(key, label) in SCORE_KEYS {
                                { let val = res.scores.get(key).copied().unwrap_or(0.0);
                                  let cls = score_class(key, val);
                                  let display = fmt_val(val);
                                  rsx! { div { class: "score-item",
                                      div { class: "score-label", "{label}" }
                                      div { class: "score-value {cls}", "{display}" }
                                  }}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
