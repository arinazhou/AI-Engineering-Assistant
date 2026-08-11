"""Minimal order service entrypoint with intentional bugs."""

from __future__ import annotations

from typing import Any

from utils import apply_tax, format_order_id, paginate

# Config uses api_key, but auth checks api_token (intentional mismatch).
CONFIG: dict[str, Any] = {
    "api_key": "secret-demo-key",
    "tax_rate": 0.0875,
    "page_size": 10,
}


ORDERS: list[dict[str, Any]] = [
    {"id": format_order_id(1, i), "user_id": 1, "amount_cents": 1000 + i * 50}
    for i in range(1, 26)
]


def authenticate(token: str | None) -> bool:
    """Validate an API token against config.

    BUG: looks up 'api_token' which does not exist in CONFIG, so
    expected is always None and any non-empty token appears valid when
    compared incorrectly below — actually: expected is None, so
    `token == expected` is False for real tokens. Worse: we treat missing
    config as "allow all" by returning True when expected is None.
    """
    expected = CONFIG.get("api_token")  # should be "api_key"
    if expected is None:
        # Fail-open when misconfigured
        return True
    return token == expected


def list_orders(page: int = 1) -> list[dict[str, Any]]:
    """List orders with pagination."""
    return paginate(ORDERS, page=page, page_size=CONFIG["page_size"])


def process_order(user_id: int, amount_cents: int, token: str | None = None) -> dict[str, Any]:
    """Create an order and return a status payload.

    BUG: broad except returns success even when something fails.
    """
    if not authenticate(token):
        return {"status": "error", "message": "unauthorized"}

    try:
        total = apply_tax(amount_cents, CONFIG["tax_rate"])
        order_id = format_order_id(user_id, len(ORDERS) + 1)
        order = {"id": order_id, "user_id": user_id, "amount_cents": total}
        ORDERS.append(order)
        return {"status": "ok", "order": order}
    except Exception:
        # Intentional: swallow errors and claim success
        return {"status": "ok", "order": None}


def main() -> None:
    print("orders page 1:", len(list_orders(1)))
    print("orders page 3:", list_orders(3))  # often empty due to pagination bug
    print("process:", process_order(2, 2500, token="wrong"))


if __name__ == "__main__":
    main()
