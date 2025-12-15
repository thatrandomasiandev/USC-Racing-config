# MoTeC i2 File Parser (Rust)

High-performance parser for MoTeC i2 file formats written in Rust.

## Features

- **LDX Parser**: Parse MoTeC workspace/configuration files (XML format)
- **LD Parser**: Parse MoTeC logged data files (binary format)
- **Python Bindings**: Use from Python via PyO3
- **Fast**: Rust-native performance for large files
- **Safe**: Memory-safe parsing with proper error handling

## File Formats

### LDX Files (XML)
- MoTeC workspace/configuration files
- Contains channel definitions, worksheets, metadata
- Human-readable XML format

### LD Files (Binary)
- MoTeC logged data files
- Contains time-series telemetry data
- Binary format (proprietary, partially reverse-engineered)

## Usage

### Rust

```rust
use motec_parser::{MotecParser, FileType};

// Detect file type
let file_type = MotecParser::detect_file_type(&data);

match file_type {
    FileType::Ldx => {
        let ldx = MotecParser::parse_ldx(&data)?;
        println!("Workspace: {}", ldx.workspace_name);
    }
    FileType::Ld => {
        let ld = MotecParser::parse_ld(&data)?;
        println!("Samples: {}", ld.header.sample_count);
    }
    FileType::Unknown => {
        eprintln!("Unknown file type");
    }
}
```

### Python

```python
import motec_parser

# Parse LDX file
with open('workspace.ldx', 'rb') as f:
    data = f.read()
    ldx = motec_parser.parse_ldx(data)
    print(f"Workspace: {ldx.workspace_name}")

# Parse LD file metadata (fast, doesn't load full file)
with open('session.ld', 'rb') as f:
    data = f.read()
    metadata = motec_parser.parse_ld_metadata(data)
    print(f"Channels: {metadata.channel_names}")
```

## Building

### Rust Library

```bash
cd motec-parser
cargo build --release
```

### Python Bindings

```bash
cd motec-parser
maturin develop  # For development
maturin build    # For distribution
```

## Integration with USC Racing System

The parser can be integrated with the Python backend:

1. Build Python bindings
2. Import in `backend/internal/motec/file_service.py`
3. Use for faster LDX/LD parsing

## Performance

- **LDX Parsing**: ~10-100x faster than pure Python XML parsing
- **LD Metadata**: Fast header-only parsing without loading full file
- **Memory Efficient**: Streaming parser for large LD files

## Notes

- MoTeC LD file format is proprietary and not fully documented
- Parser implements common patterns found in LD files
- Some edge cases may require additional format research

