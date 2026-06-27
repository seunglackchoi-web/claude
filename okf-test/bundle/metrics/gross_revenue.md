---
type: Metric
title: Gross Revenue
description: Total booked revenue before refunds.
tags: [sales, revenue, finance]
timestamp: 2026-03-02T09:00:00Z
---
# Gross Revenue

Sum of [orders](/tables/orders.md).`total_amount` over completed orders.

```sql
SELECT SUM(total_amount) AS gross_revenue
FROM `acme.sales_db.orders`
WHERE status = 'completed'
```

Gross only — refunds are not subtracted. Finance reports net; do not confuse.
