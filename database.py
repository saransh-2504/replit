import sqlite3
from typing import Optional, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_NAME = 'vaani.db'

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS websites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            shop_name TEXT,
            description TEXT,
            announcement TEXT,
            image_url TEXT,
            views INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_user(username: str, password: str) -> Optional[int]:
    """
    Create a new user with hashed password.
    Returns the user ID if successful, None if username already exists.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        hashed_password = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, hashed_password)
        )
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return user_id
    except sqlite3.IntegrityError:
        return None

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user by username.
    Returns a dictionary with user data or None if not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return dict(user)
    return None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user by ID.
    Returns a dictionary with user data or None if not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return dict(user)
    return None

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a password against its hash."""
    return check_password_hash(stored_password, provided_password)

def get_website_content(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve website content for a user.
    Returns a dictionary with website data or None if not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM websites WHERE user_id = ?', (user_id,))
    website = cursor.fetchone()
    
    conn.close()
    
    if website:
        return dict(website)
    return None

def create_website_entry(user_id: int) -> int:
    """
    Create a new website entry for a user.
    Returns the website ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO websites (user_id) VALUES (?)',
        (user_id,)
    )
    
    website_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return website_id

def save_website_content(user_id: int, shop_name: str = None, 
                        description: str = None, announcement: str = None, 
                        image_url: str = None) -> bool:
    """
    Save or update website content for a user.
    Creates a new entry if none exists.
    Returns True if successful, False otherwise.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM websites WHERE user_id = ?', (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            update_fields = []
            params = []
            
            if shop_name is not None:
                update_fields.append('shop_name = ?')
                params.append(shop_name)
            if description is not None:
                update_fields.append('description = ?')
                params.append(description)
            if announcement is not None:
                update_fields.append('announcement = ?')
                params.append(announcement)
            if image_url is not None:
                update_fields.append('image_url = ?')
                params.append(image_url)
            
            if update_fields:
                params.append(user_id)
                cursor.execute(
                    f'UPDATE websites SET {", ".join(update_fields)} WHERE user_id = ?',
                    params
                )
        else:
            cursor.execute(
                '''INSERT INTO websites (user_id, shop_name, description, announcement, image_url)
                   VALUES (?, ?, ?, ?, ?)''',
                (user_id, shop_name, description, announcement, image_url)
            )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving website content: {e}")
        return False

def increment_website_view(user_id: int) -> bool:
    """
    Increment the view count for a user's website.
    Returns True if successful, False otherwise.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE websites SET views = views + 1 WHERE user_id = ?',
            (user_id,)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error incrementing view count: {e}")
        return False

def update_user_password(user_id: int, new_password: str) -> bool:
    """
    Update a user's password.
    Returns True if successful, False otherwise.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        hashed_password = generate_password_hash(new_password)
        cursor.execute(
            'UPDATE users SET password = ? WHERE id = ?',
            (hashed_password, user_id)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating user password: {e}")
        return False

def delete_user(user_id: int) -> bool:
    """
    Delete a user and their associated website.
    Returns True if successful, False otherwise.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM websites WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False

def delete_website(user_id: int) -> bool:
    """
    Delete a user's website content.
    Returns True if successful, False otherwise.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM websites WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting website: {e}")
        return False
