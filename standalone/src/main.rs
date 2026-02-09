use dioxus::prelude::*;
use serde::Deserialize;
use std::collections::HashMap;

const API_BASE: &str = "http://localhost:8000/api";

#[derive(Debug, Clone, Deserialize)]
struct AnalysisResult {
    smiles: String,
    scores: HashMap<String, f64>,
    svg: String,
}

#[derive(Debug, Clone, Deserialize)]
struct ErrorResult {
    error: Option<String>,
}

const SCORE_KEYS: &[(&str, &str)] = &[
    ("qed", "QED (Drug-likeness)"),
    ("sa_score", "SA Score"),
    ("mol_weight", "Mol. Weight"),
    ("logp", "LogP"),
    ("tpsa", "TPSA (Å²)"),
    ("hba", "H-Bond Acc."),
    ("hbd", "H-Bond Don."),
    ("rotatable_bonds", "Rot. Bonds"),
    ("num_rings", "Rings"),
    ("heavy_atoms", "Heavy Atoms"),
];

const EXAMPLES: &[(&str, &str)] = &[
    ("DLin-MC3-DMA", "CCCCCCCC/C=C\\CCCCCCCC(=O)OCC(CN(C)C)OC(=O)CCCCCCCC/C=C\\CCCCCCCC"),
    ("ALC-0315-like", "CCCCCCCCCCOC(=O)CC(CC(=O)OCCCCCCCCCC)N(C)C"),
    ("SM-102-like", "CCCCCCCCCCOC(=O)CCCN(C)CCCC(=O)OCCCCCCCCCC"),
];

fn score_class(key: &str, val: f64) -> &'static str {
    match key {
        "qed" if val > 0.5 => "score-good",
        "qed" if val > 0.3 => "score-warn",
        "qed" => "score-bad",
        "sa_score" if val < 3.0 => "score-good",
        "sa_score" if val < 5.0 => "score-warn",
        "sa_score" => "score-bad",
        _ => "score-neutral",
    }
}

fn fmt_val(val: f64) -> String {
    if val.fract() == 0.0 && val.abs() < 1e6 {
        format!("{}", val as i64)
    } else {
        format!("{:.2}", val)
    }
}

async fn fetch_analysis(smiles: String) -> Result<AnalysisResult, String> {
    let client = reqwest::Client::new();
    let resp = client
        .post(format!("{API_BASE}/analyze-smiles"))
        .json(&serde_json::json!({ "smiles": smiles }))
        .send()
        .await
        .map_err(|e| format!("Request failed: {e}"))?;
    let text = resp.text().await.map_err(|e| format!("Read failed: {e}"))?;
    if let Ok(err) = serde_json::from_str::<ErrorResult>(&text) {
        if let Some(e) = err.error {
            return Err(e);
        }
    }
    serde_json::from_str::<AnalysisResult>(&text).map_err(|e| format!("Parse failed: {e}"))
}

fn main() {
    dioxus::launch(App);
}

#[component]
fn App() -> Element {
    let mut smiles_input = use_signal(|| String::new());
    let mut result: Signal<Option<AnalysisResult>> = use_signal(|| None);
    let mut error = use_signal(|| String::new());
    let mut loading = use_signal(|| false);

    let mut run_analysis = move |smi: String| {
        smiles_input.set(smi.clone());
        loading.set(true);
        error.set(String::new());
        result.set(None);
        spawn(async move {
            match fetch_analysis(smi).await {
                Ok(r) => result.set(Some(r)),
                Err(e) => error.set(e),
            }
            loading.set(false);
        });
    };

    rsx! {
        div { class: "app",
            div { class: "header",
                h1 { "🤖 AI-LNP Agent" }
                p { "Analyze ionizable lipid candidates — RDKit molecular scoring & visualization" }
            }
            div { class: "content",
                div { class: "input-row",
                    input {
                        value: "{smiles_input}",
                        placeholder: "Enter SMILES string...",
                        disabled: loading(),
                        oninput: move |e| smiles_input.set(e.value()),
                        onkeypress: move |e: KeyboardEvent| {
                            if e.key() == Key::Enter {
                                let s = smiles_input();
                                if !s.is_empty() { run_analysis(s); }
                            }
                        },
                    }
                    button {
                        class: "btn btn-primary",
                        disabled: loading() || smiles_input().is_empty(),
                        onclick: move |_| {
                            let s = smiles_input();
                            if !s.is_empty() { run_analysis(s); }
                        },
                        "Analyze"
                    }
                }
                div { class: "examples",
                    span { "Try: " }
                    for &(name, smi) in EXAMPLES {
                        button {
                            class: "example-btn",
                            onclick: move |_| run_analysis(smi.to_string()),
                            "{name}"
                        }
                    }
                }

                if loading() {
                    div { class: "loading", "⏳ Running RDKit analysis..." }
                }
                if !error().is_empty() {
                    div { class: "error-msg", "❌ {error}" }
                }
                if let Some(ref res) = *result.read() {
                    div { class: "results",
                        div { class: "card",
                            h3 { "📐 2D Structure" }
                            div { class: "svg-container", dangerous_inner_html: "{res.svg}" }
                            p { class: "smiles-text", "{res.smiles}" }
                        }
                        div { class: "card",
                            h3 { "📊 Molecular Properties" }
                            div { class: "scores-grid",
                                for &(key, label) in SCORE_KEYS {
                                    {
                                        let val = res.scores.get(key).copied().unwrap_or(0.0);
                                        let cls = score_class(key, val);
                                        let display = fmt_val(val);
                                        rsx! {
                                            div { class: "score-card",
                                                div { class: "label", "{label}" }
                                                div { class: "value {cls}", "{display}" }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
