"""
Ticket triage script — mock Implementation Engineer task.

Reads support tickets from tickets.json (simulating a helpdesk API export),
classifies each ticket by intent, decides whether it can be auto-resolved,
and prints a summary report.

Run: python3 ticket_triage.py
"""

import json
from datetime import datetime, timezone

CONFIG = {
    "auto_resolve_intents": ["wismo", "order_status", "return"],
    "max_ticket_age_days": 30,
    "max_auto_resolve_value_eur": 100,
    "input_file": "tickets.json",
}

INTENT_KEYWORDS = {
    "wismo": ["where is my order", "wismo", "tracking", "hasn't arrived"],
    "return": ["return", "refund", "send back", "money back"],
    "order_change": ["change my order", "wrong item", "change address", "wrong size"],
    "subscription": ["subscription", "cancel my plan", "pause delivery"],
    "other": [],
}


def load_tickets(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def classify_intent(message):
    text = message.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return intent
    return "other"


def ticket_age_days(created_at):
    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    return (now - created).days


def is_auto_resolvable(ticket, intent):
    if intent not in CONFIG["auto_resolve_intents"]:
        return False
    if ticket_age_days(ticket["created_at"]) > CONFIG["max_ticket_age_days"]:
        return False
    if ticket.get("vip_customer"):
        return False  # VIPs always go to a human
    if ticket["order_value_eur"] > CONFIG["max_auto_resolve_value_eur"]:
        return False  # high-value orders always go to a human
    return True


def process_tickets(tickets):
    results = []
    for ticket in tickets:
        intent = classify_intent(ticket["message"])
        results.append({
            "id": ticket["id"],
            "customer": ticket["customer_email"],
            "intent": intent,
            "auto_resolve": is_auto_resolvable(ticket, intent),
            "age_days": ticket_age_days(ticket["created_at"]),
            "order_value_eur": ticket["order_value_eur"],
        })
    return results


def print_report(results):
    auto = [r for r in results if r["auto_resolve"]]
    manual = [r for r in results if not r["auto_resolve"]]

    manual_value = sum(r["order_value_eur"] for r in manual)

    print(f"Processed {len(results)} tickets")
    print(f"  Auto-resolvable: {len(auto)}")
    print(f"  Needs human:     {len(manual)}")
    print(f"  Unresolved value: EUR {manual_value:.2f}")
    print()
    print(f"{'ID':<8}{'Intent':<15}{'Auto':<6}{'Age(d)':<8}{'Value(EUR)':<12}Customer")
    print("-" * 72)
    for r in results:
        value = "-" if r["auto_resolve"] else f"{r['order_value_eur']:.2f}"
        print(f"{r['id']:<8}{r['intent']:<15}{str(r['auto_resolve']):<6}{r['age_days']:<8}{value:<12}{r['customer']}")


def main():
    tickets = load_tickets(CONFIG["input_file"])
    results = process_tickets(tickets)
    print_report(results)


if __name__ == "__main__":
    main()
