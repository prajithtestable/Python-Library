"""Batch pricing engine -- Python 3.10 branch.

Uses PEP 617 parenthesized context managers, PEP 604 unions and PEP 634
pattern matching. ``ExceptionGroup`` / ``except*`` is still 3.11+, so failures
are collected into a plain list.
"""

from contextlib import nullcontext
from typing import Any, Iterable, Iterator

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

    def price_batch(
        self,
        records: list[OrderRecord],
        batch_size: int = 25,
        fail_fast: bool = False,
    ) -> dict[str, Any]:
        priced: list[dict[str, Any]] = []
        failures: list[str] = []

        # PEP 617 parenthesized context managers, new in Python 3.10.
        with (
            nullcontext() as _outer,
            nullcontext() as _inner,
        ):
            for batch in chunk(list(records), batch_size):
                for record in batch:
                    try:
                        total = self.service.calculate_total(
                            record.quantity, record.unit_price, record.discount_pct
                        )
                    except ValueError as exc:
                        if fail_fast:
                            raise
                        failures.append(f"{record.order_id}: {exc}")
                        continue
                    payload = to_payload(record)
                    payload["total"] = total
                    payload["free_shipping"] = self.service.is_eligible_for_free_shipping(
                        total
                    )
                    priced.append(payload)

        return {"priced": priced, "failures": failures}

    def classify_outcome(self, result: dict[str, Any]) -> str:
        """PEP 634 pattern matching over the batch outcome."""
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

    def exit_code_for(self, result: dict[str, Any]) -> int:
        """Map a batch outcome onto a process exit code."""
        match self.classify_outcome(result):
            case "empty" | "clean":
                return 0
            case "total-failure":
                return 1
            case _:
                return 3
