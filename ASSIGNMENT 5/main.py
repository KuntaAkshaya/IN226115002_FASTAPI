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


class Checkout(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)

# --------------------------------------------------
# ASSIGNMENT 1
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

# --------------------------------------------------
# ASSIGNMENT 2
# --------------------------------------------------

@app.get("/products/filter")
def filter_products(min_price: Optional[int] = None, max_price: Optional[int] = None, category: Optional[str] = None):
    result = products
    if min_price:
        result = [p for p in result if p["price"] >= min_price]
    if max_price:
        result = [p for p in result if p["price"] <= max_price]
    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]
    return {"filtered_products": result}

# --------------------------------------------------
# ASSIGNMENT 3
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
# ASSIGNMENT 4 (CART)
# --------------------------------------------------

cart = []
order_history = []
order_counter = 1


@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):
    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        return {"error": "Product not found"}

    if not product["in_stock"]:
        return {"detail": f"{product['name']} is out of stock"}

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * item["unit_price"]
            return {"message": "Cart updated", "cart_item": item}

    new_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": quantity * product["price"]
    }

    cart.append(new_item)
    return {"message": "Added to cart", "cart_item": new_item}


@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)
    return {"items": cart, "item_count": len(cart), "grand_total": grand_total}


@app.post("/cart/checkout")
def checkout(order: Checkout):
    global order_counter

    if not cart:
        return {"error": "CART_EMPTY"}

    placed_orders = []
    grand_total = 0

    for item in cart:
        record = {
            "order_id": order_counter,
            "customer_name": order.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"]
        }

        order_history.append(record)
        placed_orders.append(record)

        grand_total += item["subtotal"]
        order_counter += 1

    cart.clear()

    return {"orders_placed": placed_orders, "grand_total": grand_total}


@app.get("/orders")
def get_orders():
    return {"orders": order_history, "total_orders": len(order_history)}

# --------------------------------------------------
#  ASSIGNMENT 5 
# --------------------------------------------------

@app.get("/orders/search")
def search_orders(customer_name: str):
    result = [o for o in order_history if customer_name.lower() in o["customer_name"].lower()]
    return {"customer_name": customer_name, "total_found": len(result), "orders": result}


@app.get("/products/sort-by-category")
def sort_by_category():
    sorted_products = sorted(products, key=lambda p: (p["category"].lower(), p["price"]))
    return {"products": sorted_products}


@app.get("/products/browse")
def browse_products(keyword: str = "", sort_by: str = "price", order: str = "asc", page: int = 1, limit: int = 4):

    result = products

    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    total = len(result)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "total_found": total,
        "total_pages": total_pages,
        "products": result[start:end]
    }


@app.get("/orders/page")
def paginate_orders(page: int = 1, limit: int = 3):
    total = len(order_history)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "total_pages": total_pages,
        "orders": order_history[start:end]
    }

# --------------------------------------------------
#  KEEP DYNAMIC ROUTES LAST (ONLY ONCE)
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