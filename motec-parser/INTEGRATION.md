# MoTeC Parser Integration Guide

## Overview

The Rust-based MoTeC parser provides high-performance parsing of MoTeC i2 files (LDX and LD formats) with Python bindings for integration with the USC Racing backend.

## Installation

### Prerequisites

1. **Install Rust**:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Install Maturin** (for Python bindings):
   ```bash
   pip install maturin
   ```

### Build

```bash
cd motec-parser
./build.sh
```

Or manually:
```bash
# Build Rust library
cargo build --release

# Build Python bindings
maturin develop --release
```

## Python Integration

### Basic Usage

```python
import motec_parser

# Parse LDX file
with open('workspace.ldx', 'rb') as f:
    data = f.read()
    ldx = motec_parser.parse_ldx(data)
    print(f"Workspace: {ldx.workspace_name}")
    print(f"Channels: {len(ldx.channels)}")

# Parse LD file metadata (fast, header-only)
with open('session.ld', 'rb') as f:
    data = f.read()
    metadata = motec_parser.parse_ld_metadata(data)
    print(f"Channels: {metadata.channel_names}")
    print(f"Samples: {metadata.sample_count}")
```

### Integration with Backend

Update `backend/internal/motec/file_service.py`:

```python
try:
    import motec_parser
    
    def read_ldx_fast(self, path: str):
        """Fast LDX parsing using Rust parser"""
        with open(path, 'rb') as f:
            data = f.read()
            ldx = motec_parser.parse_ldx(data)
            # Convert to MotecLdxModel
            return self._rust_ldx_to_model(ldx)
except ImportError:
    # Fallback to Python XML parser
    pass
```

## Performance Benefits

- **LDX Parsing**: 10-100x faster than Python XML parsing
- **LD Metadata**: Instant header-only parsing (no full file load)
- **Memory**: More efficient for large files
- **Safety**: Memory-safe Rust implementation

## File Format Support

### LDX (XML)
- ✅ Full parsing support
- ✅ Channel definitions
- ✅ Worksheets
- ✅ Metadata

### LD (Binary)
- ✅ Header/metadata parsing
- ✅ Channel name extraction
- ⚠️ Full data parsing (partial - format is proprietary)
- ⚠️ May need refinement based on actual MoTeC files

## Testing

```bash
# Test with sample files
cargo run --release -- workspace.ldx
cargo run --release -- session.ld
```

## Troubleshooting

### Build Issues

1. **Rust not found**: Install via rustup.rs
2. **Maturin not found**: `pip install maturin`
3. **Python version**: Requires Python 3.8+

### Runtime Issues

1. **Import error**: Ensure Python bindings are built (`maturin develop`)
2. **Parse errors**: LD file format may vary - parser may need adjustment

## Future Enhancements

- [ ] Full LD file data parsing (requires format documentation)
- [ ] LDX file writing support
- [ ] Streaming parser for very large LD files
- [ ] Additional MoTeC format support (LDR, etc.)

