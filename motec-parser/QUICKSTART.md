# MoTeC Parser Quick Start

## Installation

### 1. Install Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### 2. Build Parser

```bash
cd motec-parser
cargo build --release
```

### 3. Build Python Bindings (Optional)

```bash
pip install maturin
maturin develop --release
```

## Usage

### Command Line

```bash
# Parse LDX file
cargo run --release -- workspace.ldx

# Parse LD file
cargo run --release -- session.ld
```

### Python

```python
import motec_parser

# Parse LDX
with open('file.ldx', 'rb') as f:
    ldx = motec_parser.parse_ldx(f.read())
    print(ldx.workspace_name)

# Parse LD metadata (fast)
with open('file.ld', 'rb') as f:
    metadata = motec_parser.parse_ld_metadata(f.read())
    print(metadata.channel_names)
```

## Integration

The parser automatically integrates with the Python backend:
- If Rust parser is available, it's used (faster)
- If not available, falls back to Python XML parser
- No code changes needed - transparent fallback

## Performance

- **LDX**: 10-100x faster than Python XML
- **LD Metadata**: Instant (header-only parsing)
- **Memory**: More efficient for large files

