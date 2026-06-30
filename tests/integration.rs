// Integration tests for the DataKit ETL pipeline.
//
// These tests exercise a full source → transform → sink flow using the
// public API.  They depend only on the crate's public interface.

use datakit::adapter::csv_source::CsvSource;
use datakit::adapter::json_sink::JsonSink;
use datakit::adapter::uppercase_transform::UppercaseTransform;
use datakit::domain::pipeline::Pipeline;
use datakit::Record;
use std::io::Write;
use tempfile::NamedTempFile;

fn create_test_csv(lines: &[&str]) -> NamedTempFile {
    let mut f = NamedTempFile::new().unwrap();
    for line in lines {
        writeln!(f, "{line}").unwrap();
    }
    f
}

#[test]
fn integration_full_etl_pipeline() {
    let input = create_test_csv(&["name,age,city", "Alice,30,New York", "Bob,25,London"]);
    let output = NamedTempFile::new().unwrap();

    let source = CsvSource::new(input.path());
    let sink = JsonSink::new(output.path());
    let upper_name = UppercaseTransform::new("name");
    let upper_city = UppercaseTransform::new("city");

    let mut pipeline = Pipeline::new(
        Box::new(source),
        vec![Box::new(upper_name), Box::new(upper_city)],
        Box::new(sink),
    );

    pipeline.run().unwrap();

    let result = std::fs::read_to_string(output.path()).unwrap();
    let records: Vec<Record> = serde_json::from_str(&result).unwrap();

    assert_eq!(records.len(), 2);
    assert_eq!(records[0].get("name"), Some(&"ALICE".to_string()));
    assert_eq!(records[0].get("city"), Some(&"NEW YORK".to_string()));
    assert_eq!(records[0].get("age"), Some(&"30".to_string()));
    assert_eq!(records[1].get("name"), Some(&"BOB".to_string()));
    assert_eq!(records[1].get("city"), Some(&"LONDON".to_string()));
}

#[test]
fn integration_streaming_mode() {
    let input = create_test_csv(&["word", "hello", "world", "rust"]);
    let output = NamedTempFile::new().unwrap();

    let source = CsvSource::new(input.path());
    let sink = JsonSink::new(output.path());
    let upper = UppercaseTransform::new("word");

    let mut pipeline = Pipeline::new(
        Box::new(source),
        vec![Box::new(upper)],
        Box::new(sink),
    );

    let count = pipeline.run_stream().unwrap();
    assert_eq!(count, 3);

    // Streaming mode: each write overwrites, so output contains only
    // the last record.
    let result = std::fs::read_to_string(output.path()).unwrap();
    let records: Vec<Record> = serde_json::from_str(&result).unwrap();
    assert_eq!(records.len(), 1);
    assert_eq!(records[0].get("word"), Some(&"RUST".to_string()));
}

#[test]
fn integration_single_transform() {
    let input = create_test_csv(&["label", "foo", "bar"]);
    let output = NamedTempFile::new().unwrap();

    let source = CsvSource::new(input.path());
    let sink = JsonSink::new(output.path());
    let upper = UppercaseTransform::new("label");

    let mut pipeline = Pipeline::new(Box::new(source), vec![Box::new(upper)], Box::new(sink));
    pipeline.run().unwrap();

    let result = std::fs::read_to_string(output.path()).unwrap();
    let records: Vec<Record> = serde_json::from_str(&result).unwrap();
    assert_eq!(records.len(), 2);
    assert_eq!(records[0].get("label"), Some(&"FOO".to_string()));
}

#[test]
fn integration_empty_pipeline_no_transforms() {
    let input = create_test_csv(&["x", "1", "2"]);
    let output = NamedTempFile::new().unwrap();

    let source = CsvSource::new(input.path());
    let sink = JsonSink::new(output.path());

    let mut pipeline = Pipeline::new(Box::new(source), vec![], Box::new(sink));
    pipeline.run().unwrap();

    let result = std::fs::read_to_string(output.path()).unwrap();
    let records: Vec<Record> = serde_json::from_str(&result).unwrap();
    assert_eq!(records.len(), 2);
    assert_eq!(records[0].get("x"), Some(&"1".to_string()));
}
