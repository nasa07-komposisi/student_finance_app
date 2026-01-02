import pandas as pd
from datetime import datetime
import streamlit as st
from supabase import create_client, Client

# Initialize Supabase client
# These should be set in Streamlit Secrets or .streamlit/secrets.toml
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Supabase Configuration Error: {e}")
    st.info("Pastikan SUPABASE_URL dan SUPABASE_KEY sudah diatur di Streamlit Secrets.")

def create_tables():
    """
    Note: In Supabase, tables are best created via the SQL Editor in the dashboard.
    This function is kept for compatibility but doesn't do anything.
    """
    pass

def add_student(name, attendance_number, class_name, parent_contact, status='Active'):
    """Add a new student to Supabase."""
    try:
        data = {
            "name": name,
            "attendance_number": attendance_number,
            "class_name": class_name,
            "parent_contact": parent_contact,
            "status": status
        }
        response = supabase.table("students").insert(data).execute()
        if response.data:
            return response.data[0]['id']
    except Exception as e:
        st.error(f"Error adding student: {e}")
    return None

def update_student(student_id, name, attendance_number, class_name, parent_contact, status):
    """Update existing student details in Supabase."""
    try:
        data = {
            "name": name,
            "attendance_number": attendance_number,
            "class_name": class_name,
            "parent_contact": parent_contact,
            "status": status
        }
        response = supabase.table("students").update(data).eq("id", student_id).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Error updating student: {e}")
    return False

def delete_student(student_id):
    """Delete a student from Supabase."""
    try:
        response = supabase.table("students").delete().eq("id", student_id).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Error deleting student: {e}")
    return False

def get_all_students():
    """Retrieve all students from Supabase."""
    try:
        response = supabase.table("students").select("*").order("name").execute()
        if response.data:
            return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error fetching students: {e}")
    return pd.DataFrame()

def add_transaction(student_id, date, type_, amount, payment_month, payment_year, description, recipient=None):
    """Add a new transaction to Supabase."""
    try:
        data = {
            "student_id": student_id,
            "recipient": recipient,
            "date": date,
            "type": type_,
            "amount": float(amount),
            "payment_month": payment_month,
            "payment_year": int(payment_year) if payment_year else None,
            "description": description
        }
        # Postgres expects student_id as BIGINT, but can be NULL
        if student_id is None:
            del data['student_id'] # or set to None explicitly
        
        response = supabase.table("transactions").insert(data).execute()
        if response.data:
            return response.data[0]['id']
    except Exception as e:
        st.error(f"Error adding transaction: {e}")
    return None

def update_transaction(transaction_id, date, type_, amount, payment_month, payment_year, description):
    """Update an existing transaction in Supabase."""
    try:
        data = {
            "date": date,
            "type": type_,
            "amount": float(amount),
            "payment_month": payment_month,
            "payment_year": int(payment_year) if payment_year else None,
            "description": description
        }
        response = supabase.table("transactions").update(data).eq("id", transaction_id).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Error updating transaction: {e}")
    return False

def delete_transaction(transaction_id):
    """Delete a transaction from Supabase."""
    try:
        response = supabase.table("transactions").delete().eq("id", transaction_id).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Error deleting transaction: {e}")
    return False

def get_transactions():
    """Retrieve all transactions with student names or recipient from Supabase."""
    try:
        # Supabase doesn't do complex joins easily in one line without stored procedures 
        # but we can select columns from related tables if foreign keys are set.
        # Syntax: select("*, students(name, attendance_number)")
        query = "*, students(name, attendance_number)"
        response = supabase.table("transactions").select(query).order("date", desc=True).execute()
        
        if response.data:
            data = []
            for item in response.data:
                row = {
                    "id": item["id"],
                    "student_id": item["student_id"],
                    "recipient": item["recipient"],
                    "date": item["date"],
                    "type": item["type"],
                    "amount": item["amount"],
                    "payment_month": item["payment_month"],
                    "payment_year": item["payment_year"],
                    "description": item["description"]
                }
                
                # Handle Joined Student Data
                if item.get("students"):
                    row["student_name"] = item["students"]["name"]
                    row["attendance_number"] = item["students"]["attendance_number"]
                else:
                    # If student is null, it's an expense with a recipient
                    row["student_name"] = item["recipient"] if item["recipient"] else "-"
                    row["attendance_number"] = "-"
                
                data.append(row)
            
            return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching transactions: {e}")
    return pd.DataFrame()

if __name__ == '__main__':
    # For testing connectivity locally if env vars are set
    pass