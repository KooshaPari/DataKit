use crate::domain::record::Record;
use crate::error::Error;
use crate::port::DataSink;
use std::path::Path;

/// A `DataSink` that writes records as a JSON array to a file.
///
/// Each call to `write` replaces the file content.  If you need to append
/// to an existing file, provide your own writer-based constructor variant.
pub struct JsonSink {
    path: std::path::PathBuf,
}

impl JsonSink {
    /// Create a new `JsonSink` that writes to the given file path.
    pub fn new<P: AsRef<Path>>(path: P) -> Self {
        JsonSink {
            path: path.as_ref().to_path_buf(),
        }
    }

    /// The file path this sink writes to.
    pub fn path(&self) -> &std::path::Path {
        &self.path
    }
}

impl DataSink for JsonSink {
    fn write(&mut self, records: &[Record]) -> Result<(), Error> {
        let json = serde_json::to_string_pretty(records)?;
        std::fs::write(&self.path, json)?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::NamedTempFile;

    #[test]
    fn test_json_sink_writes_array() {
        let f = NamedTempFile::new().unwrap();
        let records = vec![
            Record::from_pairs([("name".into(), "Alice".into())]),
            Record::from_pairs([("name".into(), "Bob".into())]),
        ];

        let mut sink = JsonSink::new(f.path());
        sink.write(&records).unwrap();

        let content = std::fs::read_to_string(f.path()).unwrap();
        let parsed: Vec<Record> = serde_json::from_str(&content).unwrap();
        assert_eq!(parsed.len(), 2);
        assert_eq!(parsed[0].get("name"), Some(&"Alice".into()));
    }

    #[test]
    fn test_json_sink_empty_array() {
        let f = NamedTempFile::new().unwrap();
        let mut sink = JsonSink::new(f.path());
        sink.write(&[]).unwrap();
        let content = std::fs::read_to_string(f.path()).unwrap();
        assert_eq!(content, "[]");
    }

    #[test]
    fn test_json_sink_overwrites() {
        let f = NamedTempFile::new().unwrap();
        let mut sink = JsonSink::new(f.path());

        // First write
        sink.write(&[Record::from_pairs([("k".into(), "v1".into())])])
            .unwrap();

        // Second write — should overwrite
        sink.write(&[Record::from_pairs([("k".into(), "v2".into())])])
            .unwrap();

        let content = std::fs::read_to_string(f.path()).unwrap();
        let parsed: Vec<Record> = serde_json::from_str(&content).unwrap();
        assert_eq!(parsed.len(), 1);
        assert_eq!(parsed[0].get("k"), Some(&"v2".into()));
    }

    #[test]
    fn test_json_sink_path_accessor() {
        let f = NamedTempFile::new().unwrap();
        let sink = JsonSink::new(f.path());
        assert_eq!(sink.path(), f.path());
    }
}
