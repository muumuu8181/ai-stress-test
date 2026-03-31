from jsonpath import find, update, delete

def get_test_data():
    return {
        "store": {
            "book": [
                {"category": "reference", "author": "Nigel Rees", "title": "Sayings of the Century", "price": 8.95},
                {"category": "fiction", "author": "Evelyn Waugh", "title": "Sword of Honour", "price": 12.99},
                {"category": "fiction", "author": "Herman Melville", "title": "Moby Dick", "isbn": "0-553-21311-3", "price": 8.99},
                {"category": "fiction", "author": "J. R. R. Tolkien", "title": "The Lord of the Rings", "isbn": "0-395-19395-8", "price": 22.99}
            ],
            "bicycle": {"color": "red", "price": 19.95}
        }
    }

def test_find_basic():
    data = get_test_data()
    assert find(data, "$.store.bicycle.color") == ["red"]
    assert find(data, "$.store.book[0].title") == ["Sayings of the Century"]
    assert find(data, "$.store.book[-1].title") == ["The Lord of the Rings"]

def test_find_wildcard():
    data = get_test_data()
    assert find(data, "$.store.book[*].author") == ["Nigel Rees", "Evelyn Waugh", "Herman Melville", "J. R. R. Tolkien"]
    assert len(find(data, "$.store.*")) == 2

def test_find_recursive():
    data = get_test_data()
    authors = find(data, "$..author")
    assert len(authors) == 4
    assert "Nigel Rees" in authors

def test_find_slice():
    data = get_test_data()
    assert len(find(data, "$.store.book[0:2]")) == 2
    assert len(find(data, "$.store.book[:2]")) == 2
    assert len(find(data, "$.store.book[-2:]")) == 2

def test_find_filter():
    data = get_test_data()
    cheap_books = find(data, "$.store.book[?(@.price < 10)]")
    assert len(cheap_books) == 2
    assert cheap_books[0]["title"] == "Sayings of the Century"
    assert cheap_books[1]["title"] == "Moby Dick"

def test_find_union():
    data = get_test_data()
    res = find(data, "$.store['bicycle', 'book']")
    assert len(res) == 2

def test_update():
    data = get_test_data()
    update(data, "$.store.bicycle.color", "blue")
    assert data["store"]["bicycle"]["color"] == "blue"

    update(data, "$.store.book[*].price", 0)
    for book in data["store"]["book"]:
        assert book["price"] == 0

def test_delete():
    data = get_test_data()
    delete(data, "$.store.bicycle")
    assert "bicycle" not in data["store"]

    delete(data, "$.store.book[0]")
    assert len(data["store"]["book"]) == 3
    assert data["store"]["book"][0]["author"] == "Evelyn Waugh"
