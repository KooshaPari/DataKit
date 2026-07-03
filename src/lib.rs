/// A single data record flowing through a pipeline.
///
/// Wraps a value of type `T` — the core data unit that sources emit,
/// transforms process, and sinks consume.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DataStream<T> {
    pub data: T,
}

impl<T> DataStream<T> {
    pub fn new(data: T) -> Self {
        Self { data }
    }
}

/// Type-safe entrypoint for a data pipeline.
///
/// A pipeline accepts a vector of `DataStream<T>` inputs, applies a
/// transformation, and produces `DataStream<U>` outputs.
///
/// # Example
///
/// ```
/// use datakit::{DataStream, Pipeline};
///
/// let double = Pipeline::new(Box::new(|x: i32| x * 2));
/// let input  = vec![DataStream::new(1), DataStream::new(2)];
/// let output = double.run(input);
/// assert_eq!(output, vec![DataStream::new(2), DataStream::new(4)]);
/// ```
pub struct Pipeline<T, U> {
    transform: Box<dyn Fn(T) -> U>,
}

impl<T, U> Pipeline<T, U> {
    pub fn new(transform: Box<dyn Fn(T) -> U>) -> Self {
        Self { transform }
    }

    /// Run the pipeline over a batch of input streams.
    pub fn run(&self, input: Vec<DataStream<T>>) -> Vec<DataStream<U>> {
        input
            .into_iter()
            .map(|stream| DataStream::new((self.transform)(stream.data)))
            .collect()
    }
}
