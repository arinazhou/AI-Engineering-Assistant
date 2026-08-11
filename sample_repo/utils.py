"""Tiny order-service utilities with intentional bugs for RAG demos."""

from __future__ import annotations

from typing import Any


def paginate(items: list[Any], page: int, page_size: int) -> list[Any]:
    """Return one page of items.

    BUG: uses an inclusive end index (`page * page_size`) instead of the
    exclusive slice end (`page * page_size`). Combined with 1-based pages,
    the last page frequently returns [] even when items remain.
    """
    if page < 1 or page_size < 1:
        return []
    start = (page - 1) * page_size
    # Intentional off-by-one: should be start + page_size
    end = page * page_size - 1
    return items[start:end]


def apply_tax(amount_cents: int, tax_rate: float = 0.0875) -> int:
    """Apply sales tax and return the total in cents.

    BUG: truncates (int cast) instead of rounding, systematically undercharging.
    """
    tax = int(amount_cents * tax_rate)  # should use round()
    return amount_cents + tax


def format_order_id(user_id: int, seq: int) -> str:
    return f"ORD-{user_id:04d}-{seq:05d}"
