import unittest

from kanban.security import (
    SessionSigner,
    hash_password,
    normalize_email,
    validate_email,
    validate_password,
    verify_password,
)


class PasswordTests(unittest.TestCase):
    def test_password_hash_is_salted_and_verifiable(self):
        first = hash_password("Strong123")
        second = hash_password("Strong123")
        self.assertNotEqual(first, second)
        self.assertTrue(verify_password("Strong123", first))
        self.assertFalse(verify_password("Wrong123", first))

    def test_password_rules_report_missing_groups(self):
        problems = validate_password("short")
        self.assertIn("не менее 8 символов", problems)
        self.assertIn("заглавная буква", problems)
        self.assertIn("цифра", problems)

    def test_email_normalization_and_validation(self):
        self.assertEqual(normalize_email("  Name@Example.COM "), "name@example.com")
        self.assertTrue(validate_email("name@example.com"))
        self.assertFalse(validate_email("not-an-email"))


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.signer = SessionSigner("test-secret")

    def test_session_and_csrf_round_trip(self):
        token, csrf = self.signer.create(42, now=100)
        session = self.signer.verify(token, now=101)
        self.assertIsNotNone(session)
        self.assertEqual(session.user_id, 42)
        self.assertTrue(self.signer.valid_csrf(session, csrf))

    def test_tampered_and_expired_session_is_rejected(self):
        token, _ = self.signer.create(42, now=100)
        self.assertIsNone(self.signer.verify(token + "x", now=101))
        self.assertIsNone(self.signer.verify(token, now=100 + 12 * 60 * 60))


if __name__ == "__main__":
    unittest.main()
