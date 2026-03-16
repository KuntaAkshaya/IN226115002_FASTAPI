from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# --------------------------------------------------
# PRODUCT DATA
# --------------------------------------------------

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

# --------------------------------------------------
# MODELS
# --------------------------------------------------

class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool


class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)


class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str
    items: List[OrderItem]

# --------------------------------------------------
# DAY 1 ENDPOINTS
# --------------------------------------------------

@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):

    result = [p for p in products if p["category"].lower() == category_name.lower()]

    if not result:
        return {"error": "No products found in this category"}

    return {"category": category_name, "products": result}


@app.get("/products/instock")
def get_instock():

    available = [p for p in products if p["in_stock"]]

    return {"in_stock_products": available, "count": len(available)}


@app.get("/store/summary")
def store_summary():

    in_stock = len([p for p in products if p["in_stock"]])
    out_stock = len(products) - in_stock
    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock,
        "out_of_stock": out_stock,
        "categories": categories
    }


@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    results = [p for p in products if keyword.lower() in p["name"].lower()]

    return {"keyword": keyword, "results": results, "total": len(results)}


@app.get("/products/deals")
def get_deals():

    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }

# --------------------------------------------------
# DAY 2 TASKS
# --------------------------------------------------

@app.get("/products/filter")
def filter_products(
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    category: Optional[str] = None
):

    result = products

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    return {"filtered_products": result}


feedback = []

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data)

    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
    }


@app.get("/products/summary")
def product_summary():

    total_products = len(products)

    in_stock_count = len([p for p in products if p["in_stock"]])
    out_of_stock_count = total_products - in_stock_count

    most_expensive = max(products, key=lambda x: x["price"])
    cheapest = min(products, key=lambda x: x["price"])

    categories = list(set([p["category"] for p in products]))

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": most_expensive,
        "cheapest": cheapest,
        "categories": categories
    }


orders = []

@app.post("/orders/bulk")
def bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    total = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
            continue

        if not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
            continue

        subtotal = product["price"] * item.quantity
        total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": total
    }

# --------------------------------------------------
# ASSIGNMENT 3 CRUD
# --------------------------------------------------

@app.post("/products", status_code=201)
def add_product(product: Product):

    for p in products:
        if p["name"].lower() == product.name.lower():
            return {"error": "Duplicate product"}

    new_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {"message": "Product added", "product": new_product}

# --------------------------------------------------
# PRODUCT AUDIT (must be above dynamic routes)
# --------------------------------------------------

@app.get("/products/audit")
def product_audit():

    in_stock_products = [p for p in products if p["in_stock"]]
    out_of_stock_products = [p for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in in_stock_products)

    most_expensive = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_products),
        "out_of_stock_names": [p["name"] for p in out_of_stock_products],
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }

# --------------------------------------------------
# BONUS DISCOUNT
# --------------------------------------------------

@app.put("/products/discount")
def bulk_discount(
    category: str = Query(...),
    discount_percent: int = Query(..., ge=1, le=99)
):

    updated_products = []

    for product in products:

        if product["category"].lower() == category.lower():

            product["price"] = int(product["price"] * (1 - discount_percent / 100))

            updated_products.append(product)

    if not updated_products:
        return {"message": "No products found in this category"}

    return {
        "updated_count": len(updated_products),
        "updated_products": updated_products
    }

# --------------------------------------------------
# DYNAMIC ROUTES
# --------------------------------------------------

@app.get("/products/{product_id}")
def get_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return product

    return {"error": "Product not found"}


@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {"name": product["name"], "price": product["price"]}

    return {"error": "Product not found"}


@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    in_stock: Optional[bool] = None,
    price: Optional[int] = None
):

    for product in products:

        if product["id"] == product_id:

            if in_stock is not None:
                product["in_stock"] = in_stock

            if price is not None:
                product["price"] = price

            return {"message": "Product updated", "product": product}

    return {"error": "Product not found"}


@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for product in products:

        if product["id"] == product_id:

            products.remove(product)

            return {"message": f"Product '{product['name']}' deleted"}

    return {"error": "Product not found"}