---
type: BigQuery Table
title: Order Items
description: Line items, one row per product per order.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales_db&t=order_items
tags: [sales]
timestamp: 2026-05-28T14:30:00Z
---
# Order Items

One row per product per [order](/tables/orders.md).

## Schema
| Column | Type | Description |
|---|---|---|
| order_id | STRING | FK to [orders](/tables/orders.md) |
| product_id | STRING | Product SKU |
| quantity | INT64 | Units purchased |
| unit_price | NUMERIC | Price per unit in USD |
