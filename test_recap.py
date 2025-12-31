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
        {"No Absen": "10", "Nama Siswa": "Zara", "Jumlah": 1, "Rupiah": 66000, "January": "Sudah Bayar"},
        {"No Absen": "1", "Nama Siswa": "Adam", "Jumlah": 2, "Rupiah": 132000, "January": "Sudah Bayar", "February": "Sudah Bayar"},
        {"No Absen": "2", "Nama Siswa": "Budi", "Jumlah": 3, "Rupiah": 198000, "January": "Sudah Bayar", "February": "Sudah Bayar", "March": "Sudah Bayar"}
    ]
    recap_df = pd.DataFrame(recap_data)
    
    # Fill missing months with "-"
    months = ["January", "February", "March"]
    for m in months:
        if m not in recap_df.columns:
            recap_df[m] = "-"
        recap_df[m] = recap_df[m].fillna("-")

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
        print("FAILURE: Numeric sorting failed.")
        
    # --- Test Total & Rupiah Logic ---
    print("\n--- Testing Total & Rupiah Rows ---")
    
    if not recap_df.empty:
        # 1. TOTAL Row
        total_row = {col: None for col in recap_df.columns}
        total_row["Nama Siswa"] = "TOTAL"
        
        total_jumlah = recap_df['Jumlah'].sum()
        total_rupiah_col = recap_df['Rupiah'].sum()
        
        total_row["Jumlah"] = total_jumlah
        total_row["Rupiah"] = total_rupiah_col
        
        month_counts = {}
        for month in months:
            count = recap_df[month].apply(lambda x: 1 if x == "Sudah Bayar" else 0).sum()
            total_row[month] = count
            month_counts[month] = count
            
        recap_df = pd.concat([recap_df, pd.DataFrame([total_row])], ignore_index=True)
        
        # 2. RUPIAH Row
        rupiah_row = {col: None for col in recap_df.columns}
        rupiah_row["Nama Siswa"] = "RUPIAH"
        
        def format_currency(x): return f"Rp {x:,.0f}"
        
        for month in months:
            rupiah_row[month] = format_currency(month_counts[month] * 66000)
        
        rupiah_row["Jumlah"] = format_currency(total_jumlah * 66000)
        rupiah_row["Rupiah"] = format_currency(total_rupiah_col)
        
        recap_df = pd.concat([recap_df, pd.DataFrame([rupiah_row])], ignore_index=True)

    print("\nResult Dataframe Tail (Last 3 rows):")
    print(recap_df.tail(3))
    
    # Check TOTAL row
    total_row = recap_df[recap_df['Nama Siswa'] == 'TOTAL'].iloc[0]
    if total_row['Jumlah'] == 6 and total_row['January'] == 3: # 1+2+3 = 6; All 3 paid Jan
        print("SUCCESS: TOTAL row calculation (Jumlah & Months) correct.")
    else:
        print(f"FAILURE: TOTAL row incorrect. Jumlah: {total_row['Jumlah']}, Jan: {total_row['January']}")

    # Check RUPIAH row
    rupiah_row = recap_df[recap_df['Nama Siswa'] == 'RUPIAH'].iloc[0]
    # Jan Count 3 * 66000 = 198,000
    expected_jan = "Rp 198,000"
    if rupiah_row['January'] == expected_jan:
        print(f"SUCCESS: RUPIAH row calculation correct. Jan: {rupiah_row['January']}")
    else:
        print(f"FAILURE: RUPIAH row incorrect. Expected {expected_jan}, Got {rupiah_row['January']}")

if __name__ == "__main__":
    test_recap()
