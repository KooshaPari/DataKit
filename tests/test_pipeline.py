"""Tests for the DataKit pipeline core module."""

from __future__ import annotations

import pytest

from datakit.pipeline import (
    DataStream,
    Pipeline,
    PipelineError,
    Sink,
    Source,
    Transform,
)


class TestDataStream:
    """DataStream creation and default metadata."""

    def test_basic_record(self) -> None:
        stream = DataStream(data=42)
        assert stream.data == 42
        assert stream.metadata == {}

    def test_with_metadata(self) -> None:
        stream = DataStream(data="hello", metadata={"key": "val"})
        assert stream.data == "hello"
        assert stream.metadata == {"key": "val"}


class TestSource:
    """Source produces DataStream records."""

    def test_from_producer(self) -> None:
        src = Source(producer=lambda: iter([10, 20, 30]))
        results = list(src())
        assert len(results) == 3
        assert results[0].data == 10
        assert results[2].data == 30

    def test_empty_producer(self) -> None:
        src = Source(producer=lambda: iter([]))
        assert list(src()) == []

    def test_subclass(self) -> None:
        class RangeSource(Source[int]):
            def __init__(self, n: int) -> None:
                super().__init__()
                self._n = n

            def _emit(self):  # type: ignore[no-untyped-def]
                for i in range(self._n):
                    yield DataStream(data=i)

        src = RangeSource(3)
        results = list(src())
        assert [r.data for r in results] == [0, 1, 2]


class TestTransform:
    """Transform maps DataStream data values."""

    def test_from_fn(self) -> None:
        t = Transform(fn=lambda x: x * 2)
        result = t(DataStream(data=21))
        assert result.data == 42

    def test_preserves_metadata(self) -> None:
        t = Transform(fn=lambda x: x.upper())
        result = t(DataStream(data="hi", metadata={"src": "test"}))
        assert result.data == "HI"
        assert result.metadata == {"src": "test"}

    def test_subclass(self) -> None:
        class PrefixTransform(Transform[str, str]):
            def __init__(self, prefix: str) -> None:
                super().__init__()
                self._prefix = prefix

            def _apply(self, stream):  # type: ignore[no-untyped-def]
                return DataStream(
                    data=self._prefix + stream.data,
                    metadata=stream.metadata,
                )

        t = PrefixTransform("Mr. ")
        result = t(DataStream(data="Smith"))
        assert result.data == "Mr. Smith"


class TestSink:
    """Sink consumes DataStream records."""

    def test_from_consumer(self) -> None:
        collected: list[int] = []

        def collector(stream: DataStream[int]) -> None:
            collected.append(stream.data)

        sink = Sink(consumer=collector)
        sink(DataStream(data=99))
        assert collected == [99]

    def test_default_sink_does_not_raise(self) -> None:
        sink = Sink()
        sink(DataStream(data="anything"))  # should not raise


class TestPipeline:
    """Pipeline end-to-end execution."""

    def test_source_to_sink(self) -> None:
        collected: list[int] = []
        pipe = Pipeline[int](
            source=Source(producer=lambda: iter([1, 2, 3])),
            sink=Sink(consumer=lambda s: collected.append(s.data)),
        )
        pipe.run()
        assert collected == [1, 2, 3]

    def test_with_transform(self) -> None:
        collected: list[int] = []
        pipe = Pipeline[int](
            source=Source(producer=lambda: iter([1, 2, 3])),
            transforms=[Transform(fn=lambda x: x * 10)],
            sink=Sink(consumer=lambda s: collected.append(s.data)),
        )
        pipe.run()
        assert collected == [10, 20, 30]

    def test_multiple_transforms(self) -> None:
        collected: list[str] = []
        pipe = Pipeline[str](
            source=Source(producer=lambda: iter(["a", "b", "c"])),
            transforms=[
                Transform(fn=lambda x: x.upper()),
                Transform(fn=lambda x: f"[{x}]"),
            ],
            sink=Sink(consumer=lambda s: collected.append(s.data)),
        )
        pipe.run()
        assert collected == ["[A]", "[B]", "[C]"]

    def test_handles_record_error(self) -> None:
        """A failing record should not halt the entire pipeline."""

        def bad_producer():  # type: ignore[no-untyped-def]
            yield 1
            yield 2
            raise ValueError("producer failed on third")

        with pytest.raises(PipelineError) as exc_info:
            pipe = Pipeline[int](
                source=Source(producer=bad_producer),
                sink=Sink(consumer=lambda s: None),
            )
            pipe.run()
        assert len(exc_info.value.errors) == 1
        assert isinstance(exc_info.value.errors[0], ValueError)

    def test_transform_error_collected(self) -> None:
        collected: list[int] = []

        def failing_transform(x: int) -> int:
            if x == 2:
                raise ValueError("bad value")
            return x

        with pytest.raises(PipelineError) as exc_info:
            pipe = Pipeline[int](
                source=Source(producer=lambda: iter([1, 2, 3])),
                transforms=[Transform(fn=failing_transform)],
                sink=Sink(consumer=lambda s: collected.append(s.data)),
            )
            pipe.run()
        assert len(exc_info.value.errors) == 1
        assert isinstance(exc_info.value.errors[0], ValueError)
        # Pipeline continues after a failed record; 1 and 3 both succeed
        assert collected == [1, 3]

    def test_no_transforms(self) -> None:
        collected: list[int] = []
        pipe = Pipeline[int](
            source=Source(producer=lambda: iter([100])),
            sink=Sink(consumer=lambda s: collected.append(s.data)),
        )
        pipe.run()
        assert collected == [100]

    def test_empty_source(self) -> None:
        collected: list[int] = []
        pipe = Pipeline[int](
            source=Source(producer=lambda: iter([])),
            sink=Sink(consumer=lambda s: collected.append(s.data)),
        )
        pipe.run()
        assert collected == []

    def test_metadata_preserved_through_pipeline(self) -> None:
        """Verify a Source subclass can attach metadata and it survives transforms."""
        collected: list[DataStream[int]] = []

        class MetaSource(Source[int]):
            def __init__(self) -> None:
                super().__init__()

            def _emit(self):  # type: ignore[no-untyped-def]
                for i in range(2):
                    yield DataStream(data=i, metadata={"source": "test"})

        pipe = Pipeline[int](
            source=MetaSource(),
            transforms=[Transform(fn=lambda x: x + 1)],
            sink=Sink(consumer=lambda s: collected.append(s)),
        )
        pipe.run()
        assert len(collected) == 2
        for s in collected:
            assert s.metadata == {"source": "test"}
        assert [s.data for s in collected] == [1, 2]


class TestPipelineError:
    """PipelineError carries inner exception list."""

    def test_error_list(self) -> None:
        inner = [ValueError("e1"), TypeError("e2")]
        err = PipelineError("2 errors", inner)
        assert len(err.errors) == 2
        assert "2 errors" in str(err)
