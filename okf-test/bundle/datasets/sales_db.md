---
type: BigQuery Dataset
title: sales_db
description: The production sales warehouse in BigQuery.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales_db
tags: [sales, production]
timestamp: 2026-05-28T14:30:00Z
---
# sales_db

Owns the canonical [orders](/tables/orders.md), [customers](/tables/customers.md),
and [order_items](/tables/order_items.md) tables. Refreshed hourly from the OLTP
store via Datastream. PII columns are governed; see the data-governance wiki.
