import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = 'student_finance.db'

def create_connection():
    """Create a database connection to the SQLite database specified by DB_NAME."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn

def create_tables():
    """Create tables in the database."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            # Students table
            c.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    attendance_number TEXT,
                    class_name TEXT NOT NULL,
                    parent_contact TEXT,
                    status TEXT DEFAULT 'Active'
                );
            """)
            
            # Check if attendance_number column exists (migration for existing db)
            c.execute("PRAGMA table_info(students)")
            columns = [info[1] for info in c.fetchall()]
            if 'attendance_number' not in columns:
                c.execute("ALTER TABLE students ADD COLUMN attendance_number TEXT")
                print("Added attendance_number column to students table.")
            
            # Transactions table
            c.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    payment_month TEXT,
                    payment_year INTEGER,
                    description TEXT,
                    FOREIGN KEY (student_id) REFERENCES students (id)
                );
            """)
            conn.commit()
            print("Tables created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")

def add_student(name, attendance_number, class_name, parent_contact, status='Active'):
    """Add a new student to the database."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute("INSERT INTO students (name, attendance_number, class_name, parent_contact, status) VALUES (?, ?, ?, ?, ?)",
                      (name, attendance_number, class_name, parent_contact, status))
            conn.commit()
            return c.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding student: {e}")
        finally:
            conn.close()
    return None

def update_student(student_id, name, attendance_number, class_name, parent_contact, status):
    """Update existing student details."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute("""
                UPDATE students 
                SET name=?, attendance_number=?, class_name=?, parent_contact=?, status=?
                WHERE id=?
            """, (name, attendance_number, class_name, parent_contact, status, student_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating student: {e}")
        finally:
            conn.close()
    return False

def delete_student(student_id):
    """Delete a student (and potentially cascade/handle transactions later)."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            # Note: dependent transactions might become orphaned or you should delete them too.
            # For now, we just delete the student.
            c.execute("DELETE FROM students WHERE id=?", (student_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting student: {e}")
        finally:
            conn.close()
    return False

def get_all_students():
    """Retrieve all students."""
    conn = create_connection()
    if conn is not None:
        try:
            return pd.read_sql_query("SELECT * FROM students", conn)
        except Exception as e:
            print(f"Error fetching students: {e}")
        finally:
            conn.close()
    return pd.DataFrame()

def add_transaction(student_id, date, type_, amount, payment_month, payment_year, description, recipient=None):
    """Add a new transaction."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute("""
                INSERT INTO transactions (student_id, recipient, date, type, amount, payment_month, payment_year, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (student_id, recipient, date, type_, amount, payment_month, payment_year, description))
            conn.commit()
            return c.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding transaction: {e}")
        finally:
            conn.close()
    return None

def update_transaction(transaction_id, date, type_, amount, payment_month, payment_year, description):
    """Update an existing transaction."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute("""
                UPDATE transactions 
                SET date=?, type=?, amount=?, payment_month=?, payment_year=?, description=?
                WHERE id=?
            """, (date, type_, amount, payment_month, payment_year, description, transaction_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating transaction: {e}")
        finally:
            conn.close()
    return False

def delete_transaction(transaction_id):
    """Delete a transaction."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting transaction: {e}")
        finally:
            conn.close()
    return False

def get_transactions():
    """Retrieve all transactions with student names or recipient."""
    conn = create_connection()
    if conn is not None:
        try:
            # Query updated to handle NULL student_id and include recipient
            # Use COALESCE to prioritize student name, but we might want to distinct them?
            # User wants "Penerima Dana".
            query = """
                SELECT t.id, t.student_id, t.recipient, s.name as student_name, s.attendance_number, t.date, t.type, t.amount, t.payment_month, t.payment_year, t.description
                FROM transactions t
                LEFT JOIN students s ON t.student_id = s.id
                ORDER BY t.date DESC
            """
            df = pd.read_sql_query(query, conn)
            # Create a unified 'name' column for display logic if needed, 
            # or keep them separate. App likely expects 'student_name'.
            # Let's fill student_name with recipient if student_id is None
            if not df.empty:
                df['student_name'] = df.apply(
                    lambda row: row['student_name'] if pd.notna(row['student_id']) else (row['recipient'] if pd.notna(row['recipient']) else "-"),
                    axis=1
                )
            return df
        except Exception as e:
            print(f"Error fetching transactions: {e}")
        finally:
            conn.close()
    return pd.DataFrame()

if __name__ == '__main__':
    create_tables()