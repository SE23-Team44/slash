import pytest
from flask import Flask
from src.modules.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_success(client):
    # Simulate a successful login
    response = client.post('/login', data={
        'username': 'sspatil6',
        'password': 'soham@123'
    })
    print(response.data)  # Debug print
    assert response.status_code == 200
    assert b'Welcome' in response.data

def test_login_failure(client):
    # Simulate a failed login
    response = client.post('/login', data={
        'username': 'invalid_user',
        'password': 'invalid_password'
    })
    print(response.data)  # Debug print
    assert response.status_code == 401
    assert b'Invalid Username or Password' in response.data

def test_login_empty_username(client):
    # Simulate login with empty username
    response = client.post('/login', data={
        'username': '',
        'password': 'some_password'
    })
    print(response.data)  # Debug print
    assert response.status_code == 400
    assert b'Username and Password are required' in response.data

def test_login_empty_password(client):
    # Simulate login with empty password
    response = client.post('/login', data={
        'username': 'some_user',
        'password': ''
    })
    print(response.data)  # Debug print
    assert response.status_code == 400
    assert b'Username and Password are required' in response.data