use crate::domain::record::Record;
use crate::error::Error;

/// Port trait for transforming a single data record.
///
/// Transforms are stateless by design — identical input should always
/// produce identical output.  For stateful operations (aggregations,
/// windowing) use an external state store and reference it from the
/// transform implementation.
pub trait Transform {
    /// Transform a single record, returning the modified record.
    fn transform(&self, record: Record) -> Result<Record, Error>;
}
