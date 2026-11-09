import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.auth import hash_password, verify_password, create_access_token, decode_access_token
from fastapi import HTTPException

class TestAuthModule(unittest.TestCase):
    def test_password_hashing_and_verification(self):
        pwd = "SecretPassword123!"
        hashed = hash_password(pwd)
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_token_creation_and_decoding(self):
        payload = {"sub": "alice", "role": "admin"}
        token = create_access_token(payload, expires_in_seconds=60)
        decoded = decode_access_token(token)
        self.assertEqual(decoded["sub"], "alice")
        self.assertEqual(decoded["role"], "admin")

    def test_token_expiration(self):
        payload = {"sub": "bob"}
        token = create_access_token(payload, expires_in_seconds=-10)
        with self.assertRaises(HTTPException):
            decode_access_token(token)
