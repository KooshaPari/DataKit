use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

/// A single data record — a schema-less key-value map.
///
/// `Record` is the core domain type flowing through a pipeline:
/// a source produces `Record` values, transforms mutate them, and a sink
/// consumes them.  Values are stored as `String` for simplicity in this
/// first increment; a future version may add typed variants.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Record {
    /// Ordered key-value fields.
    pub fields: BTreeMap<String, String>,
}

impl Record {
    /// Create an empty record.
    pub fn new() -> Self {
        Record {
            fields: BTreeMap::new(),
        }
    }

    /// Create a record from a key-value iterator.
    pub fn from_pairs<I>(iter: I) -> Self
    where
        I: IntoIterator<Item = (String, String)>,
    {
        Record {
            fields: BTreeMap::from_iter(iter),
        }
    }

    /// Get a field value by key.
    pub fn get(&self, key: &str) -> Option<&String> {
        self.fields.get(key)
    }

    /// Insert a field value.
    pub fn insert(&mut self, key: String, value: String) {
        self.fields.insert(key, value);
    }

    /// Return the number of fields.
    pub fn len(&self) -> usize {
        self.fields.len()
    }

    /// Return true if the record has no fields.
    pub fn is_empty(&self) -> bool {
        self.fields.is_empty()
    }

    /// Return a sorted list of field keys (for deterministic iteration).
    pub fn keys(&self) -> Vec<&String> {
        self.fields.keys().collect()
    }
}

impl Default for Record {
    fn default() -> Self {
        Record::new()
    }
}

impl<I> From<I> for Record
where
    I: IntoIterator<Item = (String, String)>,
{
    fn from(iter: I) -> Self {
        Record::from_pairs(iter)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_record_is_empty() {
        let r = Record::new();
        assert!(r.is_empty());
        assert_eq!(r.len(), 0);
    }

    #[test]
    fn test_record_insert_and_get() {
        let mut r = Record::new();
        r.insert("name".into(), "Alice".into());
        r.insert("age".into(), "30".into());
        assert_eq!(r.get("name"), Some(&"Alice".into()));
        assert_eq!(r.get("age"), Some(&"30".into()));
        assert_eq!(r.len(), 2);
    }

    #[test]
    fn test_record_from_iter() {
        let data = vec![
            ("a".to_string(), "1".to_string()),
            ("b".to_string(), "2".to_string()),
        ];
        let r = Record::from_pairs(data);
        assert_eq!(r.get("a"), Some(&"1".into()));
        assert_eq!(r.get("b"), Some(&"2".into()));
    }

    #[test]
    fn test_record_from_trait() {
        let data = vec![
            ("x".to_string(), "10".to_string()),
            ("y".to_string(), "20".to_string()),
        ];
        let r: Record = data.into();
        assert_eq!(r.get("x"), Some(&"10".into()));
    }

    #[test]
    fn test_record_serde_roundtrip() {
        let mut r = Record::new();
        r.insert("key".into(), "value".into());
        let json = serde_json::to_string(&r).unwrap();
        let back: Record = serde_json::from_str(&json).unwrap();
        assert_eq!(r, back);
    }

    #[test]
    fn test_record_keys_are_sorted() {
        let data = vec![
            ("z".to_string(), "1".to_string()),
            ("a".to_string(), "2".to_string()),
            ("m".to_string(), "3".to_string()),
        ];
        let r = Record::from_pairs(data);
        let keys = r.keys();
        assert_eq!(keys, vec![&"a".to_string(), &"m".to_string(), &"z".to_string()]);
    }

    #[test]
    fn test_record_default() {
        let r = Record::default();
        assert!(r.is_empty());
    }
}
