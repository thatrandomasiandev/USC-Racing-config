#!/bin/bash
# Build script for MoTeC Parser

set -e

echo "🔨 Building MoTeC Parser..."

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo "❌ Rust/Cargo not found. Please install Rust: https://rustup.rs/"
    exit 1
fi

# Build Rust library
echo "📦 Building Rust library..."
cargo build --release

# Check if maturin is installed (for Python bindings)
if command -v maturin &> /dev/null; then
    echo "🐍 Building Python bindings..."
    maturin develop --release
    echo "✅ Python bindings built successfully"
else
    echo "⚠️  Maturin not found. Python bindings not built."
    echo "   Install with: pip install maturin"
fi

echo "✅ Build complete!"
echo ""
echo "Library location: target/release/libmotec_parser.*"

