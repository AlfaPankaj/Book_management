def test_create_book(client):
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "summary": "This is a test book."
    }
    response = client.post("/api/v1/books/", json=book_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == book_data["title"]
    assert data["author"] == book_data["author"]
    assert data["id"] == 1

def test_read_books(client):
    response = client.get("/api/v1/books/")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)

def test_read_book_by_id(client):
    # First create a book
    book_data = {
        "title": "Test Book 2",
        "author": "Test Author 2",
        "summary": "Another test book."
    }
    response = client.post("/api/v1/books/", json=book_data)
    assert response.status_code == 200
    book_id = response.json()["id"]

    # Then retrieve it
    response = client.get(f"/api/v1/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == book_data["title"]