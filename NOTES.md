# Notes

Running log of changes and decisions made during this exercise. One line per decision — what changed, where, and why.

**Format:** `HH:MM — <what> — <why / decision reasoning>`

---

- 09:00 — Baseline run confirmed — 7 tickets, 1 auto-resolvable, script working as-is before any changes.
- 09:20 — Added `order_value_eur` to the report (per-ticket column + total unresolved value) — added in `print_report()` only, since this is a display concern, not a classification/decision change. Auto-resolved tickets show "-" instead of a value, to keep focus on money still stuck with a human.
- 09:45 — Returns under 100 EUR rule requested — implementation in progress; test ticket (return, 45 EUR) still failing (shows `False`), debugging threshold placement.
