import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["service"] == "E-Commerce Product API"
    assert data["status"] == "running"


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"


def test_readiness_check(client):
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ready"


def test_get_products(client):
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.get_json()
    assert "products" in data
    assert "total" in data
    assert data["total"] == 5


def test_get_single_product(client):
    response = client.get("/api/products/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Wireless Headphones"
    assert data["price"] == 59.99


def test_get_product_not_found(client):
    response = client.get("/api/products/999")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Product not found"


def test_create_product(client):
    new_product = {
        "name": "Webcam HD",
        "price": 49.99,
        "stock": 30
    }
    response = client.post("/api/products", json=new_product)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Webcam HD"
    assert data["price"] == 49.99


def test_create_product_missing_fields(client):
    response = client.post("/api/products", json={"name": "Test"})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data