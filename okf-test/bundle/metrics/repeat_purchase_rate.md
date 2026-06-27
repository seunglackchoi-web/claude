---
type: Metric
title: Repeat Purchase Rate
description: Share of customers with more than one completed order.
tags: [sales, retention]
timestamp: 2026-05-28T14:30:00Z
---
# Repeat Purchase Rate

```sql
SELECT COUNTIF(n > 1) / COUNT(*) AS repeat_purchase_rate
FROM (
  SELECT customer_id, COUNT(*) AS n
  FROM `acme.sales_db.orders`
  GROUP BY customer_id
)
```

Depends on [orders](/tables/orders.md) and [customers](/tables/customers.md).
