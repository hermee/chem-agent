# LNP Desktop App (Dioxus)

Cross-platform desktop application for the Reactome LNP Agent, built with Dioxus 0.6.

## Architecture

- **Framework**: Dioxus with `desktop` feature
- **Platform**: Cross-platform (Linux, macOS, Windows)
- **UI**: Embeds Angular frontend via iframe
- **Backend**: Connects to FastAPI on `localhost:8000`
- **Frontend**: Connects to Angular dev server on `localhost:4200`

## Build

```bash
./build.sh
```

This creates a native binary at `target/release/lnp-desktop`.

## Run

```bash
./target/release/lnp-desktop
```

**Requirements:**
- Backend running on port 8000
- Angular dev server on port 4200

## Testing with Remote Backend (Port Forwarding)

If you're developing on a remote server with VS Code port forwarding:

1. **On remote server**: Start backend and Angular
   ```bash
   ./run.sh  # Starts both on ports 8000 and 4200
   ```

2. **In VS Code**: Forward ports 8000 and 4200 (Ports panel)

3. **On your Mac**: Build and run
   ```bash
   cd standalone-desktop
   ./build.sh
   ./target/release/lnp-desktop
   ```

The app will automatically connect to `localhost:8000` and `localhost:4200` which are forwarded to your remote server.

## Configuration

Edit `src/main.rs` to change the frontend URL:
```rust
const FRONTEND_URL: &str = "http://localhost:4200";  // Default
// const FRONTEND_URL: &str = "http://localhost:8000";  // Backend only
```

## Features

- Native window (1280x820)
- Full Angular app functionality (chat, reactions, workflow)
- Cross-platform support via Dioxus
- Single binary executable

## Comparison with wry Version

| Feature | wry (old) | Dioxus (new) |
|---------|-----------|--------------|
| Framework | wry + tao | Dioxus desktop |
| Assets | Compile-time embedded | Runtime iframe |
| Size | ~8 MB | ~10 MB |
| Complexity | 47 lines | 32 lines |
| Cross-platform | Yes | Yes |
| Hot reload | No | Yes (dev mode) |
