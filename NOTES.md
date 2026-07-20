# Notes

Running log of changes and decisions made during this exercise. One line per decision — what changed, where, and why.

**Format:** `HH:MM — <what> — <why / decision reasoning>`

---

- 09:00 — Baseline run confirmed — 7 tickets, 1 auto-resolvable, script working as-is before any changes.
- 09:20 — Added `order_value_eur` to the report (per-ticket column + total unresolved value) — added in `print_report()` only, since this is a display concern, not a classification/decision change. Auto-resolved tickets show "-" instead of a value, to keep focus on money still stuck with a human.
- 09:45 — Returns under 100 EUR rule requested — implementation in progress; test ticket (return, 45 EUR) still failing (shows `False`), debugging threshold placement.
- 10:15 — Root cause found: `"return"` was missing from `CONFIG["auto_resolve_intents"]`, so the intent check rejected all returns before the value/age/VIP checks ran. Added `"return"` to the whitelist — T-1008 (45 EUR return) now shows `True`, T-1002 (129 EUR return) correctly stays `False`.
- 10:30 — Requested that auto-resolved tickets also show their order value in the report table (previously hidden as "-" to keep focus on money still stuck with a human). Changed `print_report()` to always print `order_value_eur`. "Unresolved value" total is unaffected — still sums manual tickets only.
- 11:00 — Client requested VIP customers get first in the queue with agents. Added `vip_customer` to the `process_tickets()` result dict, added `queue_order()` (stable sort, VIP first, non-VIP keep original relative order), and updated `print_report()` to iterate in that order plus show a VIP column. VIPs were already forced to `auto_resolve = False`, so this only reorders who reaches the human queue first — no change to auto-resolve logic itself.
- 11:20 — Requested a CSV export of the report with all print-table columns, filename carrying the export date. Added `export_csv()` — writes ID, Intent, Auto, VIP, Age(d), Value(EUR), Customer to `ticket_report_<date>.csv` in the same `queue_order()` order as the printed table, called at the end of `main()`. Added `.gitignore` for `ticket_report_*.csv` since these are per-run generated artifacts, not source.
- 11:35 — Clarified `queue_order()` sort behavior: sort key is only `not vip_customer` (VIP → 0, non-VIP → 1), so VIP tickets go first and everything else ties. Python's `sorted()` is stable, so tied (non-VIP) tickets keep their original `tickets.json` order as the tiebreaker — it's not sorted by age or value at all.
