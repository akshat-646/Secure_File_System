import mysql.connector
from mysql.connector import Error
import hashlib

def create_database_connection():
    """Create connection to MySQL database"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='secure_file_system',
            user='root',  # Change this to your MySQL username
            password='root'  # Change this to your MySQL password
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database_and_tables():
    """Create the database and required tables"""
    try:
        # First connect without specifying database to create it
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Change this to your MySQL username
            password='root'  # Change this to your MySQL password
        )
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS secure_file_system")
        cursor.execute("USE secure_file_system")
        
        # Create users table
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(64) NOT NULL,
            role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
            face_image_path VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL
        )
        """
        cursor.execute(create_users_table)
        
        # Create login_attempts table for additional security
        create_attempts_table = """
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50),
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN DEFAULT FALSE,
            ip_address VARCHAR(45)
        )
        """
        cursor.execute(create_attempts_table)
        
        connection.commit()
        print("✅ Database and tables created successfully!")
        
    except Error as e:
        print(f"❌ Error creating database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user_to_db(username, password, role, face_image_path):
    """Register a new user in the database"""
    connection = create_database_connection()
    if not connection:
        return False
        
    try:
        cursor = connection.cursor()
        password_hash = hash_password(password)
        
        query = """
        INSERT INTO users (username, password_hash, role, face_image_path)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (username, password_hash, role, face_image_path))
        connection.commit()
        return True
        
    except mysql.connector.IntegrityError:
        print("❌ User already exists!")
        return False
    except Error as e:
        print(f"❌ Error registering user: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def verify_user_credentials(username, password):
    """Verify user credentials against database"""
    connection = create_database_connection()
    if not connection:
        return None
        
    try:
        cursor = connection.cursor()
        password_hash = hash_password(password)
        
        query = """
        SELECT username, role, face_image_path FROM users 
        WHERE username = %s AND password_hash = %s
        """
        cursor.execute(query, (username, password_hash))
        result = cursor.fetchone()
        
        if result:
            return {
                'username': result[0],
                'role': result[1],
                'face_image_path': result[2]
            }
        return None
        
    except Error as e:
        print(f"❌ Error verifying credentials: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_last_login(username):
    """Update last login timestamp"""
    connection = create_database_connection()
    if not connection:
        return
        
    try:
        cursor = connection.cursor()
        query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = %s"
        cursor.execute(query, (username,))
        connection.commit()
        
    except Error as e:
        print(f"❌ Error updating last login: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def log_login_attempt(username, success=False, ip_address="127.0.0.1"):
    """Log login attempt for security monitoring"""
    connection = create_database_connection()
    if not connection:
        return
        
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO login_attempts (username, success, ip_address)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (username, success, ip_address))
        connection.commit()
        
    except Error as e:
        print(f"❌ Error logging attempt: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
def delete_user_from_db(username):
    """Delete user and related data from database"""
    connection = create_database_connection()
    if not connection:
        return False

    try:
        cursor = connection.cursor()
        query = "DELETE FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        connection.commit()
        print(f"✅ User '{username}' deleted from DB")
        return True
    except Error as e:
        print(f"❌ Error deleting user: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == "__main__":
    # Run this script first to set up the database
    create_database_and_tables()