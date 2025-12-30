import database
import pandas as pd
from datetime import datetime

def test_recap():
    print("Testing Recap Logic...")
    
    # 1. Setup Mock Data
    current_year = 2024 # Force 2024 for test
    selected_year = current_year
    
    students = database.get_all_students()
    print(f"Students: {len(students)}")
    
    transactions = database.get_transactions()
    print(f"Transactions: {len(transactions)}")
    
    # Filter like in app
    paid_trans = pd.DataFrame()
    if not transactions.empty:
        # Check types present in DB
        print("Transaction Types in DB:", transactions['type'].unique())
        
        paid_trans = transactions[
            (transactions['payment_year'] == selected_year) & 
            (transactions['type'].isin(['Pemasukan', 'Income', 'Tuition']))
        ]
        print(f"Paid Transactions for {selected_year}: {len(paid_trans)}")

    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    
    active_students = students[students['status'] == 'Active']
    
    recap_data = []
    
    for idx, student in active_students.iterrows():
        row_data = {
            "No Absen": student['attendance_number'] if pd.notna(student['attendance_number']) else "",
            "Nama Siswa": student['name']
        }
        
        student_payments = []
        if not paid_trans.empty:
            student_payments = paid_trans[paid_trans['student_id'] == student['id']]['payment_month'].unique()
        
        for month in months:
            if month in student_payments:
                row_data[month] = "Sudah Bayar"
            else:
                row_data[month] = "-"
        
        # Mock calculation for test consistency
        row_data["Jumlah"] = len([m for m in months if m in student_payments])
        
    # Mock Data for Sorting
    recap_data = [
        {"No Absen": "10", "Nama Siswa": "Zara", "Jumlah": 1},
        {"No Absen": "1", "Nama Siswa": "Adam", "Jumlah": 2},
        {"No Absen": "2", "Nama Siswa": "Budi", "Jumlah": 3}
    ]
    recap_df = pd.DataFrame(recap_data)
    
    print("\n--- Testing Sorting Logic ---")
    print("Original Order:", recap_df['No Absen'].tolist())
    
    # Test Sort Logic
    try:
        recap_df['No Absen Temp'] = pd.to_numeric(recap_df['No Absen'], errors='coerce')
        recap_df = recap_df.sort_values('No Absen Temp').drop(columns=['No Absen Temp'])
    except:
        recap_df = recap_df.sort_values('No Absen')
        
    print("Sorted Order:", recap_df['No Absen'].tolist())
    
    if recap_df['No Absen'].tolist() == ["1", "2", "10"]:
        print("SUCCESS: Numeric sorting works correctly.")
    else:
        print("FAILURE: Numeric sorting failed (likely lexicographical: 1, 10, 2).")

    # Mock Total Row Logic
    if not recap_df.empty:
        total_paid = recap_df['Jumlah'].sum()
        total_row = {col: "" for col in recap_df.columns}
        total_row["Nama Siswa"] = "TOTAL"
        total_row["Jumlah"] = total_paid
        recap_df = pd.concat([recap_df, pd.DataFrame([total_row])], ignore_index=True)

    print("\nResult Dataframe Head & Tail:")
    print(recap_df.head())
    print(recap_df.tail(1))
    
    if recap_df.iloc[-1]['Nama Siswa'] == "TOTAL":
         print(f"\nSUCCESS: 'TOTAL' row found. Total Amount: {recap_df.iloc[-1]['Jumlah']}")
    else:
         print("\nFAILURE: 'TOTAL' row NOT found.")
    
    # Check if we have any 'Sudah Bayar'
    paid_count = (recap_df == "Sudah Bayar").sum().sum()
    print(f"\nTotal 'Sudah Bayar' cells: {paid_count}")

if __name__ == "__main__":
    test_recap()
