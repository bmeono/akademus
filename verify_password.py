import psycopg2
import bcrypt

password = '2026$$Bri@n'
stored_hash = '$2b$12$qGKpcpmwWBxecXPR6t/pT.dt2Cz6d1RrdFVbwZfc4vG8cF7ezKj1.'

try:
    result = bcrypt.checkpw(password.encode(), stored_hash.encode())
    print(f"Password válido: {result}")
except Exception as e:
    print(f"Error: {e}")