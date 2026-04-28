import bcrypt

password = "admin123"
hashed = "$2b$12$Rou5kQxsj/ia/Yllp5OhD.nRyb4fH/6/FS5WzSh5/EG576wfOfhqW"

try:
    result = bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    print(f"Password match: {result}")
except Exception as e:
    print(f"Error: {e}")

# Try another test
hashed2 = "$2b$12$kdNxUYSx/J8KCvfKGJgTW.14pAfmQoErD2n0CEn9Jb8YmKD18Gghi"
result2 = bcrypt.checkpw("test123".encode("utf-8"), hashed2.encode("utf-8"))
print(f"test@akademus.com with test123: {result2}")