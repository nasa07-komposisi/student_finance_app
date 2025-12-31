import streamlit as st
import pandas as pd
import database
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import base64

# Page Configuration
st.set_page_config(
    page_title="Sistem Keuangan Siswa",
    page_icon="💰",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .st-emotion-cache-16idsys p {
        font-size: 1.2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Helper Functions
def format_currency(amount):
    return f"Rp {amount:,.0f}"

def export_to_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Laporan Keuangan", ln=1, align='C')
    
    # Simple table dump (improvement: make it a real table)
    for i, row in dataframe.iterrows():
        line = f"{row['date']} | {row['student_name']} | {row['type']} | {row['amount']}"
        pdf.cell(200, 10, txt=line, ln=1)
        
    return pdf.output(dest='S').encode('latin-1')

# Main Application
def main():
    st.title("💰 Sistem Pencatatan Keuangan Siswa")

    # Sidebar Navigation
    menu = ["Dashboard", "Siswa", "Transaksi", "Laporan", "Rekap"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Dashboard":
        with st.container():
            st.header("Ringkasan Keuangan")
            
            # Fetch Data
            transactions = database.get_transactions()
            students = database.get_all_students()
            
            # --- SVGs (Lineart) ---
            ICON_INCOME = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>"""
            ICON_STUDENTS = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>"""
            ICON_CALENDAR = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>"""
            ICON_OUTPUT = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5z"></path><line x1="16" y1="8" x2="2" y2="22"></line><line x1="17.5" y1="15" x2="9" y2="15"></line></svg>"""

            # --- Custom CSS for Cards ---
            st.markdown("""
            <style>
            .dashboard-card {
                background-color: white;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                display: flex;
                align-items: center;
                margin-bottom: 20px;
                transition: transform 0.2s;
            }
            .dashboard-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }
            .icon-box {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 15px;
                font-size: 24px;
            }
            .card-content {
                flex-grow: 1;
            }
            .card-title {
                margin: 0;
                color: #6b7280;
                font-size: 14px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .card-value {
                margin: 5px 0 0 0;
                color: #111827;
                font-size: 24px;
                font-weight: 700;
            }
            
            /* Color Themes - background for whole card */
            .theme-green { background-color: #dcfce7; border-left: 5px solid #16a34a; }
            .theme-blue { background-color: #dbeafe; border-left: 5px solid #2563eb; }
            .theme-purple { background-color: #f3e8ff; border-left: 5px solid #9333ea; }
            .theme-red { background-color: #fee2e2; border-left: 5px solid #dc2626; }
            .theme-orange { background-color: #ffedd5; border-left: 5px solid #ea580c; }
            
            /* Monochrome Icon Box */
            .icon-box {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background-color: rgba(255, 255, 255, 0.5); /* Semi-transparent white */
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 15px;
                /* Removed fixed font size and filter for SVGs */
                color: #374151; /* Dark grey for SVG stroke via currentColor */
            }
            .dashboard-card svg {
                width: 28px;
                height: 28px;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Helper to create card
            # Helper to create card
            def card(title, value, icon="💰", color="green", help_text=None):
                help_p = f'<p style="font-size:12px;color:#888;margin-top:4px;">{help_text}</p>' if help_text else ''
                html = f"""<div class="dashboard-card theme-{color}"><div class="icon-box">{icon}</div><div class="card-content"><p class="card-title">{title}</p><p class="card-value">{value}</p>{help_p}</div></div>"""
                st.markdown(html, unsafe_allow_html=True)

            if not transactions.empty:
                # 1. Total Income (All Time)
                total_income = transactions[transactions['type'].isin(['Income', 'Tuition', 'Pemasukan'])]['amount'].sum()
                
                # 2. Income by Year
                income_df = transactions[transactions['type'].isin(['Income', 'Tuition', 'Pemasukan'])]
                income_by_year = income_df.groupby('payment_year')['amount'].sum().sort_index()
                
                # 3. Expense by Description (Grouped)
                expense_df = transactions[transactions['type'].isin(['Expense', 'Pengeluaran'])]
                # Clean description to group better? For now grouping by exact description as requested ("transaksi yang sama")
                expense_by_desc = expense_df.groupby('description')['amount'].sum().sort_values(ascending=False)

                # --- DISPLAY ---
                
                # SECTION 1: PEMASUKAN
                st.subheader("PEMASUKAN")
                
                # Row 1: Total Overview
                c1, c2, c3 = st.columns(3)
                with c1:
                    card("TOTAL UANG MASUK", format_currency(total_income), icon=ICON_INCOME, color="green")
                with c2:
                    card("Total Siswa Aktif", f"{len(students[students['status'] == 'Active'])}", icon=ICON_STUDENTS, color="blue")
                    
                st.markdown("### Uang Masuk per Tahun")
                if not income_by_year.empty:
                    # Dynamic grid for years
                    cols = st.columns(4) # Max 4 per row
                    for i, (year, amount) in enumerate(income_by_year.items()):
                        with cols[i % 4]:
                           card(f"Tahun {year}", format_currency(amount), icon=ICON_CALENDAR, color="purple")
                else:
                    st.info("Belum ada data pemasukan.")
                
                st.divider()

                # SECTION 2: PENGELUARAN
                st.subheader("PENGELUARAN")
                
                if not expense_by_desc.empty:
                    # Total Expense Card
                    total_expense = expense_df['amount'].sum()
                    cols_total = st.columns(3)
                    with cols_total[0]:
                        card("TOTAL PENGELUARAN", format_currency(total_expense), icon=ICON_OUTPUT, color="red")
                    
                    st.markdown("#### Rincian per Transaksi")
                    
                    # Convert series to dataframe for list view
                    expense_list_df = expense_by_desc.reset_index()
                    expense_list_df.columns = ['Keterangan', 'Jumlah']
                    
                    # Format amount for display if desired, or simpler just use the df
                    # Let's create a display copy
                    display_exp_df = expense_list_df.copy()
                    display_exp_df['Jumlah'] = display_exp_df['Jumlah'].apply(format_currency)
                    
                    st.dataframe(
                        display_exp_df, 
                        use_container_width=True,
                        column_config={
                            "Keterangan": st.column_config.TextColumn("Keterangan"),
                            "Jumlah": st.column_config.TextColumn("Total Pengeluaran")
                        },
                        hide_index=True
                    )
                else:
                    st.info("Belum ada data pengeluaran.")

            else:
                st.info("Belum ada data transaksi.")

    elif choice == "Siswa":
        st.header("Manajemen Data Siswa")
        
        # Add Student Section
        with st.expander("Tambah Siswa Baru"):
            with st.form("add_student_form", clear_on_submit=True):
                name = st.text_input("Nama Siswa")
                attendance_number = st.text_input("Nomor Absen")
                class_name = st.text_input("Kelas")
                contact = st.text_input("Kontak Orang Tua")
                submit = st.form_submit_button("Simpan")
                
                if submit:
                    if name and class_name:
                        database.add_student(name, attendance_number, class_name, contact)
                        st.success(f"Siswa {name} berhasil ditambahkan!")
                        st.rerun()
                    else:
                        st.error("Nama dan Kelas wajib diisi.")
        
        # Display Students
        st.subheader("Daftar Siswa")
        students = database.get_all_students()
        
        if not students.empty:
            # Table Header
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 2, 1, 2, 2, 2, 2])
            with c1: st.write("**ID**")
            with c2: st.write("**Nama**")
            with c3: st.write("**Absen**")
            with c4: st.write("**Kelas**")
            with c5: st.write("**Kontak**")
            with c6: st.write("**Status**")
            with c7: st.write("**Aksi**")
            
            st.divider()
            
            # Iterate Rows
            for index, row in students.iterrows():
                c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 2, 1, 2, 2, 2, 2])
                with c1: st.write(str(row['id']))
                with c2: st.write(row['name'])
                with c3: st.write(str(row['attendance_number']) if pd.notna(row['attendance_number']) else "-")
                with c4: st.write(row['class_name'])
                with c5: st.write(row['parent_contact'] if pd.notna(row['parent_contact']) else "-")
                with c6: 
                    status_color = "green" if row['status'] == "Active" else "red"
                    st.markdown(f":{status_color}[{row['status']}]")
                
                with c7:
                    col_edit, col_del = st.columns(2)
                    if col_edit.button("✏️", key=f"edit_btn_{row['id']}", help="Edit Siswa"):
                        st.session_state[f'edit_mode_{row["id"]}'] = not st.session_state.get(f'edit_mode_{row["id"]}', False)
                    
                    if col_del.button("🗑️", key=f"del_btn_{row['id']}", help="Hapus Siswa"):
                         # Direct delete or confirm? Streamlit reruns. 
                         # Ideally use a confirmation, but for simplicity/speed requested:
                         st.session_state[f'confirm_del_{row["id"]}'] = True

                # Edit Form (conditionally displayed below the row)
                if st.session_state.get(f'edit_mode_{row["id"]}', False):
                    with st.expander(f"Edit Data: {row['name']}", expanded=True):
                        with st.form(key=f"edit_form_{row['id']}"):
                            ed_name = st.text_input("Nama", value=row['name'])
                            ed_absen = st.text_input("Absen", value=row['attendance_number'] if pd.notna(row['attendance_number']) else "")
                            ed_class = st.text_input("Kelas", value=row['class_name'])
                            ed_contact = st.text_input("Kontak", value=row['parent_contact'] if pd.notna(row['parent_contact']) else "")
                            ed_status = st.selectbox("Status", ["Active", "Inactive"], index=0 if row['status'] == "Active" else 1)
                            
                            if st.form_submit_button("Update"):
                                database.update_student(row['id'], ed_name, ed_absen, ed_class, ed_contact, ed_status)
                                st.success("Updated!")
                                st.session_state[f'edit_mode_{row["id"]}'] = False # Close after update
                                st.rerun()

                # Delete Confirmation
                if st.session_state.get(f'confirm_del_{row["id"]}', False):
                    st.warning(f"Hapus {row['name']}?")
                    col_y, col_n = st.columns(2)
                    if col_y.button("Ya", key=f"yes_del_{row['id']}"):
                        database.delete_student(row['id'])
                        st.success("Deleted")
                        del st.session_state[f'confirm_del_{row["id"]}']
                        st.rerun()
                    if col_n.button("Batal", key=f"no_del_{row['id']}"):
                        del st.session_state[f'confirm_del_{row["id"]}']
                        st.rerun()
                    st.divider()

        else:
            st.info("Belum ada data siswa.")

    elif choice == "Transaksi":
        st.header("Pencatatan Transaksi")
        
        students = database.get_all_students()
        
        # Prepare dictionaries
        student_dict = {}     # "ID - Name" -> ID
        student_details = {}  # ID -> Row Data
        
        if not students.empty:
            for i, row in students.iterrows():
                label = f"{row['id']} - {row['name']}"
                student_dict[label] = row['id']
                student_details[row['id']] = row
        
        # Collapsible Add Transaction Form
        with st.expander("Tambah Transaksi Baru"):
            with st.form("add_transaction_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    student_option = st.selectbox("Pilih Siswa", options=list(student_dict.keys())) if student_dict else st.selectbox("Pilih Siswa", ["Data Kosong"])
                    
                    # Auto-fill Attendance Number
                    current_absen = ""
                    if student_dict and student_option:
                        s_id = student_dict[student_option]
                        s_row = student_details.get(s_id)
                        if s_row is not None and pd.notna(s_row['attendance_number']):
                            current_absen = s_row['attendance_number']
                    
                    st.text_input("Nomor Absen", value=current_absen, disabled=True)
                    
                    trans_type = st.selectbox("Jenis Transaksi", ["Pemasukan", "Pengeluaran"])
                    amount = st.number_input("Jumlah (Rp)", min_value=0, step=1000)
                
                with col2:
                    payment_month = st.selectbox("Bulan Pembayaran", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
                    payment_year = st.number_input("Tahun Pembayaran", min_value=2020, max_value=2030, value=datetime.now().year)
                    date = st.date_input("Tanggal Transaksi", datetime.now())
                    
                desc = st.text_area("Keterangan")
                submit = st.form_submit_button("Simpan Transaksi")
                
                if submit:
                    if student_dict:
                        student_id = student_dict[student_option]
                        database.add_transaction(student_id, str(date), trans_type, amount, payment_month, payment_year, desc)
                        st.success("Transaksi berhasil disimpan!")
                        st.rerun()
                    else:
                        st.error("Tambahkan data siswa terlebih dahulu.")
        
        # History
        st.subheader("Riwayat Transaksi")
        transactions = database.get_transactions()
        
        if not transactions.empty:
            # Header
            cols = st.columns([1, 2, 1, 2, 2, 2, 2, 2])
            headers = ["Tgl", "Siswa", "Absen", "Jenis", "Nominal", "Bulan", "Ket", "Aksi"]
            for col, h in zip(cols, headers):
                col.write(f"**{h}**")
            st.divider()
            
            # Rows
            for idx, row in transactions.iterrows():
                cols = st.columns([1, 2, 1, 2, 2, 2, 2, 2])
                cols[0].write(row['date'])
                cols[1].write(row['student_name'])
                cols[2].write(row['attendance_number'] if pd.notna(row['attendance_number']) else "-")
                
                type_color = "green" if row['type'] in ["Income", "Tuition", "Pemasukan"] else "red"
                cols[3].markdown(f":{type_color}[{row['type']}]")
                
                cols[4].write(format_currency(row['amount']))
                cols[5].write(f"{row['payment_month']} {row['payment_year']}")
                cols[6].write(row['description'])
                
                # Actions
                with cols[7]:
                    c_edit, c_del = st.columns(2)
                    if c_edit.button("✏️", key=f"edit_trans_{row['id']}"):
                        st.session_state[f"edit_trans_mode_{row['id']}"] = not st.session_state.get(f"edit_trans_mode_{row['id']}", False)
                    
                    if c_del.button("🗑️", key=f"del_trans_{row['id']}"):
                        st.session_state[f"confirm_del_trans_{row['id']}"] = True
                
                # Inline Edit Form
                if st.session_state.get(f"edit_trans_mode_{row['id']}", False):
                    with st.expander(f"Edit Transaksi: {row['student_name']}", expanded=True):
                        with st.form(key=f"edit_trans_form_{row['id']}"):
                            nc1, nc2 = st.columns(2)
                            with nc1:
                                n_type = st.selectbox("Jenis", ["Pemasukan", "Pengeluaran"], index=0 if row['type'] == "Pemasukan" else 1)
                                n_amount = st.number_input("Jumlah", value=float(row['amount']))
                            with nc2:
                                n_month = st.selectbox("Bulan", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], index=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"].index(row['payment_month']) if row['payment_month'] in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"] else 0)
                                n_year = st.number_input("Tahun", value=int(row['payment_year']))
                                
                            n_date = st.date_input("Tanggal", value=pd.to_datetime(row['date']))
                            n_desc = st.text_area("Keterangan", value=row['description'])
                            
                            if st.form_submit_button("Update Transaksi"):
                                database.update_transaction(row['id'], str(n_date), n_type, n_amount, n_month, n_year, n_desc)
                                st.success("Transaksi diperbarui!")
                                st.session_state[f"edit_trans_mode_{row['id']}"] = False
                                st.rerun()

                # Delete Confirmation
                if st.session_state.get(f"confirm_del_trans_{row['id']}", False):
                    st.warning("Hapus transaksi ini?")
                    if st.button("Ya", key=f"yes_del_trans_{row['id']}"):
                        database.delete_transaction(row['id'])
                        st.success("Terhapus!")
                        del st.session_state[f"confirm_del_trans_{row['id']}"]
                        st.rerun()
                    if st.button("Batal", key=f"no_del_trans_{row['id']}"):
                        del st.session_state[f"confirm_del_trans_{row['id']}"]
                        st.rerun()
                    st.divider()

    elif choice == "Laporan":
        st.header("Laporan Keuangan")
        
        transactions = database.get_transactions()
        if not transactions.empty:
            # Prepare data for filtering
            # Extract month name from transaction date for "Bulan Transaksi"
            transactions['trans_month_name'] = pd.to_datetime(transactions['date']).dt.strftime('%B')
            
            # Filters
            # Filters
            # Filters
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            
            # Filter 1: Bulan Bayar (payment_month)
            unique_pay_months = ["Semua"] + list(transactions['payment_month'].unique())
            pay_month_filter = col_f1.selectbox("Filter Bulan Bayar", unique_pay_months)
            
            # Filter 2: Tahun Bayar (payment_year)
            unique_pay_years = ["Semua"] + sorted([int(x) for x in transactions['payment_year'].unique() if pd.notna(x)])
            pay_year_filter = col_f2.selectbox("Filter Tahun Bayar", unique_pay_years)
            
            # Filter 3: Jenis Transaksi (type)
            unique_types = ["Semua"] + list(transactions['type'].unique())
            type_filter = col_f3.selectbox("Filter Jenis", unique_types)

            # Filter 4: Tanggal Transaksi (Range)
            transactions['date'] = pd.to_datetime(transactions['date'])
            min_date = transactions['date'].min().date()
            max_date = transactions['date'].max().date()
            
            date_range = col_f4.date_input("Rentang Tanggal Input", [min_date, max_date])
            
            # Apply Filters
            filtered_df = transactions.copy()
            
            if pay_month_filter != "Semua":
                filtered_df = filtered_df[filtered_df['payment_month'] == pay_month_filter]
                
            if pay_year_filter != "Semua":
                filtered_df = filtered_df[filtered_df['payment_year'] == pay_year_filter]
                
            if type_filter != "Semua":
                filtered_df = filtered_df[filtered_df['type'] == type_filter]
            
            # Apply Date Range Filter
            if len(date_range) == 2:
                start_date, end_date = date_range
                # Ensure comparison uses datetime.date
                filtered_df = filtered_df[
                    (filtered_df['date'].dt.date >= start_date) & 
                    (filtered_df['date'].dt.date <= end_date)
                ]
            
            # Select and Rename Columns for Display (Hide IDs)
            # Available: id, student_id, student_name, attendance_number, date, type, amount, payment_month, payment_year, description
            display_columns = ['date', 'student_name', 'attendance_number', 'type', 'amount', 'payment_month', 'payment_year', 'description']
            display_df = filtered_df[display_columns].copy()
            
            display_df.columns = ["Tanggal", "Nama Siswa", "Absen", "Jenis", "Nominal", "Bulan Bayar", "Tahun Bayar", "Keterangan"]
            
            # Format Currency
            display_df['Nominal'] = display_df['Nominal'].apply(format_currency)
            
            # Format Date dd-mmm-yyyy (e.g., 20-Jan-2024)
            # Ensure it is datetime first (it should be from earlier steps, but safe to check)
            display_df['Tanggal'] = pd.to_datetime(display_df['Tanggal']).dt.strftime('%d-%b-%Y')
                
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            csv = display_df.to_csv(index=False).encode('utf-8')
            col1.download_button("Download CSV", csv, "laporan.csv", "text/csv")
            
            # PDF Export
            if st.button("Download PDF"):
                # Use filtered_df but with nice columns for PDF too? 
                # For simplicity, passing display_df which has nice headers but no IDs
                pdf_bytes = export_to_pdf(filtered_df) # export_to_pdf function might need adjustment if it relies on specific col names
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="laporan.pdf">Download PDF File</a>'
                col2.markdown(href, unsafe_allow_html=True)
        else:
            st.info("Belum ada data transaksi untuk laporan.")

    elif choice == "Rekap":
        st.header("Rekapitulasi Pembayaran")
        
        # 1. Filter Year
        current_year = datetime.now().year
        selected_year = st.number_input("Tahun", min_value=2020, max_value=2030, value=current_year)
        
        # 2. Get Data
        students = database.get_all_students()
        active_students = students[students['status'] == 'Active'] if not students.empty else pd.DataFrame()
        transactions = database.get_transactions()
        
        if active_students.empty:
            st.info("Tidak ada siswa aktif to display.")
        else:
            # 3. Process Data
            # Filter transactions for the selected year and income types
            # Note: We consider 'Pemasukan', 'Income', 'Tuition' as payments
            paid_trans = pd.DataFrame()
            if not transactions.empty:
                paid_trans = transactions[
                    (transactions['payment_year'] == selected_year) & 
                    (transactions['type'].isin(['Pemasukan', 'Income', 'Tuition']))
                ]
            
            # Create a pivot-like structure
            months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            
            recap_data = []
            
            for idx, student in active_students.iterrows():
                row_data = {
                    "No Absen": student['attendance_number'] if pd.notna(student['attendance_number']) else "",
                    "Nama Siswa": student['name']
                }
                
                # Check payment for each month
                student_payments = []
                if not paid_trans.empty:
                    student_payments = paid_trans[paid_trans['student_id'] == student['id']]['payment_month'].unique()
                
                paid_count = 0
                for month in months:
                    if month in student_payments:
                        row_data[month] = "Sudah Bayar"
                        paid_count += 1
                    else:
                        row_data[month] = "-"
                
                row_data["Jumlah"] = paid_count
                row_data["Rupiah"] = paid_count * 66000
                
                # Try to convert No Absen to numeric for better native sorting
                try:
                    row_data["No Absen"] = int(row_data["No Absen"])
                except:
                    pass
                
                recap_data.append(row_data)
                
            recap_df = pd.DataFrame(recap_data)

            # Calculate and Append Total & Rupiah Rows
            if not recap_df.empty:
                # Calculate totals BEFORE formatting
                total_jumlah = recap_df['Jumlah'].sum()
                total_rupiah_col = recap_df['Rupiah'].sum() # Sum on raw numbers
                
                # Now format the main column
                recap_df['Rupiah'] = recap_df['Rupiah'].apply(format_currency)
                
                # 1. TOTAL Row
                total_row = {col: None for col in recap_df.columns}
                total_row["Nama Siswa"] = "TOTAL"
                total_row["No Absen"] = ""
                
                total_row["Jumlah"] = total_jumlah
                total_row["Rupiah"] = format_currency(total_rupiah_col) # Match format
                
                # Count 'Sudah Bayar' for month columns
                month_counts = {}
                for month in months:
                    count = recap_df[month].apply(lambda x: 1 if x == "Sudah Bayar" else 0).sum()
                    total_row[month] = count
                    month_counts[month] = count
                    
                recap_df = pd.concat([recap_df, pd.DataFrame([total_row])], ignore_index=True)
                
                # 2. RUPIAH Row
                rupiah_row = {col: None for col in recap_df.columns}
                rupiah_row["Nama Siswa"] = "RUPIAH"
                rupiah_row["No Absen"] = ""

                
                # Calculate Rupiah for months
                for month in months:
                    rupiah_row[month] = format_currency(month_counts[month] * 66000)
                
                # For Jumlah column, maybe show the total Rupiah equivalent? 
                # User request: "buat baris rupiah yang merupakan hasil total dikali dengan 66.000 rupiah"
                rupiah_row["Jumlah"] = format_currency(total_jumlah * 66000)
                rupiah_row["Rupiah"] = format_currency(total_rupiah_col) # Already in Rupiah
                
                recap_df = pd.concat([recap_df, pd.DataFrame([rupiah_row])], ignore_index=True)

            # Format Rupiah column in main df for display?
            # It might be better to keep as numbers for sorting until the end, but the Total row mixes types (counts).
            # Streamlit dataframe handles mixed types okay. 
            # Let's format the money columns in the rows for better readability if possible, 
            # or use column_config. For now, I'll format the new row values as currency strings.
            # The 'Rupiah' column in main body is number.
            
            
            # Sort by No Absen (try to convert to int if possible for correct sorting)
            # Create a localized column mapping if desired, but user asked for standard months? 
            # User instructions: "bulan januari s.d desember" -> Let's rename columns for display
            
            indo_months = {
                "January": "Januari", "February": "Februari", "March": "Maret", "April": "April", 
                "May": "Mei", "June": "Juni", "July": "Juli", "August": "Agustus", 
                "September": "September", "October": "Oktober", "November": "November", "December": "Desember"
            }
            recap_df = recap_df.rename(columns=indo_months)
            
            # Styling function
            def color_paid(val):
                color = '#90EE90' if val == 'Sudah Bayar' else '' # Light green
                return f'background-color: {color}' if color else ''

            st.dataframe(
                recap_df.style.applymap(color_paid, subset=list(indo_months.values())),
                use_container_width=True,
                height=500,
                hide_index=True
            )

if __name__ == '__main__':
    # Initialize DB if needed
    database.create_tables()
    main()