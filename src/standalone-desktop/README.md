# LNP Desktop App (Dioxus)

Cross-platform native desktop application for the Reactome LNP Agent, built with Dioxus 0.6.

## Architecture

- **Framework**: Dioxus with `desktop` feature (native GUI, not iframe/wry)
- **Platform**: Cross-platform (Linux, macOS, Windows)
- **UI**: Same Dioxus components as `src/standalone/` (WASM version)
- **Backend**: Connects to FastAPI on `localhost:8000`
- **Storage**: Local filesystem (`~/.local/share/lnp-desktop/conversations.json`)

## Build

```bash
./build.sh
```

Creates a native binary at `target/release/lnp-desktop`.

## Run

```bash
./target/release/lnp-desktop
```

**Requires:** Backend running on port 8000.

## Differences from standalone (WASM)

| Feature | standalone (WASM) | standalone-desktop (native) |
|---------|-------------------|----------------------------|
| Dioxus feature | `web` | `desktop` |
| Storage | localStorage | Filesystem (~/.local/share) |
| Timestamps | js_sys::Date | std::time::SystemTime |
| Served via | Trunk + Python HTTP | Native binary |
| Dependencies | wasm-bindgen, web-sys | dirs |

Both apps share identical UI components (pages, layout, styling).
