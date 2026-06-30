"""Core pipeline abstractions for data extraction, transformation, and loading."""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")
U = TypeVar("U")


@dataclass
class DataStream(Generic[T]):
    """A single record flowing through a pipeline, carrying data and metadata."""

    data: T
    metadata: dict[str, Any] = field(default_factory=dict)


class Source(Generic[T]):
    """Produce a sequence of DataStream records.

    Subclass and override ``__call__`` (or pass a callable) to emit records
    from any backend — files, databases, APIs, message queues.
    """

    def __init__(self, producer: Callable[[], Iterator[T]] | None = None) -> None:
        self._producer = producer

    def __call__(self) -> Iterator[DataStream[T]]:
        if self._producer is not None:
            for item in self._producer():
                yield DataStream(data=item)
        else:
            yield from self._emit()

    def _emit(self) -> Iterator[DataStream[T]]:
        """Override in subclasses to provide custom production logic."""
        return iter([])


class Transform(Generic[T, U]):
    """Transform each record in a pipeline.

    Subclass and override ``__call__`` (or pass a callable) to apply
    stateless or stateful transformations.
    """

    def __init__(self, fn: Callable[[T], U] | None = None) -> None:
        self._fn = fn

    def __call__(self, stream: DataStream[T]) -> DataStream[U]:
        if self._fn is not None:
            return DataStream(data=self._fn(stream.data), metadata=stream.metadata)
        return self._apply(stream)

    def _apply(self, stream: DataStream[T]) -> DataStream[U]:
        """Override in subclasses to provide custom transformation logic."""
        return DataStream(data=stream.data)  # type: ignore[return-value]


class Sink(Generic[T]):
    """Consume the final output of a pipeline.

    Subclass and override ``__call__`` (or pass a callable) to write records
    to any destination — files, databases, APIs, etc.
    """

    def __init__(self, consumer: Callable[[DataStream[T]], None] | None = None) -> None:
        self._consumer = consumer

    def __call__(self, stream: DataStream[T]) -> None:
        if self._consumer is not None:
            self._consumer(stream)
        else:
            self._accept(stream)

    def _accept(self, stream: DataStream[T]) -> None:
        """Override in subclasses to provide custom consumption logic."""
        return


class Pipeline(Generic[T]):
    """Orchestrate a sequence of source → transforms → sink.

    Example::

        pipe = Pipeline[int](
            source=Source(producer=lambda: iter(range(3))),
            transforms=[Transform(fn=lambda x: x * 2)],
            sink=Sink(consumer=lambda s: results.append(s.data)),
        )
        pipe.run()
    """

    def __init__(
        self,
        source: Source[T],
        transforms: list[Transform[Any, Any]] | None = None,
        sink: Sink[T] | None = None,
    ) -> None:
        self.source = source
        self.transforms = transforms or []
        self.sink = sink or Sink()

    def run(self) -> None:
        """Execute the pipeline: pull from source, push through transforms, deliver to sink."""
        errors: list[Exception] = []
        source_iter = iter(self.source())
        while True:
            try:
                stream = next(source_iter)
            except StopIteration:
                break
            except Exception as exc:
                logger.exception("Pipeline source failed")
                errors.append(exc)
                continue
            try:
                current: DataStream[Any] = stream
                for transform in self.transforms:
                    current = transform(current)
                self.sink(current)
            except Exception as exc:
                logger.exception("Pipeline record failed")
                errors.append(exc)
        if errors:
            raise PipelineError(
                f"{len(errors)} record(s) failed during pipeline execution",
                errors,
            )


class PipelineError(Exception):
    """Raised when one or more records fail during pipeline execution."""

    def __init__(self, message: str, errors: list[Exception]) -> None:
        self.errors = errors
        super().__init__(message)
