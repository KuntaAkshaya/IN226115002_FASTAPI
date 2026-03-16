# FastAPI Internship — Assignment 2

## Overview

This assignment demonstrates the implementation and testing of multiple FastAPI endpoints for product management, filtering, validation, and bulk order processing.

All APIs were tested using Swagger UI available at `/docs`.

## Implemented Features

### Q1 — Product Filtering

* Endpoint: `/products/filter`
* Supports filtering products by:

  * `min_price`
  * `max_price`
* Example:

  * `/products/filter?min_price=400` → Returns **Wireless Mouse** and **USB Hub**
  * `/products/filter?min_price=100&max_price=600` → Returns **Wireless Mouse**

### Q2 — Product Price Endpoint

* Endpoint: `/products/{product_id}/price`
* Returns **only product name and price**
* Example:

  * `/products/1/price` → Returns name and price
  * `/products/99/price` → Returns **Product not found error**

### Q3 — Feedback Validation

* Endpoint: `POST /feedback`
* Input validation implemented using FastAPI.
* Example:

  * `rating = 6` → Returns **422 validation error**
  * Valid rating → Feedback saved successfully
* `comment` field is optional.

### Q4 — Product Summary

* Endpoint: `/products/summary`
* Returns store statistics including:

  * Total products
  * In-stock products
  * Out-of-stock products
  * Most expensive product
  * Cheapest product

### Q5 — Bulk Order Processing

* Endpoint: `POST /orders/bulk`
* Handles multiple product orders in a single request.
* Features:

  * Valid orders added to **confirmed list**
  * Out-of-stock items added to **failed list**
  * Calculates **grand total** for confirmed orders

### Bonus Feature

* New orders initially created with **status: pending**
* Endpoint to update status:

  * `PATCH /confirm`
* Changes order status from **pending → confirmed**

## Testing

All endpoints were tested using Swagger UI:
`/docs`

Output screenshots are included in this repository.

## Technologies Used

* FastAPI
* Python
* Swagger UI
* REST API concepts

## Author

Submitted as part of **FastAPI Internship Assignment**
By Akshaya 
