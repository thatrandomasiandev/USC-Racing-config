# Testing Guide

## Running Tests

### Install Test Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Files

```bash
# Test authentication
pytest tests/test_auth.py -v

# Test parameters
pytest tests/test_parameters.py -v

# Test user management
pytest tests/test_users.py -v
```

### Run with Coverage

```bash
pip install pytest-cov
pytest tests/ --cov=backend --cov-report=html
```

## Test Structure

- `tests/conftest.py` - Pytest fixtures and configuration
- `tests/test_auth.py` - Authentication and authorization tests
- `tests/test_parameters.py` - Parameter CRUD and queue tests
- `tests/test_users.py` - User management tests

## Writing New Tests

1. Create test file in `tests/` directory
2. Use fixtures from `conftest.py`:
   - `client` - Test client
   - `admin_session` - Authenticated admin session
   - `user_session` - Authenticated user session
   - `test_db` - Temporary database

Example:

```python
def test_new_feature(admin_session):
    response = admin_session.get("/api/new-endpoint")
    assert response.status_code == 200
```

## Continuous Integration

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

See `.github/workflows/test.yml` for CI configuration.
