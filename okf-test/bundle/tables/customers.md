---
type: BigQuery Table
title: Customers
description: One row per registered customer.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales_db&t=customers
tags: [sales, pii]
timestamp: 2026-05-28T14:30:00Z
---
# Customers

One row per registered customer. `email` is PII and governed.

## Schema
| Column | Type | Description |
|---|---|---|
| customer_id | STRING | Globally unique customer identifier |
| email | STRING | Login email (PII, governed) |
| country | STRING | ISO-3166 alpha-2 country code |
| created_at | TIMESTAMP | Signup time |
