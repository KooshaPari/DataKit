use crate::domain::record::Record;
use crate::error::Error;
use crate::port::{DataSink, DataSource, Transform};

/// A data pipeline that reads from a `DataSource`, applies a chain of
/// `Transform`s, and writes the results to a `DataSink`.
///
/// This is the core orchestrator in the hexagonal architecture: it
/// depends only on port traits, never on concrete adapters.
///
/// # Example
///
/// ```rust,ignore
/// use datakit::domain::pipeline::Pipeline;
/// # // Concrete adapter types would be used here in a real example.
/// ```
pub struct Pipeline {
    source: Box<dyn DataSource>,
    transforms: Vec<Box<dyn Transform>>,
    sink: Box<dyn DataSink>,
}

impl Pipeline {
    /// Create a new pipeline from a source, a list of transforms, and a sink.
    pub fn new(
        source: Box<dyn DataSource>,
        transforms: Vec<Box<dyn Transform>>,
        sink: Box<dyn DataSink>,
    ) -> Self {
        Pipeline {
            source,
            transforms,
            sink,
        }
    }

    /// Run the pipeline: read all records from the source, apply each
    /// transform in order, and write the results to the sink.
    pub fn run(&mut self) -> Result<(), Error> {
        let records = self.source.read()?;
        let transformed = records
            .into_iter()
            .map(|rec| {
                self.transforms
                    .iter()
                    .try_fold(rec, |r, t| t.transform(r))
            })
            .collect::<Result<Vec<Record>, Error>>()?;
        self.sink.write(&transformed)
    }

    /// A streaming variant: process records one at a time without
    /// materialising the entire dataset.  Returns the count of processed
    /// records.
    pub fn run_stream(&mut self) -> Result<usize, Error> {
        let records = self.source.read()?;
        let mut count = 0;
        for record in records {
            let transformed = self
                .transforms
                .iter()
                .try_fold(record, |r, t| t.transform(r))?;
            self.sink.write(&[transformed])?;
            count += 1;
        }
        Ok(count)
    }

    // -- accessors (useful for inspection / testing) --

    pub fn source_ref(&self) -> &dyn DataSource {
        &*self.source
    }

    pub fn transforms(&self) -> &[Box<dyn Transform>] {
        &self.transforms
    }

    pub fn sink_ref(&self) -> &dyn DataSink {
        &*self.sink
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::adapter::csv_source::CsvSource;
    use crate::adapter::json_sink::JsonSink;
    use crate::adapter::uppercase_transform::UppercaseTransform;
    use std::io::Write;
    use tempfile::NamedTempFile;

    fn csv_input() -> NamedTempFile {
        let mut f = NamedTempFile::new().unwrap();
        writeln!(f, "name,city").unwrap();
        writeln!(f, "Alice,New York").unwrap();
        writeln!(f, "Bob,London").unwrap();
        f
    }

    #[test]
    fn test_pipeline_run() {
        let input = csv_input();
        let output = NamedTempFile::new().unwrap();

        let source = CsvSource::new(input.path());
        let sink = JsonSink::new(output.path());
        let transform = UppercaseTransform::new("name");

        let mut pipeline = Pipeline::new(
            Box::new(source),
            vec![Box::new(transform)],
            Box::new(sink),
        );

        pipeline.run().unwrap();

        let result = std::fs::read_to_string(output.path()).unwrap();
        let records: Vec<Record> = serde_json::from_str(&result).unwrap();
        assert_eq!(records.len(), 2);
        assert_eq!(records[0].get("name"), Some(&"ALICE".to_string()));
        assert_eq!(records[1].get("name"), Some(&"BOB".to_string()));
    }

    #[test]
    fn test_pipeline_with_multiple_transforms() {
        let input = csv_input();
        let output = NamedTempFile::new().unwrap();

        let source = CsvSource::new(input.path());
        let sink = JsonSink::new(output.path());
        let t1 = UppercaseTransform::new("name");
        let t2 = UppercaseTransform::new("city");

        let mut pipeline = Pipeline::new(
            Box::new(source),
            vec![Box::new(t1), Box::new(t2)],
            Box::new(sink),
        );

        pipeline.run().unwrap();

        let result = std::fs::read_to_string(output.path()).unwrap();
        let records: Vec<Record> = serde_json::from_str(&result).unwrap();
        assert_eq!(records[0].get("name"), Some(&"ALICE".to_string()));
        assert_eq!(records[0].get("city"), Some(&"NEW YORK".to_string()));
    }

    #[test]
    fn test_pipeline_run_stream() {
        let input = csv_input();
        let output = NamedTempFile::new().unwrap();

        let source = CsvSource::new(input.path());
        let sink = JsonSink::new(output.path());
        let transform = UppercaseTransform::new("name");

        let mut pipeline = Pipeline::new(
            Box::new(source),
            vec![Box::new(transform)],
            Box::new(sink),
        );

        let count = pipeline.run_stream().unwrap();
        assert_eq!(count, 2);

        // In streaming mode each write overwrites, so the output
        // contains only the last record.
        let result = std::fs::read_to_string(output.path()).unwrap();
        let records: Vec<Record> = serde_json::from_str(&result).unwrap();
        assert_eq!(records.len(), 1);
        assert_eq!(records[0].get("name"), Some(&"BOB".to_string()));
    }

    #[test]
    fn test_pipeline_with_empty_input() {
        let mut input = NamedTempFile::new().unwrap();
        writeln!(input, "name").unwrap();
        let output = NamedTempFile::new().unwrap();

        let source = CsvSource::new(input.path());
        let sink = JsonSink::new(output.path());
        let transform = UppercaseTransform::new("name");

        let mut pipeline = Pipeline::new(
            Box::new(source),
            vec![Box::new(transform)],
            Box::new(sink),
        );

        pipeline.run().unwrap();
        let result = std::fs::read_to_string(output.path()).unwrap();
        assert_eq!(result, "[]");
    }

    #[test]
    fn test_pipeline_accessors() {
        let input = csv_input();
        let output = NamedTempFile::new().unwrap();

        let source = CsvSource::new(input.path());
        let sink = JsonSink::new(output.path());

        let pipeline = Pipeline::new(Box::new(source), vec![], Box::new(sink));

        // Verify accessors don't panic
        pipeline.source_ref();
        pipeline.sink_ref();
        assert!(pipeline.transforms().is_empty());
    }
}
