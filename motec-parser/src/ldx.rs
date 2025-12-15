// LDX File Parser (XML format)
// MoTeC i2 workspace/configuration files

use quick_xml::de::from_str;
use serde::{Deserialize, Serialize};
use crate::error::{MotecError, Result};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LdxFile {
    pub workspace_name: String,
    pub project_name: Option<String>,
    pub car_name: Option<String>,
    pub channels: Vec<Channel>,
    pub worksheets: Vec<Worksheet>,
    pub metadata: Vec<MetadataItem>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Channel {
    #[serde(rename = "@Name")]
    pub name: String,
    
    #[serde(rename = "@Units")]
    pub units: Option<String>,
    
    #[serde(rename = "@Source")]
    pub source: Option<String>,
    
    #[serde(rename = "@Scaling")]
    pub scaling: Option<String>,
    
    #[serde(rename = "Math")]
    pub math: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Worksheet {
    #[serde(rename = "@Name")]
    pub name: String,
    
    #[serde(rename = "@Type")]
    pub worksheet_type: Option<String>,
    
    #[serde(rename = "ChannelRef")]
    pub channel_refs: Vec<ChannelRef>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChannelRef {
    #[serde(rename = "@Name")]
    pub name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetadataItem {
    #[serde(rename = "@Key")]
    pub key: String,
    
    #[serde(rename = "@Value")]
    pub value: String,
}

/// Parse LDX file from XML bytes
pub fn parse_ldx(data: &[u8]) -> Result<LdxFile> {
    let xml_str = std::str::from_utf8(data)
        .map_err(|e| MotecError::Utf8(e))?;

    // MoTeC LDX files use a Workspace root element
    // We need to handle the XML structure properly
    let ldx: LdxWorkspace = from_str(xml_str)
        .map_err(|e| MotecError::XmlParse(e.to_string()))?;

    Ok(ldx.into())
}

#[derive(Debug, Deserialize)]
#[serde(rename = "Workspace")]
struct LdxWorkspace {
    #[serde(rename = "@Name")]
    workspace_name: Option<String>,
    
    #[serde(rename = "@Project")]
    project_name: Option<String>,
    
    #[serde(rename = "@Car")]
    car_name: Option<String>,
    
    #[serde(rename = "Channels")]
    channels: Option<ChannelsContainer>,
    
    #[serde(rename = "Worksheets")]
    worksheets: Option<WorksheetsContainer>,
    
    #[serde(rename = "Metadata")]
    metadata: Option<MetadataContainer>,
}

#[derive(Debug, Deserialize)]
struct ChannelsContainer {
    #[serde(rename = "Channel")]
    channels: Vec<Channel>,
}

#[derive(Debug, Deserialize)]
struct WorksheetsContainer {
    #[serde(rename = "Worksheet")]
    worksheets: Vec<Worksheet>,
}

#[derive(Debug, Deserialize)]
struct MetadataContainer {
    #[serde(rename = "Item")]
    items: Vec<MetadataItem>,
}

impl From<LdxWorkspace> for LdxFile {
    fn from(ws: LdxWorkspace) -> Self {
        LdxFile {
            workspace_name: ws.workspace_name.unwrap_or_else(|| "Default".to_string()),
            project_name: ws.project_name,
            car_name: ws.car_name,
            channels: ws.channels.map(|c| c.channels).unwrap_or_default(),
            worksheets: ws.worksheets.map(|w| w.worksheets).unwrap_or_default(),
            metadata: ws.metadata.map(|m| m.items).unwrap_or_default(),
        }
    }
}

/// Write LDX file to XML bytes
pub fn write_ldx(ldx: &LdxFile) -> Result<Vec<u8>> {
    let xml = quick_xml::se::to_string(ldx)
        .map_err(|e| MotecError::XmlParse(e.to_string()))?;
    
    Ok(xml.into_bytes())
}

