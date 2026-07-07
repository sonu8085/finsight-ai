"""Rule-based spending analysis that works even without an OpenAI key.

This produces the raw statistical insights (subscriptions, weekend spend,
category trends, etc). The AI service layer then optionally asks an LLM to
turn these into natural-language advice.
"""
from collections import defaultdict
from datetime import date

from app.models.transaction import Transaction, TransactionType


def _month_key(d: date) -> str:
    return d.strftime("%Y-%m")


def analyze_transactions(transactions: list[Transaction]) -> dict:
    """Compute structured statistics from a user's transaction history."""
    expenses = [t for t in transactions if t.type == TransactionType.EXPENSE]
    income = [t for t in transactions if t.type == TransactionType.INCOME]

    total_expense = sum(float(t.amount) for t in expenses)
    total_income = sum(float(t.amount) for t in income)

    # Category totals
    category_totals: dict[str, float] = defaultdict(float)
    for t in expenses:
        name = t.category.name if t.category else "Uncategorized"
        category_totals[name] += float(t.amount)
    top_categories = sorted(category_totals.items(), key=lambda x: -x[1])[:5]

    # Weekend vs weekday spend
    weekend_total = sum(float(t.amount) for t in expenses if t.transaction_date.weekday() >= 5)
    weekday_total = total_expense - weekend_total

    # Possible recurring subscriptions: same merchant/description appearing 2+ times
    # with similar amounts across different months.
    desc_occurrences: dict[str, list[Transaction]] = defaultdict(list)
    for t in expenses:
        key = (t.merchant or t.description).strip().lower()
        desc_occurrences[key].append(t)

    subscriptions = []
    for key, txns in desc_occurrences.items():
        months = {_month_key(t.transaction_date) for t in txns}
        if len(txns) >= 2 and len(months) >= 2:
            amounts = [float(t.amount) for t in txns]
            avg_amount = sum(amounts) / len(amounts)
            if max(amounts) - min(amounts) < avg_amount * 0.15:  # amounts are consistent
                subscriptions.append({"name": key, "avg_amount": round(avg_amount, 2), "occurrences": len(txns)})

    # Month-over-month comparison
    month_totals: dict[str, float] = defaultdict(float)
    for t in expenses:
        month_totals[_month_key(t.transaction_date)] += float(t.amount)
    sorted_months = sorted(month_totals.items())

    # Outlier expenses (more than 2x the average transaction size)
    avg_txn = total_expense / len(expenses) if expenses else 0
    outliers = sorted(
        [{"description": t.description, "amount": float(t.amount), "date": t.transaction_date.isoformat()}
         for t in expenses if avg_txn > 0 and float(t.amount) > avg_txn * 3],
        key=lambda x: -x["amount"],
    )[:5]

    savings_rate = ((total_income - total_expense) / total_income * 100) if total_income > 0 else 0.0

    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "savings_rate_pct": round(savings_rate, 2),
        "top_categories": [{"name": n, "total": round(v, 2)} for n, v in top_categories],
        "weekend_spend": round(weekend_total, 2),
        "weekday_spend": round(weekday_total, 2),
        "likely_subscriptions": subscriptions[:10],
        "monthly_totals": [{"month": m, "total": round(v, 2)} for m, v in sorted_months],
        "outlier_expenses": outliers,
    }


def rule_based_insights(stats: dict) -> list[str]:
    """Generate plain-language insight strings without calling any LLM."""
    insights = []

    if stats["savings_rate_pct"] < 0:
        insights.append("You spent more than you earned this period — expenses exceeded income.")
    elif stats["savings_rate_pct"] < 10:
        insights.append(f"Your savings rate is {stats['savings_rate_pct']}%, which is fairly low. Aim for 20%+.")
    else:
        insights.append(f"Nice work — your savings rate is {stats['savings_rate_pct']}%.")

    if stats["top_categories"]:
        top = stats["top_categories"][0]
        insights.append(f"Your biggest expense category is {top['name']} at {top['total']}.")

    if stats["weekend_spend"] > stats["weekday_spend"] * 0.4:
        insights.append("A significant portion of your spending happens on weekends.")

    if stats["likely_subscriptions"]:
        names = ", ".join(s["name"].title() for s in stats["likely_subscriptions"][:3])
        insights.append(f"You may have recurring subscriptions worth reviewing: {names}.")

    if stats["outlier_expenses"]:
        oe = stats["outlier_expenses"][0]
        insights.append(f"Unusually large expense detected: '{oe['description']}' for {oe['amount']}.")

    return insights
