from app import app

client = app.test_client()

def test_home_route():
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode() == "Welcome to Pytest"

def test_add_route():
    response = client.get('/add/10/20')
    assert response.status_code == 200
    assert response.data.decode() == '20'