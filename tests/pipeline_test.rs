use datakit::{DataStream, Pipeline};

#[test]
fn test_basic_transform() {
    let pipeline = Pipeline::new(Box::new(|x: i32| x * 2));
    let input = vec![DataStream::new(1), DataStream::new(2), DataStream::new(3)];
    let output = pipeline.run(input);
    assert_eq!(
        output,
        vec![DataStream::new(2), DataStream::new(4), DataStream::new(6)]
    );
}
