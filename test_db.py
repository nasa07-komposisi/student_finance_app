import database
import os

def test_database():
    print("Testing Student Financial Database...")
    
    # Ensure fresh start
    if os.path.exists(database.DB_NAME):
        os.remove(database.DB_NAME)
        print("Removed existing database.")
        
    # 1. Create Tables
    database.create_tables()
    assert os.path.exists(database.DB_NAME), "Database file not created"
    
    # 2. Add Student
    student_id = database.add_student("John Doe", "10A", "08123456789")
    print(f"Added Student ID: {student_id}")
    assert student_id is not None, "Failed to add student"
    
    students = database.get_all_students()
    print("Students in DB:")
    print(students)
    assert len(students) == 1, "Student count mismatch"
    assert students.iloc[0]['name'] == "John Doe", "Student name mismatch"
    
    # 3. Add Transaction
    trans_id = database.add_transaction(
        student_id=student_id,
        date="2024-01-15",
        type_="Tuition",
        amount=500000,
        payment_month="January",
        payment_year=2024,
        description="Monthly Tuition"
    )
    print(f"Added Transaction ID: {trans_id}")
    assert trans_id is not None, "Failed to add transaction"
    
    transactions = database.get_transactions()
    print("Transactions in DB:")
    print(transactions)
    assert len(transactions) == 1, "Transaction count mismatch"
    assert transactions.iloc[0]['amount'] == 500000, "Transaction amount mismatch"
    assert transactions.iloc[0]['payment_month'] == "January", "Payment month mismatch"
    
    print("\nALL TEST PASSED SUCCESSFULLLY!")

if __name__ == "__main__":
    test_database()
