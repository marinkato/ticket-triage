"""
Ticket triage script — mock Implementation Engineer task.

Reads support tickets from tickets.json (simulating a helpdesk API export),
classifies each ticket by intent, decides whether it can be auto-resolved,
and prints a summary report.

Run: python3 ticket_triage.py
"""

import csv
import json
import os
from datetime import datetime, timezone

REPORTS_DIR = "reports"

CONFIG = {
    "auto_resolve_intents": ["wismo", "order_status", "return"],
    "max_ticket_age_days": 30,
    "max_auto_resolve_value_eur": 100,
    "input_file": "tickets.json",
}

INTENT_KEYWORDS = {
    "wismo": ["where is my order", "wismo", "tracking", "hasn't arrived"],
    "return": ["return", "refund", "send back", "money back"],
    "order_change": ["change my order", "wrong item", "wrong size"],
    "address_change": ["change address", "change my address", "wrong address", "update my address", "shipping address", "delivery address"],
    "subscription_cancel": ["cancel my subscription", "cancel subscription", "cancel my plan", "cancel my membership", "stop my subscription", "end my subscription"],
    "subscription_pause": ["pause my subscription", "pause subscription", "pause delivery", "skip my delivery", "skip a delivery", "hold my subscription"],
    "other": [],
}

TEAM_ROUTING = {
    "subscription_cancel": "retention",
    "subscription_pause": "billing",
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
    if intent == "address_change":
        # Not the usual age/value gated rule: address changes auto-resolve purely on
        # shipped status. VIPs are normally always routed to a human, but this rule
        # carves out an explicit exception for them, capped at the standard value cap.
        if ticket.get("shipped"):
            return False  # already shipped — a human needs to handle it
        if ticket.get("vip_customer"):
            return ticket["order_value_eur"] < CONFIG["max_auto_resolve_value_eur"]
        return True
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
            "vip_customer": ticket.get("vip_customer", False),
            "team": TEAM_ROUTING.get(intent, "-"),
        })
    return results


def queue_order(results):
    return sorted(results, key=lambda r: not r["vip_customer"])


def print_report(results):
    auto = [r for r in results if r["auto_resolve"]]
    manual = [r for r in results if not r["auto_resolve"]]

    manual_value = sum(r["order_value_eur"] for r in manual)

    print(f"Processed {len(results)} tickets")
    print(f"  Auto-resolvable: {len(auto)}")
    print(f"  Needs human:     {len(manual)}")
    print(f"  Unresolved value: EUR {manual_value:.2f}")
    print()
    print(f"{'ID':<8}{'Intent':<20}{'Team':<11}{'Auto':<6}{'VIP':<6}{'Age(d)':<8}{'Value(EUR)':<12}Customer")
    print("-" * 94)
    for r in queue_order(results):
        value = f"{r['order_value_eur']:.2f}"
        print(f"{r['id']:<8}{r['intent']:<20}{r['team']:<11}{str(r['auto_resolve']):<6}{str(r['vip_customer']):<6}{r['age_days']:<8}{value:<12}{r['customer']}")


def export_csv(results):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    export_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(REPORTS_DIR, f"ticket_report_{export_timestamp}.csv")
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Intent", "Team", "Auto", "VIP", "Age(d)", "Value(EUR)", "Customer"])
        for r in queue_order(results):
            writer.writerow([
                r["id"],
                r["intent"],
                r["team"],
                r["auto_resolve"],
                r["vip_customer"],
                r["age_days"],
                f"{r['order_value_eur']:.2f}",
                r["customer"],
            ])
    return filename


def main():
    tickets = load_tickets(CONFIG["input_file"])
    results = process_tickets(tickets)
    print_report(results)
    csv_path = export_csv(results)
    print(f"\nCSV report exported to {csv_path}")


if __name__ == "__main__":
    main()
