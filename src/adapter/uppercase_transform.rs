use crate::domain::record::Record;
use crate::error::Error;
use crate::port::Transform;

/// A `Transform` that uppercases the string value of a named field.
///
/// If the field does not exist in the record, the record passes through
/// unchanged.
pub struct UppercaseTransform {
    field: String,
}

impl UppercaseTransform {
    /// Create a new `UppercaseTransform` targeting the given field.
    pub fn new(field: &str) -> Self {
        UppercaseTransform {
            field: field.to_string(),
        }
    }

    /// The field name this transform operates on.
    pub fn field(&self) -> &str {
        &self.field
    }
}

impl Transform for UppercaseTransform {
    fn transform(&self, mut record: Record) -> Result<Record, Error> {
        if let Some(value) = record.fields.get_mut(&self.field) {
            *value = value.to_uppercase();
        }
        Ok(record)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_transform_uppercases_field() {
        let mut record = Record::new();
        record.insert("name".into(), "alice".into());
        record.insert("city".into(), "New York".into());

        let t = UppercaseTransform::new("name");
        let result = t.transform(record).unwrap();
        assert_eq!(result.get("name"), Some(&"ALICE".into()));
        assert_eq!(result.get("city"), Some(&"New York".into()));
    }

    #[test]
    fn test_transform_missing_field_unchanged() {
        let mut record = Record::new();
        record.insert("name".into(), "alice".into());

        let t = UppercaseTransform::new("nonexistent");
        let result = t.transform(record).unwrap();
        assert_eq!(result.get("name"), Some(&"alice".into()));
    }

    #[test]
    fn test_transform_empty_value() {
        let mut record = Record::new();
        record.insert("name".into(), "".into());

        let t = UppercaseTransform::new("name");
        let result = t.transform(record).unwrap();
        assert_eq!(result.get("name"), Some(&"".into()));
    }

    #[test]
    fn test_transform_multiple_calls() {
        let mut record = Record::new();
        record.insert("word".into(), "hello".into());

        let t = UppercaseTransform::new("word");
        let r1 = t.transform(record).unwrap();
        assert_eq!(r1.get("word"), Some(&"HELLO".into()));
    }

    #[test]
    fn test_uppercase_transform_field_accessor() {
        let t = UppercaseTransform::new("my_field");
        assert_eq!(t.field(), "my_field");
    }
}
