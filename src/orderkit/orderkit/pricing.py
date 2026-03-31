"""Batch pricing engine -- Python 3.9 branch.

The batch entry point behind ``orderkit.price_batch``. Kept separate from
the public facade so the facade stays a thin, stable surface. ``ExceptionGroup`` / ``except*`` (PEP 654) is 3.11+, and
``itertools.batched`` is 3.12+, so this branch batches by hand and collects
failures into a plain list.
"""

from typing import Any, Iterable, Iterator, List, Optional

from orderkit.models.order_record import OrderRecord, to_payload
from orderkit.services.order_service import OrderService


def chunk(items: List[Any], size: int) -> Iterator[List[Any]]:
    """Manual batching. itertools.batched is not available before 3.12."""
    if size <= 0:
        raise ValueError("size must be positive")
    for start in range(0, len(items), size):
        yield items[start : start + size]


class BatchPricer:
    """Prices batches of order records on behalf of the public API."""

    def __init__(self, service: Optional[OrderService] = None) -> None:
        self._service = service

    @property
    def service(self) -> OrderService:
        """Lazily constructed so ``import orderkit`` stays cheap."""
        if self._service is None:
            self._service = OrderService()
        return self._service

    def price_batch(
        self,
        records: List[OrderRecord],
        batch_size: int = 25,
        fail_fast: bool = False,
    ) -> dict:
        """Price a list of records, returning results and failures."""
        priced = []
        failures = []

        for batch in chunk(list(records), batch_size):
            for record in batch:
                try:
                    total = self.service.calculate_total(
                        record.quantity, record.unit_price, record.discount_pct
                    )
                except ValueError as exc:
                    if fail_fast:
                        raise
                    failures.append("{0}: {1}".format(record.order_id, exc))
                    continue
                payload = to_payload(record)
                payload["total"] = total
                payload["free_shipping"] = self.service.is_eligible_for_free_shipping(total)
                priced.append(payload)

        return {"priced": priced, "failures": failures}

    def records_from(self, rows: Optional[Iterable[dict]]) -> Iterable[OrderRecord]:
        for row in rows or []:
            yield OrderRecord(
                order_id=row["order_id"],
                channel=row.get("channel", "retail"),
                quantity=int(row.get("quantity", 0)),
                unit_price=float(row.get("unit_price", 0.0)),
                discount_pct=float(row.get("discount_pct", 0.0)),
            )

    def status_for(self, result: dict) -> str:
        """Summarise a batch outcome for the caller."""
        if not result["priced"] and not result["failures"]:
            return "empty"
        if result["failures"] and not result["priced"]:
            return "failed"
        if result["failures"]:
            return "partial"
        return "ok"
