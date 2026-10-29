HEADERS = {"X-API-Key": "test-only-key"}

def sample_product(sku="SKU-001"):
    return {"sku": sku, "name": "Apple Keyboard", "description": "Mechanical keyboard", "price": "49.99", "stock": 10, "category": "Accessories"}

def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}

def test_crud_flow(client):
    created = client.post("/products", json=sample_product(), headers=HEADERS)
    assert created.status_code == 201
    product_id = created.json()["id"]
    assert created.headers["location"] == f"/products/{product_id}"
    assert client.get(f"/products/{product_id}").json()["name"] == "Apple Keyboard"
    updated = client.patch(f"/products/{product_id}", json={"stock": 7}, headers=HEADERS)
    assert updated.status_code == 200
    assert updated.json()["stock"] == 7
    assert client.delete(f"/products/{product_id}", headers=HEADERS).status_code == 204
    assert client.get(f"/products/{product_id}").status_code == 404

def test_duplicate_sku(client):
    assert client.post("/products", json=sample_product(), headers=HEADERS).status_code == 201
    assert client.post("/products", json=sample_product(), headers=HEADERS).status_code == 409

def test_invalid_product(client):
    data = sample_product()
    data["price"] = "-10"
    assert client.post("/products", json=data, headers=HEADERS).status_code == 422

def test_admin_access_required(client):
    assert client.post("/products", json=sample_product()).status_code == 401

def test_pagination_and_filtering(client):
    for i in range(3):
        data = sample_product(f"SKU-{i}")
        data["name"] = f"Apple item {i}" if i < 2 else "Banana item"
        assert client.post("/products", json=data, headers=HEADERS).status_code == 201
    response = client.get("/products?limit=1&offset=0&name=Apple")
    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert len(response.json()["items"]) == 1
    assert client.get("/products?limit=101").status_code == 422

def test_missing_product(client):
    assert client.patch("/products/999", json={"stock": 2}, headers=HEADERS).status_code == 404
    assert client.delete("/products/999", headers=HEADERS).status_code == 404
