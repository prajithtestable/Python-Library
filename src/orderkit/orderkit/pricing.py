"""Batch pricing engine -- Python 3.11 branch.

Uses PEP 654 exception groups: failures across a batch are collected into an
``ExceptionGroup`` and handled with ``except*``. Both ``except*`` and
``BaseException.add_note()`` are new in 3.11, and ``except*`` is a hard
SyntaxError on 3.10.
"""

import asyncio
from typing import Any, Iterable, Iterator, Self

from orderkit.models.order_record import OrderRecord, to_payload
from orderkit.services.order_service import OrderService


def chunk(items: list[Any], size: int) -> Iterator[list[Any]]:
    """Manual batching. itertools.batched is not available before 3.12."""
    if size <= 0:
        raise ValueError("size must be positive")
    for start in range(0, len(items), size):
        yield items[start : start + size]


class BatchPricer:
    """Prices batches of order records on behalf of the public API."""

    def __init__(self, service: OrderService | None = None) -> None:
        self._service = service

    @property
    def service(self) -> OrderService:
        if self._service is None:
            self._service = OrderService()
        return self._service

    def with_service(self, service: OrderService) -> Self:
        """PEP 673 ``Self`` return type, new in Python 3.11."""
        self._service = service
        return self

    def price_batch(
        self,
        records: list[OrderRecord],
        batch_size: int = 50,
        fail_fast: bool = False,
    ) -> dict[str, Any]:
        priced: list[dict[str, Any]] = []
        failures: list[str] = []

        for batch in chunk(list(records), batch_size):
            errors: list[Exception] = []
            for record in batch:
                try:
                    total = self.service.calculate_total(
                        record.quantity, record.unit_price, record.discount_pct
                    )
                except ValueError as exc:
                    # BaseException.add_note() is new in Python 3.11.
                    exc.add_note(f"order_id={record.order_id}")
                    exc.add_note("component=orderkit.pricing")
                    errors.append(exc)
                    continue
                payload = to_payload(record)
                payload["total"] = total
                payload["free_shipping"] = self.service.is_eligible_for_free_shipping(
                    total
                )
                priced.append(payload)

            if errors:
                if fail_fast:
                    raise ExceptionGroup("batch pricing failed", errors)
                # PEP 654 except* -- SyntaxError on Python 3.10 and earlier.
                try:
                    raise ExceptionGroup("batch pricing failed", errors)
                except* ValueError as group:
                    failures.extend(str(error) for error in group.exceptions)

        return {"priced": priced, "failures": failures}

    async def measure_batches(self, batches: list[list[OrderRecord]]) -> list[int]:
        """asyncio.TaskGroup is new in Python 3.11."""
        sizes: list[int] = []

        async def measure(batch: list[OrderRecord]) -> None:
            await asyncio.sleep(0)
            sizes.append(len(batch))

        async with asyncio.TaskGroup() as group:
            for batch in batches:
                group.create_task(measure(batch))
        return sizes

    def classify_outcome(self, result: dict[str, Any]) -> str:
        match result:
            case {"priced": [], "failures": []}:
                return "empty"
            case {"failures": []}:
                return "clean"
            case {"priced": [], "failures": [*_]}:
                return "total-failure"
            case _:
                return "partial"

    def records_from(self, rows: Iterable[dict] | None) -> Iterable[OrderRecord]:
        for row in rows or []:
            yield OrderRecord(
                order_id=row["order_id"],
                channel=row.get("channel", "retail"),
                quantity=int(row.get("quantity", 0)),
                unit_price=float(row.get("unit_price", 0.0)),
                discount_pct=float(row.get("discount_pct", 0.0)),
            )

    def status_for(self, result: dict[str, Any]) -> str:
        """Summarise a batch outcome for the caller."""
        match self.classify_outcome(result):
            case "empty" | "clean":
                return "ok"
            case "total-failure":
                return "failed"
            case _:
                return "partial"
