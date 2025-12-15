use thiserror::Error;

#[derive(Error, Debug)]
pub enum MotecError {
    #[error("XML parsing error: {0}")]
    XmlParse(String),

    #[error("Binary parsing error: {0}")]
    BinaryParse(String),

    #[error("Invalid file format: {0}")]
    InvalidFormat(String),

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("UTF-8 encoding error: {0}")]
    Utf8(#[from] std::str::Utf8Error),

    #[error("Missing required field: {0}")]
    MissingField(String),

    #[error("Invalid data: {0}")]
    InvalidData(String),
}

pub type Result<T> = std::result::Result<T, MotecError>;

