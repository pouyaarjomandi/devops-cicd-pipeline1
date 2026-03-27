from flask import Flask, jsonify, request
import os

app = Flask(__name__)

# Sample product data (simulating a database)
products = [
    {"id": 1, "name": "Wireless Headphones", "price": 59.99, "stock": 120},
    {"id": 2, "name": "USB-C Hub", "price": 34.99, "stock": 85},
    {"id": 3, "name": "Mechanical Keyboard", "price": 89.99, "stock": 45},
    {"id": 4, "name": "Monitor Stand", "price": 29.99, "stock": 200},
    {"id": 5, "name": "Laptop Sleeve", "price": 19.99, "stock": 150},
]


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "E-Commerce Product API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "status": "running",
        "environment": os.getenv("FLASK_ENV", "development")
    })


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200


@app.route("/ready", methods=["GET"])
def readiness_check():
    return jsonify({"status": "ready"}), 200


@app.route("/api/products", methods=["GET"])
def get_products():
    return jsonify({"products": products, "total": len(products)}), 200


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        return jsonify(product), 200
    return jsonify({"error": "Product not found"}), 404


@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json()

    if not data or "name" not in data or "price" not in data:
        return jsonify({"error": "Missing required fields: name, price"}), 400

    new_product = {
        "id": max(p["id"] for p in products) + 1 if products else 1,
        "name": data["name"],
        "price": float(data["price"]),
        "stock": int(data.get("stock", 0))
    }
    products.append(new_product)
    return jsonify(new_product), 201


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
