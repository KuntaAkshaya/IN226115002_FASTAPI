# FastAPI Internship — Assignment 3

## Overview

This assignment focuses on implementing and testing CRUD operations, product auditing, and bulk updates using FastAPI. All endpoints were tested using Swagger UI available at `/docs`.

---

## Implemented Tasks

### Q1 — Add Products

Endpoint: `POST /products`

* Added **Laptop Stand** with ID `5` (Status: 201)
* Added **Sticky Notes** with ID `6` (Status: 201)
* Attempting to add duplicate product **Wireless Mouse** returns **400 Duplicate Error**

---

### Q2 — Update Products

Endpoint: `PUT /products/{product_id}`

Features implemented:

* `PUT /products/3?in_stock=true` → Restocks **USB Hub**
* `PUT /products/3?in_stock=true&price=649` → Updates both stock and price
* `PUT /products/99?price=100` → Returns **404 Not Found**

---

### Q3 — Delete Products

Endpoint: `DELETE /products/{product_id}`

* `DELETE /products/4` → Removes **Pen Set** and confirms deletion
* Deleting the same product again returns **404 Not Found**

---

### Q4 — Full CRUD Lifecycle

Complete **Create → Read → Update → Delete** lifecycle implemented using the example product **Smart Watch**.

Steps tested:

1. Create product
2. Retrieve product
3. Update product
4. Verify updates
5. Delete product
6. Confirm deletion

---

### Q5 — Product Audit

Endpoint: `GET /products/audit`

Returns:

* Total number of products
* In-stock product count
* Out-of-stock product count
* Total stock value
* Most expensive product

Important:
The `/products/audit` endpoint is placed **above `/products/{product_id}`** to avoid routing conflicts.

---

### Bonus Feature — Bulk Discount

Endpoint: `PUT /products/discount`

Example:

`/products/discount?category=Electronics&discount_percent=10`

Functionality:

* Applies discount to **all products in the Electronics category**
* Updates prices dynamically.

---

## Testing

All APIs were tested using **Swagger UI** available at:

`/docs`

Screenshots of all outputs are included in this repository.

---

## Technologies Used

* Python
* FastAPI
* Swagger UI
* REST API concepts

---

## Author

Submitted as part of **FastAPI Internship Training — Assignment 3 (Day 4)**.

