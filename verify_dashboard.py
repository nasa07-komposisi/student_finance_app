import database
import pandas as pd

def verify_calculations():
    print("Verifying Dashboard Logic...")
    
    # Simulate data fetching
    transactions = database.get_transactions()
    students = database.get_all_students()
    
    # 1. Verify Student Count
    total_students = len(students[students['status'] == 'Active']) if not students.empty else 0
    print(f"Total Active Students: {total_students}")
    print(f"Raw Student Count: {len(students)}")
    
    # 2. Verify Financials
    if not transactions.empty:
        # Pemasukan
        income_df = transactions[transactions['type'].isin(['Income', 'Tuition', 'Pemasukan'])]
        total_income = income_df['amount'].sum()
        print(f"Total Income (Calculated): {total_income}")
        print("Income Transactions:")
        print(income_df[['type', 'amount']])
        
        # Pengeluaran
        expense_df = transactions[transactions['type'].isin(['Expense', 'Pengeluaran'])]
        total_expense = expense_df['amount'].sum()
        print(f"Total Expense (Calculated): {total_expense}")
        print("Expense Transactions:")
        print(expense_df[['type', 'amount']])
    else:
        print("No transactions found.")

if __name__ == "__main__":
    verify_calculations()
