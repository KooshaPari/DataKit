use std::fmt;

/// Unified error type for the DataKit crate.
#[derive(Debug)]
pub enum Error {
    /// Wraps an I/O error from the standard library.
    Io(std::io::Error),
    /// Wraps a CSV parsing/reading error.
    Csv(csv::Error),
    /// Wraps a JSON serialization/deserialization error.
    Json(serde_json::Error),
    /// A generic error with a message string.
    Message(String),
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::Io(e) => write!(f, "I/O error: {e}"),
            Error::Csv(e) => write!(f, "CSV error: {e}"),
            Error::Json(e) => write!(f, "JSON error: {e}"),
            Error::Message(msg) => write!(f, "{msg}"),
        }
    }
}

impl std::error::Error for Error {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            Error::Io(e) => Some(e),
            Error::Csv(e) => Some(e),
            Error::Json(e) => Some(e),
            Error::Message(_) => None,
        }
    }
}

impl From<std::io::Error> for Error {
    fn from(e: std::io::Error) -> Self {
        Error::Io(e)
    }
}

impl From<csv::Error> for Error {
    fn from(e: csv::Error) -> Self {
        Error::Csv(e)
    }
}

impl From<serde_json::Error> for Error {
    fn from(e: serde_json::Error) -> Self {
        Error::Json(e)
    }
}

impl From<String> for Error {
    fn from(msg: String) -> Self {
        Error::Message(msg)
    }
}

impl From<&str> for Error {
    fn from(msg: &str) -> Self {
        Error::Message(msg.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_display() {
        let io_err = Error::Io(std::io::Error::new(std::io::ErrorKind::NotFound, "file missing"));
        assert!(io_err.to_string().contains("I/O error"));

        let msg_err: Error = "something went wrong".into();
        assert_eq!(msg_err.to_string(), "something went wrong");
    }

    #[test]
    fn test_error_csv_display() {
        let csv_err = Error::Csv(csv::Error::from(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "bad csv",
        )));
        assert!(csv_err.to_string().contains("CSV error"));
    }

    #[test]
    fn test_error_json_display() {
        let json_err = Error::Json(serde_json::from_str::<i32>("not_a_number").unwrap_err());
        assert!(json_err.to_string().contains("JSON error"));
    }

    #[test]
    fn test_error_from_string() {
        let err: Error = "custom error".into();
        assert!(matches!(err, Error::Message(_)));
    }

    #[test]
    fn test_error_source_io() {
        let inner = std::io::Error::new(std::io::ErrorKind::NotFound, "file missing");
        let err = Error::Io(inner);
        let std_err: &dyn std::error::Error = &err;
        assert!(std_err.source().is_some());
    }

    #[test]
    fn test_error_source_csv() {
        let inner = csv::Error::from(std::io::Error::new(std::io::ErrorKind::InvalidData, "bad"));
        let err = Error::Csv(inner);
        let std_err: &dyn std::error::Error = &err;
        assert!(std_err.source().is_some());
    }

    #[test]
    fn test_error_source_json() {
        let inner = serde_json::from_str::<i32>("not_a_number").unwrap_err();
        let err = Error::Json(inner);
        let std_err: &dyn std::error::Error = &err;
        assert!(std_err.source().is_some());
    }

    #[test]
    fn test_error_source_message_returns_none() {
        let err: Error = "test error".into();
        let std_err: &dyn std::error::Error = &err;
        assert!(std_err.source().is_none());
    }
}
