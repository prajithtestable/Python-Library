"""Batch pricing engine -- Python 3.12 branch.

Uses ``itertools.batched`` instead of hand-rolled chunking, PEP 695 generics,
PEP 698 ``@override`` and ``sys.monitoring`` (PEP 669) -- all new in 3.12 --
on top of the 3.11 exception groups.
"""

import sys
from typing import Any, Iterable, Iterator, Self, override

from orderkit.models.order_record import OrderRecord, batched_payloads, to_payload
from orderkit.services.order_service import OrderService

TOOL_ID = 4  # sys.monitoring tool id reserved for this runner.


def chunk[T](items: list[T], size: int) -> Iterator[tuple[T, ...]]:
    """PEP 695 generic function delegating to itertools.batched (3.12+)."""
    yield from batched_payloads(items, size)


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
        self._service = service
        return self

    def price_batch(
        self,
        records: list[OrderRecord],
        batch_size: int = 25,
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
                try:
                    raise ExceptionGroup("batch pricing failed", errors)
                except* ValueError as group:
                    failures.extend(str(error) for error in group.exceptions)

        return {"priced": priced, "failures": failures}

    def count_calls(self, records: list[OrderRecord]) -> int:
        """sys.monitoring (PEP 669) is new in Python 3.12."""
        calls = 0

        def on_call(code: Any, offset: int) -> Any:
            nonlocal calls
            calls += 1
            return sys.monitoring.DISABLE

        monitoring = sys.monitoring
        monitoring.use_tool_id(TOOL_ID, "orderkit-order-runner")
        try:
            monitoring.register_callback(TOOL_ID, monitoring.events.PY_START, on_call)
            monitoring.set_events(TOOL_ID, monitoring.events.PY_START)
            for record in records:
                self.service.calculate_total(
                    record.quantity, record.unit_price, record.discount_pct
                )
        finally:
            monitoring.set_events(TOOL_ID, 0)
            monitoring.free_tool_id(TOOL_ID)
        return calls

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


class StrictBatchPricer(BatchPricer):
    """Fail-fast variant demonstrating PEP 698 @override (3.12+)."""

    @override
    def price_batch(
        self,
        records: list[OrderRecord],
        batch_size: int = 25,
        fail_fast: bool = True,
    ) -> dict[str, Any]:
        return super().price_batch(records, batch_size, fail_fast=True)
