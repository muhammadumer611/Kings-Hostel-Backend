from app.utils.password_handler import hash_password

password = "admin123"

hashed = hash_password(password)

print("\nHashed Password:\n")
print(hashed)