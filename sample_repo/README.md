# Sample Repo — Order Service (intentionally buggy)

A tiny pure-Python order service used to demo the AI Engineering Assistant.

## What's broken (intentional)

1. **Pagination off-by-one** in `utils.py` — `paginate()` uses an inclusive end index incorrectly, so the last page often returns empty or drops items.
2. **Wrong config key** in `app.py` — looks up `api_token` but config defines `api_key`, so auth always fails open with a misleading message.
3. **Swallowed exceptions** in `app.py` — `process_order()` catches all exceptions and returns `"ok"` even on failure.
4. **Tax rounding** in `utils.py` — `apply_tax()` truncates instead of rounding, undercharging by cents.

## Try asking the assistant

- Why does the last page of orders come back empty?
- Why does authentication always succeed even with a bad token?
- Why do failed orders still return success?
- Why is the charged total sometimes a few cents low?
