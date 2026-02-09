#!/bin/bash
# Build the standalone desktop app
# Run this on macOS (requires Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh)
set -e
cd "$(dirname "$0")"
echo "🔨 Building LNP Desktop App..."
cargo build --release
echo ""
echo "✅ Binary ready at: target/release/lnp-desktop"
echo "   Run with: ./target/release/lnp-desktop"
echo ""
echo "⚠️  Make sure the backend is running on localhost:8000"
