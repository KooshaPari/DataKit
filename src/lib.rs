// DataKit — Data transformation and ETL toolkit for the Phenotype ecosystem.
//
// This crate provides a hexagonal-architecture ETL framework with:
// - Port traits for `DataSource`, `DataSink`, and `Transform`
// - Domain types (`Record`, `Pipeline`)
// - Built-in adapter implementations (CSV, JSON, string transforms)
//
// # Architecture
// ```
// ┌─────────────────────────────────────────┐
// │              Pipeline                    │
// │  (orchestrates source → transforms → sink)│
// └──────┬──────────┬────────────┬──────────┘
//        │          │            │
//   ┌────▼──┐  ┌────▼────┐  ┌───▼────┐
//   │Source │  │Transforms│  │  Sink  │
//   │(Port) │  │  (Port)  │  │ (Port) │
//   └───┬───┘  └────┬────┘  └───┬────┘
//       │           │           │
//   ┌───▼────┐  ┌───▼────┐  ┌──▼─────┐
//   │ CsvSrc │  │ Upper  │  │JsonSink│
//   │(Adapt) │  │(Adapt) │  │(Adapt) │
//   └────────┘  └────────┘  └────────┘
// ```

pub mod domain;
pub mod port;
pub mod adapter;
pub mod error;

pub use domain::pipeline::Pipeline;
pub use domain::record::Record;
pub use port::{DataSink, DataSource, Transform};
pub use error::Error;
