"""Funnel analysis of the Retailrocket e-commerce dataset.

Usage:
    python funnel_analysis.py path/to/events.csv

Writes results/funnel_summary.md, results/funnel_chart.png and results/hourly_view_to_cart.csv.
Every rate is reported with its numerator and denominator so the definition is unambiguous.
"""
import sqlite3
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

OUT = Path("results")


def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=["timestamp", "visitorid", "event", "itemid", "transactionid"])
    df = df.drop_duplicates()  # exact duplicate rows add nothing to a funnel
    df = df[df["event"].isin(["view", "addtocart", "transaction"])]
    return df


def pct(num: int, den: int) -> float:
    return round(100 * num / den, 2) if den else 0.0


def run(path: str) -> None:
    OUT.mkdir(exist_ok=True)
    df = load(path)
    con = sqlite3.connect(":memory:")
    df.to_sql("events", con, index=False)

    queries = Path(__file__).with_name("queries.sql").read_text().split(";")
    q = [s.strip() for s in queries if "SELECT" in s]

    ev = dict(con.execute(q[0]).fetchall())
    viewers, carters, buyers = con.execute(q[1]).fetchone()
    viewed_pairs, viewed_carted, carted_bought = con.execute(q[2]).fetchone()
    hourly = pd.read_sql(q[3], con)
    hourly.to_csv(OUT / "hourly_view_to_cart.csv", index=False)

    views, carts, txns = ev.get("view", 0), ev.get("addtocart", 0), ev.get("transaction", 0)
    rows = [
        ("Event-level", "View -> add-to-cart", carts, views),
        ("Event-level", "Add-to-cart -> transaction", txns, carts),
        ("Event-level", "Cart abandonment (1 - above)", carts - txns, carts),
        ("Visitor-level", "Viewers who added to cart", carters, viewers),
        ("Visitor-level", "Carters who bought", buyers, carters),
        ("Visitor-level", "Viewers who bought", buyers, viewers),
        ("Visitor-item", "Viewed items that were carted", viewed_carted, viewed_pairs),
        ("Visitor-item", "Carted items that were bought", carted_bought, viewed_carted),
    ]

    lines = [
        "# Funnel summary",
        "",
        f"Events analysed: **{len(df):,}** from **{df['visitorid'].nunique():,}** visitors "
        f"and **{df['itemid'].nunique():,}** items.",
        "",
        "| Level | Metric | Numerator | Denominator | Rate |",
        "| --- | --- | --- | --- | --- |",
    ]
    lines += [f"| {lvl} | {m} | {n:,} | {d:,} | {pct(n, d)}% |" for lvl, m, n, d in rows]
    lines += [
        "",
        "Note: Retailrocket has no checkout-start or payment events, so 'transaction' is the only purchase signal, "
        "and event-level abandonment is an approximation (one transaction can follow several cart events).",
    ]
    (OUT / "funnel_summary.md").write_text("\n".join(lines))

    fig, ax = plt.subplots(figsize=(7, 3.5))
    stages, counts = ["Viewers", "Added to cart", "Bought"], [viewers, carters, buyers]
    ax.barh(stages[::-1], counts[::-1], color="#1F3A5F")
    for i, c in enumerate(counts[::-1]):
        ax.text(c, i, f"  {c:,} ({pct(c, viewers)}%)", va="center", fontsize=9)
    ax.set_xlabel("Distinct visitors")
    ax.set_title("Visitor funnel: share of viewers reaching each stage")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(0, viewers * 1.35)
    fig.tight_layout()
    fig.savefig(OUT / "funnel_chart.png", dpi=150)

    print((OUT / "funnel_summary.md").read_text())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python funnel_analysis.py path/to/events.csv")
    run(sys.argv[1])
