// MoTeC i2 File Format Parser
// Supports LDX (XML) and LD (binary) file formats

pub mod ldx;
pub mod ld;
pub mod error;

#[cfg(feature = "python")]
mod python_bindings;

pub use error::{MotecError, Result};

#[cfg(feature = "python")]
use pyo3::prelude::*;

#[cfg(feature = "python")]
#[pymodule]
fn motec_parser(_py: Python, m: &PyModule) -> PyResult<()> {
    python_bindings::register_module(_py, m)?;
    Ok(())
}

/// Main entry point for parsing MoTeC files
pub struct MotecParser;

impl MotecParser {
    /// Parse an LDX file (XML format)
    pub fn parse_ldx(data: &[u8]) -> Result<ldx::LdxFile> {
        ldx::parse_ldx(data)
    }

    /// Parse an LD file (binary format)
    pub fn parse_ld(data: &[u8]) -> Result<ld::LdFile> {
        ld::parse_ld(data)
    }

    /// Detect file type from data
    pub fn detect_file_type(data: &[u8]) -> FileType {
        if data.len() < 4 {
            return FileType::Unknown;
        }

        // LDX files start with XML declaration or <
        if data.starts_with(b"<?xml") || data.starts_with(b"<") {
            return FileType::Ldx;
        }

        // LD files have a specific binary header
        // MoTeC LD files typically start with specific magic bytes
        // This is a simplified detection - may need refinement
        if data.len() > 512 {
            // Check for LD file signature patterns
            // MoTeC LD files often have metadata in first 512 bytes
            return FileType::Ld;
        }

        FileType::Unknown
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum FileType {
    Ldx,
    Ld,
    Unknown,
}

