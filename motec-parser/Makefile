.PHONY: build test clean install-python

# Build Rust library
build:
	cargo build --release

# Build Python bindings
install-python:
	maturin develop --release

# Build for distribution
build-wheel:
	maturin build --release

# Run tests
test:
	cargo test

# Run CLI tool
run:
	cargo run --release -- $(FILE)

# Clean build artifacts
clean:
	cargo clean
	rm -rf target/
	rm -rf *.egg-info/
	rm -rf dist/

# Install Rust (if not installed)
install-rust:
	curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install maturin (if not installed)
install-maturin:
	pip install maturin

# Full setup
setup: install-rust install-maturin build install-python

