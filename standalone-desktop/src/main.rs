use tao::event::{Event, WindowEvent};
use tao::event_loop::{ControlFlow, EventLoop};
use tao::window::WindowBuilder;
use wry::WebViewBuilder;

// Embed Angular production build at compile time
const INDEX_HTML: &str = include_str!("../frontend/index.html");
const MAIN_JS: &[u8] = include_bytes!("../frontend/main-6DZF6I72.js");
const STYLES_CSS: &[u8] = include_bytes!("../frontend/styles-CLL64EGK.css");
const FAVICON: &[u8] = include_bytes!("../frontend/favicon.ico");

fn main() {
    let event_loop = EventLoop::new();
    let window = WindowBuilder::new()
        .with_title("🧬 Reactome LNP Agent")
        .with_inner_size(tao::dpi::LogicalSize::new(1280.0, 820.0))
        .build(&event_loop)
        .unwrap();

    let _webview = WebViewBuilder::new()
        .with_custom_protocol("app".into(), move |request| {
            let path = request.uri().path();
            let (body, mime) = match path {
                "/" | "/index.html" => (INDEX_HTML.as_bytes().to_vec(), "text/html"),
                p if p.ends_with(".js") => (MAIN_JS.to_vec(), "application/javascript"),
                p if p.ends_with(".css") => (STYLES_CSS.to_vec(), "text/css"),
                "/favicon.ico" => (FAVICON.to_vec(), "image/x-icon"),
                // SPA fallback — serve index.html for Angular routes
                _ => (INDEX_HTML.as_bytes().to_vec(), "text/html"),
            };
            wry::http::Response::builder()
                .header("Content-Type", mime)
                .header("Access-Control-Allow-Origin", "*")
                .body(body.into())
                .unwrap()
        })
        .with_url("app://localhost/")
        .build(&window)
        .unwrap();

    event_loop.run(move |event, _, control_flow| {
        *control_flow = ControlFlow::Wait;
        if let Event::WindowEvent { event: WindowEvent::CloseRequested, .. } = event {
            *control_flow = ControlFlow::Exit;
        }
    });
}
