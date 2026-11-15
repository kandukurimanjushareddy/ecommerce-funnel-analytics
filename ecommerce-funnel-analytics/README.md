# Fashion E-commerce Customer Journey & Funnel Analytics

Where do online shoppers drop off between viewing a product, adding it to the cart and buying it?
This project measures the funnel on the public **Retailrocket** e-commerce dataset, finds the biggest drop-off,
and turns it into product recommendations.

**Tools:** Python (Pandas), SQL (SQLite), Matplotlib, Power BI (dashboard)

## Data
[Retailrocket e-commerce dataset (Kaggle)](https://www.kaggle.com/retailrocket/ecommerce-dataset), `events.csv`:
about 4.5 months of real behaviour from an e-commerce site.

| Column | Meaning |
| --- | --- |
| `timestamp` | Event time, Unix milliseconds |
| `visitorid` | Anonymised visitor |
| `event` | `view`, `addtocart` or `transaction` |
| `itemid` | Anonymised product |
| `transactionid` | Set only for `transaction` events |

## Metric definitions (numerator ÷ denominator)
Every rate is reported three ways, because each answers a different question:

| Level | Metric | Definition |
| --- | --- | --- |
| Event | View → add-to-cart | `addtocart` events ÷ `view` events |
| Event | Add-to-cart → transaction | `transaction` events ÷ `addtocart` events |
| Event | Cart abandonment | 1 − (transactions ÷ add-to-carts), an approximation |
| Visitor | Viewers who carted / bought | distinct visitors at the stage ÷ distinct viewers |
| Visitor-item | Viewed items carted / carted items bought | visitor–item pairs reaching the next stage |

**Limitation:** the dataset has no checkout-start or payment events, so `transaction` is the only purchase signal.
Event-level abandonment is approximate, because one purchase can follow several add-to-cart events.

## Run it
```bash
pip install -r requirements.txt
# put events.csv in data/
python funnel_analysis.py data/events.csv
```
Outputs in `results/`: `funnel_summary.md` (all rates with numerators and denominators),
`funnel_chart.png` (visitor funnel), `hourly_view_to_cart.csv` (drop-off by hour).
The SQL behind every number is in [`queries.sql`](queries.sql).

## Findings
See [`results/funnel_summary.md`](results/funnel_summary.md). The biggest drop-off is view → add-to-cart:
only a small share of product views lead to a cart.

## Product recommendations
1. **Size and fit confidence on the product page:** show the recommended size and fit notes next to Add to cart. Uncertainty about size is a common reason to view a product and leave.
2. **Wishlist-to-cart nudges:** remind shoppers about viewed items when the price drops or stock is low.
3. **Cart recovery:** for abandoned carts, send a reminder within 24 hours that shows delivery date and return policy.

Related: [Myntra product teardown on size & fit returns](https://claude.ai/artifact/5fD6XRbjzda8i1pjRqobfW)
