// Python bindings using PyO3
// Allows calling Rust parser from Python

use pyo3::prelude::*;
use pyo3::types::PyBytes;
use crate::ldx::{LdxFile, parse_ldx};
use crate::ld::{LdFile, parse_ld, parse_ld_metadata, LdMetadata};

pub fn register_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<LdxFilePython>()?;
    m.add_class::<LdFilePython>()?;
    m.add_class::<LdMetadataPython>()?;
    m.add_function(wrap_pyfunction!(parse_ldx_py, m)?)?;
    m.add_function(wrap_pyfunction!(parse_ld_py, m)?)?;
    m.add_function(wrap_pyfunction!(parse_ld_metadata_py, m)?)?;
    Ok(())
}

#[pyclass]
pub struct LdxFilePython {
    inner: LdxFile,
}

#[pymethods]
impl LdxFilePython {
    #[new]
    fn new() -> Self {
        LdxFilePython {
            inner: LdxFile {
                workspace_name: String::new(),
                project_name: None,
                car_name: None,
                channels: vec![],
                worksheets: vec![],
                metadata: vec![],
            },
        }
    }

    fn to_dict(&self, py: Python) -> PyResult<PyObject> {
        let json_str = serde_json::to_string(&self.inner)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Serialization error: {}", e)))?;
        
        let json_module = py.import("json")?;
        let dict = json_module.call_method1("loads", (json_str,))?;
        
        Ok(dict.to_object(py))
    }

    #[getter]
    fn workspace_name(&self) -> String {
        self.inner.workspace_name.clone()
    }

    #[getter]
    fn project_name(&self) -> Option<String> {
        self.inner.project_name.clone()
    }

    #[getter]
    fn car_name(&self) -> Option<String> {
        self.inner.car_name.clone()
    }

    #[getter]
    fn channels(&self, py: Python) -> PyResult<Vec<PyObject>> {
        use pyo3::types::PyDict;
        let mut result = Vec::new();
        for ch in &self.inner.channels {
            let dict = PyDict::new(py);
            dict.set_item("name", ch.name.clone())?;
            dict.set_item("units", ch.units.clone().unwrap_or_default())?;
            dict.set_item("source", ch.source.clone().unwrap_or_default())?;
            dict.set_item("scaling", ch.scaling.clone().unwrap_or_default())?;
            dict.set_item("math", ch.math.clone().unwrap_or_default())?;
            result.push(dict.to_object(py));
        }
        Ok(result)
    }
}

#[pyclass]
pub struct LdFilePython {
    inner: LdFile,
}

#[pymethods]
impl LdFilePython {
    fn to_dict(&self, py: Python) -> PyResult<PyObject> {
        let json_str = serde_json::to_string(&self.inner)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Serialization error: {}", e)))?;
        
        let json_module = py.import("json")?;
        let dict = json_module.call_method1("loads", (json_str,))?;
        
        Ok(dict.to_object(py))
    }
}

#[pyclass]
pub struct LdMetadataPython {
    inner: LdMetadata,
}

#[pymethods]
impl LdMetadataPython {
    fn to_dict(&self, py: Python) -> PyResult<PyObject> {
        let json_str = serde_json::to_string(&self.inner)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Serialization error: {}", e)))?;
        
        let json_module = py.import("json")?;
        let dict = json_module.call_method1("loads", (json_str,))?;
        
        Ok(dict.to_object(py))
    }
}

#[pyfunction]
fn parse_ldx_py(data: &PyBytes) -> PyResult<LdxFilePython> {
    let bytes = data.as_bytes();
    let ldx = parse_ldx(bytes)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Parse error: {}", e)))?;
    
    Ok(LdxFilePython { inner: ldx })
}

#[pyfunction]
fn parse_ld_py(data: &PyBytes) -> PyResult<LdFilePython> {
    let bytes = data.as_bytes();
    let ld = parse_ld(bytes)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Parse error: {}", e)))?;
    
    Ok(LdFilePython { inner: ld })
}

#[pyfunction]
fn parse_ld_metadata_py(data: &PyBytes) -> PyResult<LdMetadataPython> {
    let bytes = data.as_bytes();
    let metadata = parse_ld_metadata(bytes)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Parse error: {}", e)))?;
    
    Ok(LdMetadataPython { inner: metadata })
}

