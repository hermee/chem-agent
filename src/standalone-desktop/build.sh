#!/bin/bash
# Build the standalone desktop app with Dioxus
set -e
cd "$(dirname "$0")"

echo "🔨 Building LNP Desktop App (Dioxus native)..."
cargo build --release

echo ""
echo "✅ Binary ready at: target/release/lnp-desktop"
echo "   Run with: ./target/release/lnp-desktop"
echo ""
echo "⚠️  Requires: Backend running on localhost:8000"
