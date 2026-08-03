def test_hello(client):
    resp = client.get("/hello")
    assert resp.status_code == 200


def test_index_redirects_to_departure(client):
    resp = client.get("/")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/departure"


def test_departure_page_renders(client):
    resp = client.get("/departure")
    assert resp.status_code == 200
