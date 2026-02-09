#!/bin/bash
# Build the standalone desktop app with Dioxus
# Run this on macOS/Linux/Windows (requires Rust)
set -e
cd "$(dirname "$0")"

echo "🔨 Building LNP Desktop App (Dioxus cross-platform)..."
cargo build --release

echo ""
echo "✅ Binary ready at: target/release/lnp-desktop"
echo "   Run with: ./target/release/lnp-desktop"
echo ""
echo "⚠️  Requirements:"
echo "   - Backend running on localhost:8000"
echo "   - Angular dev server on localhost:4200"
