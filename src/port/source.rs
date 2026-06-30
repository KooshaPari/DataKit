use crate::domain::record::Record;
use crate::error::Error;

/// Port trait for reading data records from an external source.
///
/// Implementations connect to files, databases, APIs, message queues, etc.
pub trait DataSource {
    /// Read all available records.
    fn read(&mut self) -> Result<Vec<Record>, Error>;
}
