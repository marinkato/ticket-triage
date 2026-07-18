# Ticket Triage

A small Python script simulating a support-ticket triage pipeline for an e-commerce helpdesk. It reads tickets from a JSON export, classifies each ticket by intent (WISMO, return, order change, subscription), applies business rules to decide which tickets can be auto-resolved, and prints a summary report.

Built as a live-modification exercise: start from a working baseline, then implement incoming change requests one at a time.

## Requirements

Python 3.10+ (standard library only, no dependencies).

## Usage

```bash
python3 ticket_triage.py
```

Reads `tickets.json` from the same directory and prints the triage report to the terminal.

## How it works

1. **Load** — tickets are read from `tickets.json` (mock helpdesk API export)
2. **Classify** — each message is matched against intent keywords
3. **Decide** — business rules in `CONFIG` determine auto-resolvability (allowed intents, max ticket age, VIP customers always routed to a human)
4. **Report** — summary counts plus a per-ticket table
