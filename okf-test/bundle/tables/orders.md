---
type: BigQuery Table
title: Orders
description: One row per completed customer order.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales_db&t=orders
tags: [sales, revenue]
timestamp: 2026-03-02T09:00:00Z
---
# Orders

One row per *completed* order. Cancelled carts never land here. Joins to
[customers](/tables/customers.md) on `customer_id` and to
[order_items](/tables/order_items.md) on `order_id`. Payment details live in
[payments](/tables/payments.md).

## Schema
| Column | Type | Description |
|---|---|---|
| order_id | STRING | Globally unique order identifier |
| customer_id | STRING | FK to [customers](/tables/customers.md) |
| status | STRING | Always 'completed' in this table |
| total_amount | NUMERIC | Order total in USD, before refunds |
| created_at | TIMESTAMP | When the order was placed |

## Notes
`total_amount` is gross. For net revenue subtract refunds (not modeled here yet).
