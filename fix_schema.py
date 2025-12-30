import sqlite3
import pandas as pd

DB_NAME = 'student_finance.db'

def fix_schema():
    print(f"Connecting to {DB_NAME}...")
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Check students table info
        print("Checking 'students' table schema...")
        c.execute("PRAGMA table_info(students)")
        columns_info = c.fetchall()
        
        print("Current columns:")
        column_names = []
        for col in columns_info:
            print(col)
            column_names.append(col[1])
            
        if 'attendance_number' not in column_names:
            print("Column 'attendance_number' missing. Attempting to add...")
            try:
                c.execute("ALTER TABLE students ADD COLUMN attendance_number TEXT")
                conn.commit()
                print("SUCCESS: Added 'attendance_number' column.")
            except Exception as e:
                print(f"FAILED to add column: {e}")
        else:
            print("Column 'attendance_number' already exists.")
            
        conn.close()
        
        # Verify with pandas
        print("\nVerifying with pandas...")
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM students", conn)
        print("DataFrame columns:", df.columns.tolist())
        conn.close()
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fix_schema()
