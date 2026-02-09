use dioxus::prelude::*;

// Change this to match your setup:
// - "http://localhost:4200" for forwarded Angular dev server
// - "http://localhost:8000" for backend-only (no Angular UI)
const FRONTEND_URL: &str = "http://localhost:4200";

fn main() {
    LaunchBuilder::desktop()
        .with_cfg(dioxus::desktop::Config::new()
            .with_window(dioxus::desktop::WindowBuilder::new()
                .with_title("🧬 Reactome LNP Agent")
                .with_inner_size(dioxus::desktop::LogicalSize::new(1280.0, 820.0))))
        .launch(App);
}

#[component]
fn App() -> Element {
    rsx! {
        style { {include_str!("../assets/app.css")} }
        div {
            class: "app-container",
            iframe {
                src: FRONTEND_URL,
                width: "100%",
                height: "100%",
                style: "border: none; display: block;",
                title: "Reactome LNP Agent"
            }
        }
    }
}
