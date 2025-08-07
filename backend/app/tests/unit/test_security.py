"""
Unit tests for security functions
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import jwt
import pytest

from app.core.security import (
    SecurityHeaders,
    create_access_token,
    generate_secure_token,
    get_password_hash,
    is_safe_url,
    sanitize_input,
    validate_password_strength,
    verify_password,
    verify_token,
)


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_password_hash_and_verify(self):
        """Test password hashing and verification"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        # Hash should not be the same as password
        assert hashed != password

        # Verification should work
        assert verify_password(password, hashed) is True

        # Wrong password should fail
        assert verify_password("WrongPassword", hashed) is False

    def test_password_hash_different_each_time(self):
        """Test that password hashing produces different hashes each time"""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different due to salt
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_verify_password_with_invalid_hash(self):
        """Test password verification with invalid hash"""
        password = "TestPassword123!"
        invalid_hash = "invalid_hash"

        # Should return False for invalid hash
        assert verify_password(password, invalid_hash) is False


class TestJWTTokens:
    """Test JWT token creation and verification"""

    @patch("app.core.security.get_secret_key")
    def test_create_and_verify_token(self, mock_get_secret_key):
        """Test token creation and verification"""
        mock_get_secret_key.return_value = "test_secret_key_32_characters_long"

        data = {"sub": "user123", "role": "user"}
        token = create_access_token(data)

        # Token should be a string
        assert isinstance(token, str)

        # Verify token
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["role"] == "user"
        assert "exp" in payload

    @patch("app.core.security.get_secret_key")
    def test_token_with_custom_expiry(self, mock_get_secret_key):
        """Test token creation with custom expiry"""
        mock_get_secret_key.return_value = "test_secret_key_32_characters_long"

        data = {"sub": "user123"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta)

        payload = verify_token(token)
        assert payload is not None

        # Check expiry is approximately correct (within 1 minute)
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_exp = datetime.utcnow() + expires_delta
        assert abs((exp_time - expected_exp).total_seconds()) < 60

    @patch("app.core.security.get_secret_key")
    def test_verify_invalid_token(self, mock_get_secret_key):
        """Test verification of invalid token"""
        mock_get_secret_key.return_value = "test_secret_key_32_characters_long"

        # Invalid token should return None
        assert verify_token("invalid_token") is None
        assert verify_token("") is None
        assert verify_token(None) is None

    @patch("app.core.security.get_secret_key")
    def test_verify_expired_token(self, mock_get_secret_key):
        """Test verification of expired token"""
        mock_get_secret_key.return_value = "test_secret_key_32_characters_long"

        # Create token that expires immediately
        data = {"sub": "user123"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta)

        # Should return None for expired token
        assert verify_token(token) is None


class TestPasswordValidation:
    """Test password strength validation"""

    def test_valid_passwords(self):
        """Test valid passwords"""
        valid_passwords = ["Password123!", "MySecure@Pass1", "Complex#Password9", "Strong$Pass123"]

        for password in valid_passwords:
            assert validate_password_strength(password) is True

    def test_invalid_passwords(self):
        """Test invalid passwords"""
        invalid_passwords = [
            "short",  # Too short
            "nouppercase123!",  # No uppercase
            "NOLOWERCASE123!",  # No lowercase
            "NoNumbers!",  # No numbers
            "NoSpecialChars123",  # No special characters
            "password",  # Too simple
            "",  # Empty
        ]

        for password in invalid_passwords:
            assert validate_password_strength(password) is False


class TestSecureTokenGeneration:
    """Test secure token generation"""

    def test_generate_secure_token_default_length(self):
        """Test secure token generation with default length"""
        token = generate_secure_token()

        # Should be a string
        assert isinstance(token, str)

        # Should have reasonable length (URL-safe base64 encoding)
        assert len(token) > 40  # 32 bytes -> ~43 chars in base64

    def test_generate_secure_token_custom_length(self):
        """Test secure token generation with custom length"""
        token = generate_secure_token(16)

        assert isinstance(token, str)
        assert len(token) > 20  # 16 bytes -> ~22 chars in base64

    def test_generate_secure_token_uniqueness(self):
        """Test that generated tokens are unique"""
        tokens = [generate_secure_token() for _ in range(10)]

        # All tokens should be unique
        assert len(set(tokens)) == 10


class TestInputSanitization:
    """Test input sanitization"""

    def test_sanitize_normal_input(self):
        """Test sanitization of normal input"""
        input_str = "Hello World"
        result = sanitize_input(input_str)
        assert result == "Hello World"

    def test_sanitize_dangerous_characters(self):
        """Test sanitization of dangerous characters"""
        input_str = "Hello<script>alert('xss')</script>World"
        result = sanitize_input(input_str)
        assert "<" not in result
        assert ">" not in result
        assert "script" in result  # Content should remain, just tags removed

    def test_sanitize_null_bytes(self):
        """Test sanitization of null bytes"""
        input_str = "Hello\x00World"
        result = sanitize_input(input_str)
        assert "\x00" not in result
        assert result == "HelloWorld"

    def test_sanitize_long_input(self):
        """Test sanitization of long input"""
        input_str = "A" * 2000
        result = sanitize_input(input_str, max_length=100)
        assert len(result) == 100

    def test_sanitize_non_string_input(self):
        """Test sanitization of non-string input"""
        assert sanitize_input(123) == ""
        assert sanitize_input(None) == ""
        assert sanitize_input([]) == ""


class TestURLValidation:
    """Test URL safety validation"""

    def test_safe_urls(self):
        """Test safe URLs"""
        safe_urls = [
            "https://example.com",
            "http://localhost:8000",
            "https://api.telegram.org",
            "http://192.168.1.1:3000",
        ]

        for url in safe_urls:
            assert is_safe_url(url) is True

    def test_unsafe_urls(self):
        """Test unsafe URLs"""
        unsafe_urls = [
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "vbscript:msgbox('xss')",
            "file:///etc/passwd",
            "ftp://example.com",
            "",
            None,
        ]

        for url in unsafe_urls:
            assert is_safe_url(url) is False


class TestSecurityHeaders:
    """Test security headers"""

    def test_get_security_headers(self):
        """Test security headers generation"""
        headers = SecurityHeaders.get_security_headers()

        # Should be a dictionary
        assert isinstance(headers, dict)

        # Should contain expected headers
        expected_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "Referrer-Policy",
        ]

        for header in expected_headers:
            assert header in headers
            assert isinstance(headers[header], str)
            assert len(headers[header]) > 0

    def test_security_headers_values(self):
        """Test security headers have correct values"""
        headers = SecurityHeaders.get_security_headers()

        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"
        assert "max-age" in headers["Strict-Transport-Security"]


# Integration tests for security functions
class TestSecurityIntegration:
    """Integration tests for security functions"""

    @patch("app.core.security.get_secret_key")
    def test_full_auth_flow(self, mock_get_secret_key):
        """Test full authentication flow"""
        mock_get_secret_key.return_value = "test_secret_key_32_characters_long"

        # 1. Hash password
        password = "TestPassword123!"
        hashed_password = get_password_hash(password)

        # 2. Verify password
        assert verify_password(password, hashed_password) is True

        # 3. Create token
        user_data = {"sub": "user123", "role": "user"}
        token = create_access_token(user_data)

        # 4. Verify token
        payload = verify_token(token)
        assert payload["sub"] == "user123"
        assert payload["role"] == "user"

    def test_input_sanitization_and_validation(self):
        """Test input sanitization combined with validation"""
        # Sanitize potentially dangerous input
        user_input = "Hello<script>alert('xss')</script>World!"
        sanitized = sanitize_input(user_input)

        # Should be safe now
        assert "<script>" not in sanitized
        assert "alert" not in sanitized

        # Test password validation on sanitized input
        password_input = "Password123!<script>"
        sanitized_password = sanitize_input(password_input)

        # Should still be a valid password after sanitization
        assert validate_password_strength(sanitized_password) is True
