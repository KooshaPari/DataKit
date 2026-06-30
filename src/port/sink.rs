use crate::domain::record::Record;
use crate::error::Error;

/// Port trait for writing data records to an external destination.
///
/// Implementations write to files, databases, APIs, message queues, etc.
pub trait DataSink {
    /// Write a batch of records.
    fn write(&mut self, records: &[Record]) -> Result<(), Error>;
}
