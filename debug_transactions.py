import database
import pandas as pd

def debug():
    try:
        print("Fetching transactions...")
        df = database.get_transactions()
        print("Columns found:", df.columns.tolist())
        
        if 'attendance_number' in df.columns:
            print("SUCCESS: 'attendance_number' verified in columns.")
            print("First few rows:")
            print(df[['student_name', 'attendance_number']].head())
        else:
            print("FAILURE: 'attendance_number' NOT found in columns.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug()
