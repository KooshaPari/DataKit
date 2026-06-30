use crate::domain::record::Record;
use crate::error::Error;
use crate::port::DataSource;
use std::path::Path;

/// A `DataSource` that reads records from a CSV file.
///
/// The first row of the CSV is treated as headers and becomes the field keys
/// of each `Record`.  Every subsequent row becomes one record.
///
/// # Example
///
/// ```csv
/// name,age
/// Alice,30
/// Bob,25
/// ```
///
/// produces two records: `{name: "Alice", age: "30"}` and
/// `{name: "Bob", age: "25"}`.
pub struct CsvSource {
    path: std::path::PathBuf,
}

impl CsvSource {
    /// Create a new `CsvSource` that reads from the given file path.
    pub fn new<P: AsRef<Path>>(path: P) -> Self {
        CsvSource {
            path: path.as_ref().to_path_buf(),
        }
    }

    /// The file path this source reads from.
    pub fn path(&self) -> &std::path::Path {
        &self.path
    }
}

impl DataSource for CsvSource {
    fn read(&mut self) -> Result<Vec<Record>, Error> {
        let mut reader = csv::ReaderBuilder::new()
            .flexible(true)
            .from_path(&self.path)?;

        let headers: Vec<String> = reader
            .headers()?
            .iter()
            .map(|h| h.to_string())
            .collect();

        let records: Result<Vec<Record>, Error> = reader
            .records()
            .map(|row_result| {
                let row = row_result?;
                let fields: Vec<(String, String)> = headers
                    .iter()
                    .zip(row.iter())
                    .map(|(h, v)| (h.clone(), v.to_string()))
                    .collect();
                Ok(Record::from_pairs(fields))
            })
            .collect();

        records
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    fn write_csv(lines: &[&str]) -> NamedTempFile {
        let mut f = NamedTempFile::new().unwrap();
        for line in lines {
            writeln!(f, "{line}").unwrap();
        }
        f
    }

    #[test]
    fn test_csv_source_reads_basic_csv() {
        let f = write_csv(&["name,age", "Alice,30", "Bob,25"]);
        let mut source = CsvSource::new(f.path());
        let records = source.read().unwrap();
        assert_eq!(records.len(), 2);
        assert_eq!(records[0].get("name"), Some(&"Alice".to_string()));
        assert_eq!(records[0].get("age"), Some(&"30".to_string()));
        assert_eq!(records[1].get("name"), Some(&"Bob".to_string()));
    }

    #[test]
    fn test_csv_source_single_column() {
        let f = write_csv(&["value", "hello", "world"]);
        let mut source = CsvSource::new(f.path());
        let records = source.read().unwrap();
        assert_eq!(records.len(), 2);
        assert_eq!(records[0].get("value"), Some(&"hello".to_string()));
        assert_eq!(records[1].get("value"), Some(&"world".to_string()));
    }

    #[test]
    fn test_csv_source_empty_rows() {
        let f = write_csv(&["a,b", "1,2", "", "3,4"]);
        let mut source = CsvSource::new(f.path());
        let records = source.read().unwrap();
        // flexible = true allows empty rows; they produce records with empty values
        assert!(records.len() >= 2);
    }

    #[test]
    fn test_csv_source_headers_only() {
        let f = write_csv(&["name"]);
        let mut source = CsvSource::new(f.path());
        let records = source.read().unwrap();
        assert!(records.is_empty());
    }

    #[test]
    fn test_csv_source_path_accessor() {
        let f = NamedTempFile::new().unwrap();
        let source = CsvSource::new(f.path());
        assert_eq!(source.path(), f.path());
    }

    #[test]
    fn test_csv_source_file_not_found() {
        let mut source = CsvSource::new("/tmp/nonexistent_csv_12345.csv");
        let result = source.read();
        assert!(result.is_err());
    }
}
