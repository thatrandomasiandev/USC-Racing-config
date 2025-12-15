// CLI tool for testing MoTeC parser
use motec_parser::{MotecParser, FileType};
use std::fs;
use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {
        eprintln!("Usage: motec-parser <file.ldx|file.ld>");
        std::process::exit(1);
    }
    
    let file_path = &args[1];
    let data = fs::read(file_path)
        .expect("Failed to read file");
    
    match MotecParser::detect_file_type(&data) {
        FileType::Ldx => {
            println!("Detected: LDX file");
            match MotecParser::parse_ldx(&data) {
                Ok(ldx) => {
                    println!("Workspace: {}", ldx.workspace_name);
                    println!("Project: {:?}", ldx.project_name);
                    println!("Car: {:?}", ldx.car_name);
                    println!("Channels: {}", ldx.channels.len());
                    for ch in &ldx.channels {
                        println!("  - {} ({})", ch.name, ch.units.as_deref().unwrap_or(""));
                    }
                }
                Err(e) => {
                    eprintln!("Parse error: {}", e);
                    std::process::exit(1);
                }
            }
        }
        FileType::Ld => {
            println!("Detected: LD file");
            match MotecParser::parse_ld(&data) {
                Ok(ld) => {
                    println!("Samples: {}", ld.header.sample_count);
                    println!("Sample Rate: {} Hz", ld.header.sample_rate);
                    println!("Channels: {}", ld.channels.len());
                    for ch in &ld.channels {
                        println!("  - {} ({})", ch.name, ch.units);
                    }
                }
                Err(e) => {
                    eprintln!("Parse error: {}", e);
                    std::process::exit(1);
                }
            }
        }
        FileType::Unknown => {
            eprintln!("Unknown file type");
            std::process::exit(1);
        }
    }
}

