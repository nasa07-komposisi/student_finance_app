import sqlite3

DB_NAME = 'student_finance.db'

def migrate_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        print("Starting migration...")
        
        # 1. Rename existing table
        c.execute("ALTER TABLE transactions RENAME TO transactions_old")
        
        # 2. Create new table
        c.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                recipient TEXT,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_month TEXT,
                payment_year INTEGER,
                description TEXT,
                FOREIGN KEY (student_id) REFERENCES students (id)
            );
        """)
        
        # 3. Copy data
        # student_id is preserved. recipient is NULL for existing data.
        c.execute("""
            INSERT INTO transactions (id, student_id, date, type, amount, payment_month, payment_year, description)
            SELECT id, student_id, date, type, amount, payment_month, payment_year, description
            FROM transactions_old
        """)
        
        # 4. Verify count
        c.execute("SELECT COUNT(*) FROM transactions")
        new_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM transactions_old")
        old_count = c.fetchone()[0]
        
        if new_count == old_count:
            print(f"Migration successful. Row count matches: {new_count}")
            # 5. Drop old table
            c.execute("DROP TABLE transactions_old")
            conn.commit()
            print("Old table dropped. Migration complete.")
        else:
            print(f"Migration FAILED. Row count mismatch: Old={old_count}, New={new_count}")
            conn.rollback()
            
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
