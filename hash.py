from werkzeug.security import generate_password_hash, check_password_hash

def create_hashed_password(password: str) -> str:
    """Generate a hashed password using scrypt method."""
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(stored_hash: str, input_password: str) -> bool:
    """Verify a password against its hash."""
    return check_password_hash(stored_hash, input_password)

# Example usage
hashed_password = create_hashed_password("123456789")
print(hashed_password)  # prints the hashed password

is_password_correct = verify_password(hashed_password, "123456789")
print(is_password_correct)  # Should print True if the password is correct
