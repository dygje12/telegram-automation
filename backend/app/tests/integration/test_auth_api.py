"""
Integration tests for authentication API endpoints
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestAuthEndpoints:
    """Test authentication API endpoints"""

    def test_register_user_success(self, client, sample_user_data):
        """Test successful user registration"""
        response = client.post("/api/v1/auth/register", json=sample_user_data)

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["phone_number"] == sample_user_data["phone_number"]
        assert "password" not in data["user"]  # Password should not be returned

    def test_register_user_duplicate_phone(self, client, sample_user_data):
        """Test registration with duplicate phone number"""
        # Register first user
        response1 = client.post("/api/v1/auth/register", json=sample_user_data)
        assert response1.status_code == 200

        # Try to register with same phone number
        response2 = client.post("/api/v1/auth/register", json=sample_user_data)
        assert response2.status_code == 400

        data = response2.json()
        assert "error" in data
        assert "already exists" in data["error"].lower()

    def test_register_user_invalid_data(self, client):
        """Test registration with invalid data"""
        invalid_data = {
            "phone_number": "invalid",
            "password": "weak",
            "first_name": "",
            "last_name": "",
        }

        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422

        data = response.json()
        assert "details" in data

    def test_login_success(self, client, sample_user_data):
        """Test successful login"""
        # Register user first
        client.post("/api/v1/auth/register", json=sample_user_data)

        # Login
        login_data = {
            "phone_number": sample_user_data["phone_number"],
            "password": sample_user_data["password"],
        }

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    def test_login_invalid_credentials(self, client, sample_user_data):
        """Test login with invalid credentials"""
        # Register user first
        client.post("/api/v1/auth/register", json=sample_user_data)

        # Try login with wrong password
        login_data = {
            "phone_number": sample_user_data["phone_number"],
            "password": "wrong_password",
        }

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401

        data = response.json()
        assert "error" in data

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        login_data = {"phone_number": "+1234567890", "password": "password123"}

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401

        data = response.json()
        assert "error" in data

    @patch("app.services.telegram_service.TelegramService.request_code")
    def test_request_code_success(self, mock_request_code, client, auth_headers):
        """Test successful code request"""
        mock_request_code.return_value = {"success": True, "phone_code_hash": "test_hash"}

        response = client.post(
            "/api/v1/auth/request-code", json={"phone_number": "+1234567890"}, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "phone_code_hash" in data

    @patch("app.services.telegram_service.TelegramService.request_code")
    def test_request_code_telegram_error(self, mock_request_code, client, auth_headers):
        """Test code request with Telegram error"""
        mock_request_code.side_effect = Exception("Telegram API error")

        response = client.post(
            "/api/v1/auth/request-code", json={"phone_number": "+1234567890"}, headers=auth_headers
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_request_code_unauthorized(self, client):
        """Test code request without authentication"""
        response = client.post("/api/v1/auth/request-code", json={"phone_number": "+1234567890"})

        assert response.status_code == 401

    @patch("app.services.telegram_service.TelegramService.verify_code")
    def test_verify_code_success(self, mock_verify_code, client, auth_headers):
        """Test successful code verification"""
        mock_verify_code.return_value = {
            "success": True,
            "user": {"id": 123456789, "first_name": "Test", "last_name": "User"},
        }

        verify_data = {
            "phone_number": "+1234567890",
            "code": "12345",
            "phone_code_hash": "test_hash",
        }

        response = client.post("/api/v1/auth/verify-code", json=verify_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "user" in data

    @patch("app.services.telegram_service.TelegramService.verify_code")
    def test_verify_code_invalid(self, mock_verify_code, client, auth_headers):
        """Test code verification with invalid code"""
        mock_verify_code.side_effect = Exception("Invalid code")

        verify_data = {
            "phone_number": "+1234567890",
            "code": "00000",
            "phone_code_hash": "test_hash",
        }

        response = client.post("/api/v1/auth/verify-code", json=verify_data, headers=auth_headers)

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    @patch("app.services.telegram_service.TelegramService.verify_2fa")
    def test_verify_2fa_success(self, mock_verify_2fa, client, auth_headers):
        """Test successful 2FA verification"""
        mock_verify_2fa.return_value = {"success": True, "session": "test_session_data"}

        verify_data = {"password": "2fa_password"}

        response = client.post("/api/v1/auth/verify-2fa", json=verify_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_logout_success(self, client, auth_headers):
        """Test successful logout"""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_logout_unauthorized(self, client):
        """Test logout without authentication"""
        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 401

    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "phone_number" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "password" not in data

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401


class TestAuthRateLimiting:
    """Test rate limiting on auth endpoints"""

    def test_login_rate_limiting(self, client, sample_user_data):
        """Test rate limiting on login endpoint"""
        # Register user first
        client.post("/api/v1/auth/register", json=sample_user_data)

        login_data = {
            "phone_number": sample_user_data["phone_number"],
            "password": "wrong_password",
        }

        # Make multiple failed login attempts
        responses = []
        for _ in range(10):  # Exceed rate limit
            response = client.post("/api/v1/auth/login", json=login_data)
            responses.append(response)

        # Should eventually get rate limited
        rate_limited = any(r.status_code == 429 for r in responses)
        assert rate_limited, "Rate limiting should be triggered after multiple failed attempts"

    def test_register_rate_limiting(self, client):
        """Test rate limiting on register endpoint"""
        responses = []

        # Make multiple registration attempts
        for i in range(10):
            user_data = {
                "phone_number": f"+123456789{i}",
                "password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "User",
            }
            response = client.post("/api/v1/auth/register", json=user_data)
            responses.append(response)

        # Should eventually get rate limited
        rate_limited = any(r.status_code == 429 for r in responses)
        assert (
            rate_limited
        ), "Rate limiting should be triggered after multiple registration attempts"


class TestAuthSecurity:
    """Test security aspects of auth endpoints"""

    def test_password_not_returned(self, client, sample_user_data):
        """Test that password is never returned in responses"""
        # Register
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert response.status_code == 200
        data = response.json()
        assert "password" not in str(data)

        # Login
        login_data = {
            "phone_number": sample_user_data["phone_number"],
            "password": sample_user_data["password"],
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "password" not in str(data)

    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection"""
        malicious_data = {"phone_number": "'; DROP TABLE users; --", "password": "password123"}

        response = client.post("/api/v1/auth/login", json=malicious_data)
        # Should not crash the server
        assert response.status_code in [400, 401, 422]

    def test_xss_protection(self, client):
        """Test protection against XSS"""
        malicious_data = {
            "phone_number": "+1234567890",
            "password": "password123",
            "first_name": "<script>alert('xss')</script>",
            "last_name": "<img src=x onerror=alert('xss')>",
        }

        response = client.post("/api/v1/auth/register", json=malicious_data)

        if response.status_code == 200:
            data = response.json()
            # Script tags should be sanitized
            assert "<script>" not in str(data)
            assert "onerror" not in str(data)


class TestAuthValidation:
    """Test input validation on auth endpoints"""

    def test_phone_number_validation(self, client):
        """Test phone number validation"""
        invalid_phones = [
            "",
            "123",
            "not_a_phone",
            "+",
            "123456789012345678901234567890",  # Too long
        ]

        for phone in invalid_phones:
            user_data = {
                "phone_number": phone,
                "password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "User",
            }

            response = client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code == 422

    def test_password_validation(self, client):
        """Test password validation"""
        weak_passwords = [
            "",
            "123",
            "password",
            "PASSWORD",
            "Password",
            "Password123",
            "password123!",
        ]

        for password in weak_passwords:
            user_data = {
                "phone_number": "+1234567890",
                "password": password,
                "first_name": "Test",
                "last_name": "User",
            }

            response = client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code == 422

    def test_name_validation(self, client):
        """Test name validation"""
        invalid_names = ["", "A" * 100, "123", "Name123", "Name@#$"]  # Too long

        for name in invalid_names:
            user_data = {
                "phone_number": "+1234567890",
                "password": "TestPassword123!",
                "first_name": name,
                "last_name": "User",
            }

            response = client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code == 422
