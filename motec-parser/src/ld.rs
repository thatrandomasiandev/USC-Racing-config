// LD File Parser (Binary format)
// MoTeC i2 logged data files

use byteorder::{LittleEndian, ReadBytesExt};
use nom::IResult;
use serde::{Deserialize, Serialize};
use std::io::{Cursor, Read};
use crate::error::{MotecError, Result};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LdFile {
    pub header: LdHeader,
    pub channels: Vec<LdChannel>,
    pub samples: Vec<LdSample>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LdHeader {
    pub version: u32,
    pub sample_count: u32,
    pub sample_rate: f32,
    pub start_time: Option<String>,
    pub channel_count: u16,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LdChannel {
    pub name: String,
    pub units: String,
    pub data_type: String,
    pub index: u16,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LdSample {
    pub timestamp: f64,
    pub values: Vec<f64>,
}

/// Parse LD file from binary data
/// 
/// Note: MoTeC LD file format is proprietary and not fully documented.
/// This parser implements common patterns found in LD files.
pub fn parse_ld(data: &[u8]) -> Result<LdFile> {
    if data.len() < 512 {
        return Err(MotecError::InvalidFormat(
            "LD file too small (minimum 512 bytes header)".to_string()
        ));
    }

    let mut cursor = Cursor::new(data);
    
    // Read header (first 512 bytes typically contain metadata)
    let header = parse_ld_header(&mut cursor)?;
    
    // Parse channel definitions
    let channels = parse_ld_channels(&mut cursor, header.channel_count)?;
    
    // Parse sample data
    let samples = parse_ld_samples(&mut cursor, header.sample_count, channels.len())?;

    Ok(LdFile {
        header,
        channels,
        samples,
    })
}

fn parse_ld_header(cursor: &mut Cursor<&[u8]>) -> Result<LdHeader> {
    // MoTeC LD header structure (simplified)
    // Actual format may vary by version
    
    cursor.set_position(0);
    
    // Read version (typically at offset 0)
    let version = cursor.read_u32::<LittleEndian>()
        .map_err(|e| MotecError::BinaryParse(format!("Failed to read version: {}", e)))?;
    
    // Read sample count (offset varies by version)
    cursor.set_position(4);
    let sample_count = cursor.read_u32::<LittleEndian>()
        .map_err(|e| MotecError::BinaryParse(format!("Failed to read sample count: {}", e)))?;
    
    // Read sample rate (offset varies)
    cursor.set_position(8);
    let sample_rate = cursor.read_f32::<LittleEndian>()
        .map_err(|e| MotecError::BinaryParse(format!("Failed to read sample rate: {}", e)))?;
    
    // Read channel count
    cursor.set_position(16);
    let channel_count = cursor.read_u16::<LittleEndian>()
        .map_err(|e| MotecError::BinaryParse(format!("Failed to read channel count: {}", e)))?;

    Ok(LdHeader {
        version,
        sample_count,
        sample_rate,
        start_time: None, // Would need to parse timestamp from header
        channel_count,
    })
}

fn parse_ld_channels(cursor: &mut Cursor<&[u8]>, count: u16) -> Result<Vec<LdChannel>> {
    let mut channels = Vec::new();
    
    // Channel definitions typically start after header (offset 512+)
    cursor.set_position(512);
    
    for i in 0..count {
        // Channel name (typically null-terminated string, max 32-64 bytes)
        let mut name_bytes = vec![0u8; 64];
        cursor.read_exact(&mut name_bytes)
            .map_err(|e| MotecError::BinaryParse(format!("Failed to read channel {} name: {}", i, e)))?;
        
        let name = name_bytes.iter()
            .position(|&b| b == 0)
            .map(|pos| String::from_utf8_lossy(&name_bytes[..pos]).to_string())
            .unwrap_or_else(|| String::from_utf8_lossy(&name_bytes).to_string());
        
        // Units (similar structure)
        let mut units_bytes = vec![0u8; 32];
        cursor.read_exact(&mut units_bytes)
            .map_err(|e| MotecError::BinaryParse(format!("Failed to read channel {} units: {}", i, e)))?;
        
        let units = units_bytes.iter()
            .position(|&b| b == 0)
            .map(|pos| String::from_utf8_lossy(&units_bytes[..pos]).to_string())
            .unwrap_or_else(|| String::from_utf8_lossy(&units_bytes).to_string());
        
        channels.push(LdChannel {
            name: name.trim().to_string(),
            units: units.trim().to_string(),
            data_type: "f64".to_string(), // Most MoTeC channels are float64
            index: i,
        });
    }
    
    Ok(channels)
}

fn parse_ld_samples(
    cursor: &mut Cursor<&[u8]>,
    sample_count: u32,
    channel_count: usize,
) -> Result<Vec<LdSample>> {
    let mut samples = Vec::new();
    
    // Sample data typically starts after channel definitions
    // Each sample contains values for all channels
    
    // Limit parsing to prevent memory issues with large files
    let max_samples = sample_count.min(10000); // Parse first 10k samples
    
    for i in 0..max_samples {
        // Read timestamp (typically f64)
        let timestamp = cursor.read_f64::<LittleEndian>()
            .map_err(|e| MotecError::BinaryParse(format!("Failed to read sample {} timestamp: {}", i, e)))?;
        
        // Read values for each channel
        let mut values = Vec::new();
        for _ in 0..channel_count {
            let value = cursor.read_f64::<LittleEndian>()
                .map_err(|e| MotecError::BinaryParse(format!("Failed to read sample {} value: {}", i, e)))?;
            values.push(value);
        }
        
        samples.push(LdSample {
            timestamp,
            values,
        });
    }
    
    Ok(samples)
}

/// Extract metadata from LD file without parsing full data
pub fn parse_ld_metadata(data: &[u8]) -> Result<LdMetadata> {
    if data.len() < 512 {
        return Err(MotecError::InvalidFormat(
            "LD file too small for metadata extraction".to_string()
        ));
    }

    let mut cursor = Cursor::new(&data[..512]);
    let header = parse_ld_header(&mut cursor)?;
    
    // Parse channel names from header area
    let channels = parse_ld_channels(&mut cursor, header.channel_count)?;
    
    Ok(LdMetadata {
        file_size: data.len() as u64,
        version: header.version,
        sample_count: header.sample_count,
        sample_rate: header.sample_rate,
        channel_count: header.channel_count,
        channel_names: channels.iter().map(|c| c.name.clone()).collect(),
        valid: true,
    })
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LdMetadata {
    pub file_size: u64,
    pub version: u32,
    pub sample_count: u32,
    pub sample_rate: f32,
    pub channel_count: u16,
    pub channel_names: Vec<String>,
    pub valid: bool,
}

