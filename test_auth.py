"""
Test authentication with actual credentials from .env file.
This verifies the case-sensitivity fix works correctly.
"""

import os
import sys
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import after loading .env
sys.path.insert(0, os.path.dirname(__file__))
from app import load_authorized_users, AUTHORIZED_USERS

def test_env_loaded():
    """Test that environment variables are loaded correctly."""
    print("\n" + "="*70)
    print("TEST 1: Environment Variables Loaded")
    print("="*70)

    user1_email = os.getenv('AUTH_USER1_EMAIL')
    user1_password = os.getenv('AUTH_USER1_PASSWORD')
    user2_email = os.getenv('AUTH_USER2_EMAIL')
    user2_password = os.getenv('AUTH_USER2_PASSWORD')

    assert user1_email is not None, "AUTH_USER1_EMAIL not loaded"
    assert user1_password is not None, "AUTH_USER1_PASSWORD not loaded"
    assert user2_email is not None, "AUTH_USER2_EMAIL not loaded"
    assert user2_password is not None, "AUTH_USER2_PASSWORD not loaded"

    print(f"  User 1 Email: {user1_email}")
    print(f"  User 1 Password: {'*' * len(user1_password)} (length: {len(user1_password)})")
    print(f"  User 2 Email: {user2_email}")
    print(f"  User 2 Password: {'*' * len(user2_password)} (length: {len(user2_password)})")
    print("\n[PASS] Environment variables loaded correctly")


def test_users_dictionary():
    """Test that users are stored with lowercased emails."""
    print("\n" + "="*70)
    print("TEST 2: Users Dictionary Structure")
    print("="*70)

    assert len(AUTHORIZED_USERS) == 2, f"Expected 2 users, found {len(AUTHORIZED_USERS)}"

    print(f"  Total users loaded: {len(AUTHORIZED_USERS)}")
    print(f"  Dictionary keys (lowercased emails):")
    for email in AUTHORIZED_USERS.keys():
        print(f"    - {email}")

    # Verify emails are lowercased
    for email in AUTHORIZED_USERS.keys():
        assert email == email.lower(), f"Email not lowercased: {email}"

    print("\n[PASS] All emails properly lowercased in dictionary")


def test_authentication_case_insensitive():
    """Test that authentication works regardless of email case."""
    print("\n" + "="*70)
    print("TEST 3: Case-Insensitive Authentication")
    print("="*70)

    # Test data (user enters email in various cases)
    test_cases = [
        ("stephenb@munipipe.com", "babyWren_0!!", True, "lowercase email"),
        ("StephenB@MuniPipe.com", "babyWren_0!!", True, "mixed case email"),
        ("STEPHENB@MUNIPIPE.COM", "babyWren_0!!", True, "uppercase email"),
        ("stephenb@munipipe.com", "wrong-password", False, "correct email, wrong password"),
        ("sharonm@munipipe.com", "RegalTrue1!", True, "user 2 lowercase"),
        ("SharonM@MuniPipe.com", "RegalTrue1!", True, "user 2 mixed case"),
    ]

    passed = 0
    failed = 0

    for submitted_email, submitted_password, should_pass, description in test_cases:
        # Simulate backend authentication logic
        username_lower = submitted_email.strip().lower()
        password_hash = hashlib.sha256(submitted_password.encode()).hexdigest()

        # Check if user exists
        user_exists = username_lower in AUTHORIZED_USERS

        # Check if password matches
        password_matches = False
        if user_exists:
            password_matches = password_hash == AUTHORIZED_USERS[username_lower]['password_hash']

        auth_successful = user_exists and password_matches

        # Verify result matches expectation
        if auth_successful == should_pass:
            status = "[PASS]"
            passed += 1
        else:
            status = "[FAIL]"
            failed += 1

        expected = "should pass" if should_pass else "should fail"
        actual = "passed" if auth_successful else "failed"

        print(f"  {status} {description}: {submitted_email} -> {actual} ({expected})")

    print(f"\n  Results: {passed} passed, {failed} failed")

    assert failed == 0, f"{failed} test case(s) failed"
    print("\n[PASS] All authentication scenarios work correctly")


def test_password_hashing():
    """Test that password hashing works correctly."""
    print("\n" + "="*70)
    print("TEST 4: Password Hashing")
    print("="*70)

    user1_password = os.getenv('AUTH_USER1_PASSWORD')
    expected_hash = hashlib.sha256(user1_password.encode()).hexdigest()
    stored_hash = AUTHORIZED_USERS['stephenb@munipipe.com']['password_hash']

    print(f"  Expected hash: {expected_hash[:40]}...")
    print(f"  Stored hash:   {stored_hash[:40]}...")

    assert expected_hash == stored_hash, "Password hash mismatch"

    print("\n[PASS] Password hashing works correctly")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("AUTHENTICATION SYSTEM TESTS")
    print("="*70)

    try:
        test_env_loaded()
        test_users_dictionary()
        test_authentication_case_insensitive()
        test_password_hashing()

        print("\n" + "="*70)
        print("[PASS] ALL TESTS PASSED - Authentication system working correctly")
        print("="*70)
        print("\nYou can now log in with:")
        print("  - stephenb@munipipe.com (any case variation)")
        print("  - sharonm@munipipe.com (any case variation)")
        print("\n")

    except AssertionError as e:
        print("\n" + "="*70)
        print(f"[FAIL] TEST FAILED: {e}")
        print("="*70 + "\n")
        sys.exit(1)
    except Exception as e:
        print("\n" + "="*70)
        print(f"[FAIL] UNEXPECTED ERROR: {e}")
        print("="*70 + "\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
