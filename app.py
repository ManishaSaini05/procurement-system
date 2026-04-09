#import streamlit as st
#import pandas as pd
#from pathlib import Path
#from services.db import get_connection
#from services.email_service import send_rfq_email

#st.set_page_config(page_title="Procurement System", layout="wide")

# =========================
# SESSION INIT
# =========================
#if "logged_in" not in st.session_state:
#    st.session_state.logged_in = False

#if "active_project_id" not in st.session_state:
#    st.session_state.active_project_id = None

#if "active_project_code" not in st.session_state:
#    st.session_state.active_project_code = None


# =========================
# LOGIN PAGE
# =========================
#def login_page():
#    st.title("🔐 Procurement Login")

#    username = st.text_input("Username")
#    password = st.text_input("Password", type="password")

#    if st.button("Login"):
#        conn = get_connection()
#        cursor = conn.cursor()

#        cursor.execute(
#            "SELECT * FROM users WHERE username=? AND password=?",
#            (username, password)
#        )
#        user = cursor.fetchone()
#        conn.close()

#        if user:
#            st.session_state.logged_in = True
#            st.success("Login successful")
#            st.rerun()
#        else:
#            st.error("Invalid credentials")


# =========================
# PROJECT SELECTION
# =========================
#def project_section():
#    st.subheader("📂 Select Project from Design BOQ")

#    boq_path = Path("data/Design_boq.xlsx")

#    if not boq_path.exists():
#        st.error("BOQ file not found in data folder.")
#        st.stop()

#    boq_df = pd.read_excel(boq_path)

#    required_cols = [
#        "Project_ID",
#        "Project_Name",
#        "Material_Name",
#        "Specification",
#        "BOQ_Quantity"
#    ]

#    for col in required_cols:
#        if col not in boq_df.columns:
#            st.error(f"Missing column in BOQ: {col}")
#            st.stop()

#    unique_projects = boq_df["Project_ID"].dropna().unique()

#    selected_project_code = st.selectbox(
#        "Select Project ID",
#        unique_projects
#    )

#    if selected_project_code:

#        conn = get_connection()
#        cursor = conn.cursor()

#        # Check if project exists
#        cursor.execute(
#            "SELECT * FROM projects WHERE project_code=?",
#            (selected_project_code,)
#        )
#        existing = cursor.fetchone()

#        if not existing:
#            cursor.execute(
#                """INSERT INTO projects 
#                (project_code, project_name, client, location)
#                VALUES (?, ?, ?, ?)""",
#                (selected_project_code, selected_project_code, "", "")
#            )
#            conn.commit()

#        # Fetch ID
#        cursor.execute(
#            "SELECT id FROM projects WHERE project_code=?",
#            (selected_project_code,)
#        )
#        project_id = cursor.fetchone()["id"]

#        conn.close()

#        st.session_state.active_project_id = project_id
#        st.session_state.active_project_code = selected_project_code

#        st.success(f"Project {selected_project_code} Ready for Procurement")


# =========================
# MATERIAL SECTION
# =========================
#def material_section():
#    if not st.session_state.active_project_id:
#        st.warning("Please select project first.")
#        return

#    st.subheader("📐 Materials From BOQ")

#    boq_path = Path("data/Design_boq.xlsx")
#    boq_df = pd.read_excel(boq_path)

#    project_materials = boq_df[
#        boq_df["Project_ID"] == st.session_state.active_project_code
#    ]

#    if project_materials.empty:
#        st.info("No materials found for this project.")
#        return

#    material_names = project_materials["Material_Name"].unique()

#    selected_material = st.selectbox(
#        "Select Material",
#        material_names
#    )

#    if selected_material:

#        material_row = project_materials[
#            project_materials["Material_Name"] == selected_material
#        ].iloc[0]

#        st.markdown("### 📊 Past Vendor History")

#        vendor_path = Path("data/past_vendor_data.xlsx")

#        if not vendor_path.exists():
#            st.warning("Past vendor data file not found.")
#            return

#        vendor_df = pd.read_excel(vendor_path)
#        vendor_df.columns = vendor_df.columns.str.strip()

#        required_cols = [
#            "Material_Name",
#            "Vendor_Name",
#            "Project_ID",
#            "Unit_Price",
#            "Quantity",
#            "Email"
#        ]

#        for col in required_cols:
#            if col not in vendor_df.columns:
#                st.error(f"Missing column in vendor sheet: {col}")
#                return

#        # Clean matching
#        def clean_text(text):
#            return str(text).strip().lower()

#        selected_material_clean = clean_text(selected_material)
#        vendor_df["Material_Name"] = vendor_df["Material_Name"].apply(clean_text)

#        filtered_vendors = vendor_df[
#            vendor_df["Material_Name"] == selected_material_clean
#        ]

#        if filtered_vendors.empty:
#            st.warning("No past vendor history found for this material.")
#            return

#        #filtered_vendors = filtered_vendors.drop_duplicates()

#        #.success("Past vendor history found.")
#        #st.dataframe(filtered_vendors, use_container_width=True)

#        # ✅ CORRECT Vendor Selection
#        # Add selection column
#        filtered_vendors["Select"] = False

#        edited_df = st.data_editor(
#            filtered_vendors,
#            use_container_width=True,
#            num_rows="fixed"
#        )

#        if st.button("Send RFQ"):

#            # Create RFQ master entry
#            cursor.execute("""
#                INSERT INTO rfq_master (
#                    project_id,
#                    material_name,
#                    created_at,
#                    status
#                )
#               VALUES (?, ?, datetime('now'), ?)
#            """, (
#                st.session_state.active_project_id,
#                selected_material,
#                "sent"
#            ))

#            conn.commit()
#            rfq_id = cursor.lastrowid

#            selected_rows = edited_df[edited_df["Select"] == True]

#            if selected_rows.empty:
#                st.warning("Please select at least one vendor.")
#                return

#            conn = get_connection()
#            cursor = conn.cursor()

#            for _, row in selected_rows.iterrows():

#                vendor_name = row["Vendor_Name"]
#                vendor_email = row["Email"]

        # 1️⃣ Send Email
#                email_sent = send_rfq_email(
#                    vendor_email,
#                    vendor_name,
#                    st.session_state.active_project_code,
#                    selected_material,
#                    material_row["BOQ_Quantity"],
#                    rfq_id
#                )

#                if email_sent:
#                    st.success(f"RFQ sent to {vendor_name}")
#                else:
#                    st.error(f"Failed to send email to {vendor_name}")

#        # 2️⃣ Save RFQ entry in SQLite
#                cursor.execute("""
#                   INSERT INTO rfq_master (
#                        project_id,
#                        material_name,
#                        rfq_date,
#                        status
#                    )
#                    VALUES (?, ?, datetime('now'), ?)
#                """, (st.session_state.active_project_id,selected_material_clean,"sent"))
#                # Save Vendor under RFQ
#                rfq_id = cursor.lastrowid
#                cursor.execute("""
#                    INSERT INTO rfq_vendors (
#                        rfq_id,
#                        vendor_name,
#                        vendor_email,
#                        status
#                    )
#                    VALUES (?, ?, ?, ?)
#                """, (
#                    rfq_id,
#                    vendor_name,
#                    vendor_email,
#                    "RFQ Sent"
#                ))
#            conn.commit()
#            conn.close()

#            st.success("RFQ process completed.")


# =========================
# DASHBOARD
# =========================
#def dashboard():
#    st.title("📦 Procurement Dashboard")

#    menu = st.sidebar.radio(
#        "Navigation",
#        ["Projects", "Materials"]
#    )

#    if menu == "Projects":
#        project_section()

#    elif menu == "Materials":
#        material_section()


# =========================
# APP FLOW
# =========================
#if not st.session_state.logged_in:
#    login_page()
#else:
#    dashboard()

# import streamlit as st
# import pandas as pd
# from pathlib import Path
# from services.db import get_connection
# from services.email_service import send_rfq_email

# st.set_page_config(page_title="Procurement System", layout="wide")

# # =========================
# # SESSION INIT
# # =========================
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# if "active_project_id" not in st.session_state:
#     st.session_state.active_project_id = None

# if "active_project_code" not in st.session_state:
#     st.session_state.active_project_code = None


# # =========================
# # LOGIN PAGE
# # =========================
# def login_page():
#     st.title("🔐 Procurement Login")

#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")

#     if st.button("Login"):
#         conn = get_connection()
#         cursor = conn.cursor()

#         cursor.execute(
#             "SELECT * FROM users WHERE username=? AND password=?",
#             (username, password)
#         )

#         user = cursor.fetchone()
#         conn.close()

#         if user:
#             st.session_state.logged_in = True
#             st.success("Login successful")
#             st.rerun()
#         else:
#             st.error("Invalid credentials")


# # =========================
# # PROJECT SECTION
# # =========================
# def project_section():
#     st.subheader("📂 Select Project from Design BOQ")

#     boq_path = Path("data/Design_boq.xlsx")

#     if not boq_path.exists():
#         st.error("BOQ file not found in data folder.")
#         return

#     boq_df = pd.read_excel(boq_path)

#     required_cols = [
#         "Project_ID",
#         "Project_Name",
#         "Material_Name",
#         "Specification",
#         "BOQ_Quantity"
#     ]

#     for col in required_cols:
#         if col not in boq_df.columns:
#             st.error(f"Missing column in BOQ: {col}")
#             return

#     unique_projects = boq_df["Project_ID"].dropna().unique()

#     selected_project_code = st.selectbox("Select Project ID", unique_projects)

#     if selected_project_code:

#         conn = get_connection()
#         cursor = conn.cursor()

#         cursor.execute(
#             "SELECT * FROM projects WHERE project_code=?",
#             (selected_project_code,)
#         )

#         existing = cursor.fetchone()

#         if not existing:
#             cursor.execute("""
#                 INSERT INTO projects 
#                 (project_code, project_name, client, location)
#                 VALUES (?, ?, ?, ?)
#             """, (selected_project_code, selected_project_code, "", ""))
#             conn.commit()

#         cursor.execute(
#             "SELECT id FROM projects WHERE project_code=?",
#             (selected_project_code,)
#         )

#         project_id = cursor.fetchone()["id"]

#         conn.close()

#         st.session_state.active_project_id = project_id
#         st.session_state.active_project_code = selected_project_code

#         st.success(f"Project {selected_project_code} Ready for Procurement")


# # =========================
# # MATERIAL SECTION
# # =========================
# def material_section():

#     if not st.session_state.active_project_id:
#         st.warning("Please select project first.")
#         return

#     st.subheader("📐 Materials From BOQ")

#     boq_path = Path("data/Design_boq.xlsx")
#     boq_df = pd.read_excel(boq_path)

#     project_materials = boq_df[
#         boq_df["Project_ID"] == st.session_state.active_project_code
#     ]

#     if project_materials.empty:
#         st.info("No materials found for this project.")
#         return

#     material_names = project_materials["Material_Name"].unique()

#     selected_material = st.selectbox("Select Material", material_names)

#     if not selected_material:
#         return

#     material_row = project_materials[
#         project_materials["Material_Name"] == selected_material
#     ].iloc[0]

#     st.markdown("### 📊 Past Vendor History")

#     vendor_path = Path("data/past_vendor_data.xlsx")

#     if not vendor_path.exists():
#         st.warning("Past vendor data file not found.")
#         return

#     vendor_df = pd.read_excel(vendor_path)
#     vendor_df.columns = vendor_df.columns.str.strip()

#     required_cols = [
#         "Material_Name",
#         "Vendor_Name",
#         "Project_ID",
#         "Unit_Price",
#         "Quantity",
#         "Email"
#     ]

#     for col in required_cols:
#         if col not in vendor_df.columns:
#             st.error(f"Missing column in vendor sheet: {col}")
#             return

#     vendor_df["Material_Name"] = vendor_df["Material_Name"].str.strip().str.lower()
#     selected_material_clean = selected_material.strip().lower()

#     filtered_vendors = vendor_df[
#         vendor_df["Material_Name"] == selected_material_clean
#     ]

#     if filtered_vendors.empty:
#         st.warning("No past vendor history found for this material.")
#         return

#     filtered_vendors = filtered_vendors.copy()
#     filtered_vendors["Select"] = False

#     edited_df = st.data_editor(
#         filtered_vendors,
#         use_container_width=True,
#         num_rows="fixed"
#     )

#     # =========================
#     # SEND RFQ BUTTON
#     # =========================
#     if st.button("Send RFQ"):

#         selected_rows = edited_df[edited_df["Select"] == True]

#         if selected_rows.empty:
#             st.warning("Please select at least one vendor.")
#             return

#         conn = get_connection()
#         cursor = conn.cursor()

#         # Create RFQ master once
#         cursor.execute("""
#             INSERT INTO rfq_master (
#                 project_id,
#                 material_name,
#                 rfq_date,
#                 status
#             )
#             VALUES (?, ?, datetime('now'), ?)
#         """, (
#             st.session_state.active_project_id,
#             selected_material,
#             "sent"
#         ))

#         rfq_id = cursor.lastrowid

#         # Loop vendors
#         for _, row in selected_rows.iterrows():

#             vendor_name = row["Vendor_Name"]
#             vendor_email = row["Email"]

#             email_sent = send_rfq_email(
#                 vendor_email,
#                 vendor_name,
#                 st.session_state.active_project_code,
#                 selected_material,
#                 material_row["BOQ_Quantity"],
#                 rfq_id
#             )

#             if email_sent:
#                 st.success(f"RFQ sent to {vendor_name}")
#             else:
#                 st.error(f"Failed to send email to {vendor_name}")

#             cursor.execute("""
#                 INSERT INTO rfq_vendors (
#                     rfq_id,
#                     vendor_name,
#                     vendor_email,
#                     status
#                 )
#                 VALUES (?, ?, ?, ?)
#             """, (
#                 rfq_id,
#                 vendor_name,
#                 vendor_email,
#                 "RFQ Sent"
#             ))

#         conn.commit()
#         conn.close()

#         st.success("RFQ process completed.")

# def rfq_tracking_section():

#     st.title("📊 RFQ Tracking ")

#     conn = get_connection()
#     cursor = conn.cursor()

#     # Get project list for dropdown
#     cursor.execute("SELECT id, project_code FROM projects")
#     projects = cursor.fetchall()

#     if not projects:
#         st.info("No projects found.")
#         conn.close()
#         return

#     project_dict = {p["project_code"]: p["id"] for p in projects}

#     selected_project = st.selectbox(
#         "Select Project",
#         list(project_dict.keys())
#     )

#     selected_project_id = project_dict[selected_project]

#     # Fetch RFQ data for selected project
#     cursor.execute("""
#         SELECT 
#             rm.id as rfq_id,
#             rm.material_name,
#             rm.status as rfq_status,
#             rv.vendor_name,
#             rv.vendor_email,
#             rv.status as vendor_status,
#             rv.unit_price,
#             rv.delivery_time,
#             rv.payment_terms
#         FROM rfq_master rm
#         LEFT JOIN rfq_vendors rv ON rm.id = rv.rfq_id
#         WHERE rm.project_id = ?
#         ORDER BY rm.id DESC
#     """, (selected_project_id,))

#     rows = cursor.fetchall()
#     conn.close()

#     if not rows:
#         st.warning("No RFQs found for this project.")
#         return

#     df = pd.DataFrame(rows, columns=[
#         "RFQ ID",
#         "Material",
#         "RFQ Status",
#         "Vendor",
#         "Vendor Email",
#         "Vendor Status",
#         "Unit Price",
#         "Delivery Days",
#         "Payment Terms"
#     ])

#     st.dataframe(df, use_container_width=True)

# # =========================
# # DASHBOARD
# # =========================
# def dashboard():
#     st.title("📦 Procurement Dashboard")

#     menu = st.sidebar.radio(
#         "Navigation",
#         ["Projects", "Materials", "RFQ Tracking"]
#     )

#     if menu == "Projects":
#         project_section()

#     elif menu == "Materials":
#         material_section()

#     elif menu == "RFQ Tracking":
#         rfq_tracking_section()


# # =========================
# # APP FLOW
# # =========================
# if not st.session_state.logged_in:
#     login_page()
# else:
#     dashboard()

# correct code

# import streamlit as st
# import pandas as pd
# import uuid
# from pathlib import Path
# #from services.db import get_connection
# from services.db import get_connection, get_cursor
# from services.email_service import send_rfq_email
# from services.email_service import send_approval_email
# query_params = st.query_params
# page = query_params.get("page")

# st.set_page_config(page_title="Procurement System", layout="wide")


# # =========================
# # SESSION INIT
# # =========================

# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# if "active_project_id" not in st.session_state:
#     st.session_state.active_project_id = None

# # =========================
# # LOAD FILES
# # =========================

# @st.cache_data
# def load_boq():
#     path = Path("data/Design_boq.xlsx")

#     if not path.exists():
#         return None

#     return pd.read_excel(path)


# @st.cache_data
# def load_vendor_data():
#     path = Path("data/past_vendor_data.xlsx")

#     if not path.exists():
#         return None

#     df = pd.read_excel(path)
#     df.columns = df.columns.str.strip()

#     return df


# # =========================
# # LOGIN PAGE
# # =========================

# def login_page():

#     st.title("🔐 Procurement Login")

#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")

#     if st.button("Login"):

#         # conn = get_connection()
#         # cursor = conn.cursor()
#         conn, cursor = get_cursor()
#         cursor.execute(
#             "SELECT * FROM users WHERE username=%s AND password=%s",
#             (username, password)
#         )

#         user = cursor.fetchone()
#         conn.close()

#         if user:

#             st.session_state.logged_in = True
#             st.success("Login successful")
#             st.rerun()

#         else:

#             st.error("Invalid credentials")


# # =========================
# # PROJECT SECTION
# # =========================

# def project_section():

#     st.subheader("📂 Select Project from Design BOQ")

#     boq_df = load_boq()

#     if boq_df is None:
#         st.error("BOQ file not found.")
#         return

#     unique_projects = boq_df["Project_ID"].dropna().unique()

#     selected_project_code = st.selectbox(
#         "Select Project ID",
#         unique_projects
        
#     )
#     #st.session_state.project_sheet_id = selected_project_code
#     st.session_state["selected_project_code"] = selected_project_code
#     if selected_project_code:

#         # conn = get_connection()
#         # cursor = conn.cursor()
#         conn, cursor = get_cursor()

#         cursor.execute(
#             "SELECT * FROM projects WHERE project_id=%s",
#             (selected_project_code,)
#         )

#         existing = cursor.fetchone()

#         if not existing:

#             cursor.execute(
#                 """
#                 INSERT INTO projects
#                 (project_id, project_name)
#                 VALUES (%s, %s)
#                 """,
#                 (selected_project_code, selected_project_code)
#             )

#             conn.commit()

#         cursor.execute(
#             "SELECT id FROM projects WHERE project_id=%s",
#             (selected_project_code,)
#         )

#         project_id = cursor.fetchone()["id"]

#         conn.close()

#         st.session_state.active_project_id = project_id
#         st.session_state.project_sheet_id = selected_project_code

#         st.success(f"Project {selected_project_code} Ready for Procurement")


# # =========================
# # MATERIAL SECTION
# # =========================

# def material_section():
#     selected_project_code = st.session_state.get("selected_project_code")
#     if not st.session_state.active_project_id:

#         st.warning("Please select project first.")
#         return

#     st.subheader("📐 Materials From BOQ")

#     boq_df = load_boq()

#     project_materials = boq_df[
#         boq_df["Project_ID"] == selected_project_code
#     ]

#     if project_materials.empty:

#         st.info("No materials found for this project.")
#         return

#     material_names = project_materials["Material_Name"].unique()

#     selected_material = st.selectbox(
#         "Select Material",
#         material_names
#     )

#     if not selected_material:
#         return

#     material_row = project_materials[
#         project_materials["Material_Name"] == selected_material
#     ]

#     material_row = material_row.iloc[0]
#     quantity = material_row["BOQ_Quantity"]
#     uom = material_row["uom"]
#     specification = material_row["Specification"]
    
    
#     st.markdown("### Material Details")

#     st.write(f"**Material:** {selected_material}")
#     st.write(f"**Quantity:** {quantity}")
#     st.write(f"**Specification:** {specification}")

#     st.markdown("### 📊 Past Vendor History")

#     vendor_df = load_vendor_data()
#     vendor_df.columns = vendor_df.columns.str.strip()

#     if vendor_df is None:

#         st.warning("Past vendor data file not found.")
#         return

#     vendor_df["Material_Name"] = vendor_df["Material_Name"].str.strip().str.lower()

#     selected_material_clean = selected_material.strip().lower()

#     filtered_vendors = vendor_df[
#         vendor_df["Material_Name"] == selected_material_clean
#     ]

#     if filtered_vendors.empty:

#         st.warning("No past vendor history found.")
#         return

#     filtered_vendors = filtered_vendors.copy()
#     filtered_vendors["Select"] = False

#     edited_df = st.data_editor(
#         filtered_vendors,
#         use_container_width=True
#     )

#     # =========================
#     # SEND RFQ
#     # =========================

#     if st.button("Send RFQ"):

#         selected_rows = edited_df[edited_df["Select"] == True]

#         if selected_rows.empty:

#             st.warning("Select at least one vendor.")
#             return

#         # conn = get_connection()
#         # cursor = conn.cursor()
#         conn, cursor = get_cursor()

#         # rfq_token = str(uuid.uuid4())[:8]

#         # cursor.execute(
#         #     """
#         #     INSERT INTO rfq_master
#         #     (project_id, material_name, rfq_date, status)
#         #     VALUES (%s, %s, CURRENT_TIMESTAMP, %s)
#         #     """,
#         #     (
#         #         st.session_state.active_project_id,
#         #         selected_material,
#         #         "sent"
#         #     )
#         # )

#         # rfq_id = cursor.lastrowid
#         cursor.execute(
#            """
#             INSERT INTO rfq_master
#             (project_id, material_name, rfq_date, status)
#             VALUES (%s, %s, CURRENT_TIMESTAMP, %s)
#             RETURNING rfq_id
#             """,
#             (
#                 st.session_state.active_project_id,
#                 selected_material,
#                 "sent"
#             )
#         )

#         rfq_id = cursor.fetchone()["rfq_id"]

#         # SEND EMAILS

#         for _, row in selected_rows.iterrows():

#             vendor_name = row["Vendor_Name"]
#             vendor_email = row["Email"]

#             email_sent = send_rfq_email(
#                 vendor_email,
#                 vendor_name,
#                 selected_material,
#                 quantity, 
#                 uom,
#                 specification,
#                 rfq_id,
#                 st.session_state.project_sheet_id
#             )

#             if email_sent:

#                 st.success(f"RFQ sent to {vendor_name}")

#             else:

#                 st.error(f"Failed to send email to {vendor_name}")

#             cursor.execute(
#                 """
#                 INSERT INTO vendor_quotes
#                 (rfq_id, vendor_name, vendor_email, status)
#                 VALUES (%s, %s, %s, %s)
#                 """,
#                 (
#                     rfq_id,
#                     vendor_name,
#                     vendor_email,
#                     "RFQ Sent"
#                 )
#             )

#         conn.commit()
#         conn.close()

#         st.success("RFQ process completed.")


# # =========================
# # RFQ TRACKING
# # =========================

# def rfq_tracking_section():

#     st.title("📊 RFQ Tracking")

#     # Fetch vendor replies button
#     #if st.button("📩 Fetch Vendor Replies"):
#         #with st.spinner("Reading vendor emails..."):
#             #from services.gmail_service import fetch_rfq_replies
#             #fetch_rfq_replies()
#         #st.success("Vendor replies processed successfully")
#     if st.button("📩 Fetch Vendor Replies"):
#         try:
#             with st.spinner("Reading vendor emails..."):
#                 from services.gmail_service import fetch_rfq_replies
#                 fetch_rfq_replies()
#             st.success("Vendor replies processed successfully")
#         except Exception as e:
#             st.error("REAL ERROR:")
#             st.write(e)
#     # conn = get_connection()
#     # cursor = conn.cursor()
#     conn, cursor = get_cursor()

#     cursor.execute("SELECT id, project_id FROM projects")
#     projects = cursor.fetchall()

#     if not projects:
#         st.info("No projects found.")
#         conn.close()
#         return

#     project_dict = {p["project_id"]: p["id"] for p in projects}

#     selected_project = st.selectbox(
#         "Select Project",
#         list(project_dict.keys())
#     )

#     selected_project_id = project_dict[selected_project]

#     #cursor.execute(
#          #"""
#     #     SELECT
#     #         rm.rfq_id,
#     #         rm.material_name,
#     #         rm.status,
#     #         rv.vendor_name,
#     #         rv.status
#     #     FROM rfq_master rm
#     #     LEFT JOIN vendor_quotes rv ON rm.rfq_id = rv.rfq_id
#     #     WHERE rm.project_id = %s
#     #     ORDER BY rm.rfq_id DESC
#     #     """,
#     #     (selected_project_id,)
#     #)
#     cursor.execute("""
#         SELECT
#             rm.rfq_id AS "RFQ ID",
#             rm.material_name AS "Material",
#             rm.status AS "RFQ Status",
#             rv.vendor_name AS "Vendor",
#             rv.status AS "Vendor Status"
#         FROM rfq_master rm
#         LEFT JOIN vendor_quotes rv ON rm.rfq_id = rv.rfq_id
#         WHERE rm.project_id = %s
#         ORDER BY rm.rfq_id DESC
#         """, (selected_project_id,))

#     rows = cursor.fetchall()
#     conn.close()

#     if not rows:
#         st.warning("No RFQs found.")
#         return

#     df = pd.DataFrame(rows)

#     # df.columns = [
#     #     "RFQ ID",
#     #     "Material",
#     #     "RFQ Status",
#     #     "Vendor",
#     #     "Vendor Status"
#     # ]

#     # st.dataframe(df, use_container_width=True)
#     #rows = cursor.fetchall()
#     #df = pd.DataFrame(rows)

#     st.dataframe(df, use_container_width=True)

# # def comparison_section():

# #     st.title("📊 Vendor Quote Comparison")

# #     # conn = get_connection()
# #     # cursor = conn.cursor()
# #     conn, cursor = get_cursor()

# #     # =========================
# #     # Select Project
# #     # =========================
# #     cursor.execute("SELECT id, project_id FROM projects ORDER BY id DESC")
# #     projects = cursor.fetchall()

# #     if not projects:
# #         st.warning("No projects found.")
# #         conn.close()
# #         return

# #     project_dict = {p["project_id"]: p["id"] for p in projects}
# #     selected_project = st.selectbox("Select Project", list(project_dict.keys()))
# #     selected_project_id = project_dict[selected_project]

# #     # =========================
# #     # Select Material
# #     # =========================
# #     cursor.execute(
# #         "SELECT DISTINCT material_name FROM rfq_master WHERE project_id=%s",
# #         (selected_project_id,)
# #     )
# #     materials = cursor.fetchall()
# #     if not materials:
# #         st.warning("No materials found for this project.")
# #         conn.close()
# #         return
    
# #     material_list = [m["material_name"] for m in materials]
# #     selected_material = st.selectbox("Select Material", material_list)

# #     # cursor.execute("""
# #     # SELECT rfq_id, vendor_name, unit_price, delivery_time, payment_terms
# #     # FROM vendor_quotes
# #     # ORDER BY rfq_id DESC
# #     # """)
# #     cursor.execute("""
# #     SELECT rfq_id, vendor_name, unit_price, delivery_time, payment_terms
# #     FROM vendor_quotes
# #     WHERE rfq_id IN (
# #         SELECT rfq_id FROM rfq_master
# #         WHERE project_id = %s AND LOWER(TRIM(material_name)) = LOWER(TRIM(%s))
# #     )
# #     """, (selected_project_id, selected_material))
    
# #     #print("ROWS FROM DB:", rows)
    
# #     rows = cursor.fetchall()
# #     # df = pd.DataFrame([dict(r) for r in rows])
# #     if not rows:
# #         st.warning("No quotes found.")
# #     return

# #     df = pd.DataFrame([dict(r) for r in rows])
# #     # =========================
# #     # Rename columns for display
# #     # =========================
# #     df.columns = ["RFQ ID","Vendor", "Unit Price", "Delivery Time", "Payment Terms"]

# #     # Add selection column
# #     df["Select Vendor"] = False
    
# #     df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce")

# #     df["Delivery Time"] = df["Delivery Time"].astype(str)
# #     df["Payment Terms"] = df["Payment Terms"].astype(str)

# #     edited_df = st.data_editor(
# #         df,
# #         use_container_width=True,
# #         num_rows="fixed"
# #     )
# #     column_config={
# #         "RFQ ID": st.column_config.Column(disabled=True),
# #         "Vendor": st.column_config.Column(disabled=True),
# #         "Unit Price": st.column_config.NumberColumn(),
# #         "Delivery Time": st.column_config.TextColumn(),
# #         "Payment Terms": st.column_config.TextColumn()
# #     },
  
# #     if st.button("💾 Save Edited Quotes"):

# #         # conn = get_connection()
# #         # cursor = conn.cursor()
# #         conn, cursor = get_cursor()

# #         for _, row in edited_df.iterrows():

# #             cursor.execute("""
# #             UPDATE vendor_quotes
# #             SET
# #                 unit_price = %s,
# #                 delivery_time = %s,
# #                 payment_terms = %s
# #             WHERE rfq_id = %s
# #             """, (
# #                 row["Unit Price"],
# #                 row["Delivery Time"],
# #                 row["Payment Terms"],
# #                 row["RFQ ID"]
# #             ))

# #         conn.commit()
# #         conn.close()

# #         st.success("Quotes updated successfully")
# #     # Get selected vendor
# #     selected_vendor = edited_df[edited_df["Select Vendor"] == True]


# #     # =========================
# #     # Highlight best price
# #     # =========================
# #     try:
# #         df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce")
# #         best_vendor = df.loc[df["Unit Price"].idxmin()]
# #         st.success(f"💰 Lowest Quote: {best_vendor['Vendor']} ({best_vendor['Unit Price']})")
# #     except:
# #         pass
    
# #     if st.button("📤 Send Selected Vendor for Approval"):

# #         if selected_vendor.empty:
# #             st.warning("Please select a vendor first.")
# #             return


# #         vendor_row = selected_vendor.iloc[0]

# #         # conn = get_connection()
# #         # cursor = conn.cursor()
# #         conn, cursor = get_cursor()

# #         # Check if approval already exists
# #         cursor.execute("""
# #         SELECT * FROM vendor_approvals
# #         WHERE project_id=%s AND material_name=%s AND vendor_name=%s AND status='Pending'
# #         """, (
# #         selected_project_id,
# #         selected_material,
# #         vendor_row["Vendor"]
# #         ))

# #         existing = cursor.fetchone()

# #         if existing:
# #             st.warning("Approval request already sent for this vendor.")
# #         else:
# #             cursor.execute("""
# #             INSERT INTO vendor_approvals
# #             (project_id, material_name, vendor_name, unit_price, delivery_time, payment_terms, status)
# #             VALUES (%s, %s, %s, %s, %s, %s, %s)
# #             """, (
# #             selected_project_id,
# #             selected_material,
# #             vendor_row["Vendor"],
# #             vendor_row["Unit Price"],
# #             vendor_row["Delivery Time"],
# #             vendor_row["Payment Terms"],
# #             "Pending"
# #             ))

# #             conn.commit()
# #             st.success("Vendor sent to manager for approval.")

# #         cursor.execute("""
# #         UPDATE rfq_master
# #         SET approval_status='Pending'
# #         WHERE project_id=%s AND material_name=%s
# #         """, (selected_project_id, selected_material))

# #         conn.commit()
# #         conn.close()

# #         st.success("Vendor sent to manager for approval.")
# #         send_approval_email(
# #             selected_project_id,
# #             selected_material,
# #             vendor_row["Vendor"],
# #              vendor_row["Unit Price"]
# #         )
# def comparison_section():

#     st.title("📊 Vendor Quote Comparison")

#     conn, cursor = get_cursor()

#     cursor.execute("SELECT id, project_id FROM projects ORDER BY id DESC")
#     projects = cursor.fetchall()

#     if not projects:
#         st.warning("No projects found.")
#         conn.close()
#         return

#     project_dict = {p["project_id"]: p["id"] for p in projects}
#     selected_project = st.selectbox("Select Project", list(project_dict.keys()))
#     selected_project_id = project_dict[selected_project]

#     cursor.execute(
#         "SELECT DISTINCT material_name FROM rfq_master WHERE project_id=%s",
#         (selected_project_id,)
#     )

#     materials = cursor.fetchall()

#     if not materials:
#         st.warning("No materials found.")
#         conn.close()
#         return

#     material_list = [m["material_name"] for m in materials]
#     selected_material = st.selectbox("Select Material", material_list)

#     cursor.execute("""
#         SELECT rfq_id, vendor_name, unit_price, delivery_time, payment_terms
#         FROM vendor_quotes
#         WHERE rfq_id IN (
#             SELECT rfq_id FROM rfq_master
#             WHERE project_id = %s 
#             AND LOWER(TRIM(material_name)) = LOWER(TRIM(%s))
#         )
#     """, (selected_project_id, selected_material))

#     rows = cursor.fetchall()
#     conn.close()

#     if not rows:
#         st.warning("No quotes found.")
#         return

#     df = pd.DataFrame([dict(r) for r in rows])

#     df.columns = ["RFQ ID","Vendor", "Unit Price", "Delivery Time", "Payment Terms"]

#     df["Select Vendor"] = False

#     df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce")

#     edited_df = st.data_editor(df, use_container_width=True)

#     if st.button("💾 Save Edited Quotes"):

#         conn, cursor = get_cursor()

#         for _, row in edited_df.iterrows():

#             cursor.execute("""
#                 UPDATE vendor_quotes
#                 SET
#                     unit_price = %s,
#                     delivery_time = %s,
#                     payment_terms = %s
#                 WHERE rfq_id = %s
#             """, (
#                 row["Unit Price"],
#                 row["Delivery Time"],
#                 row["Payment Terms"],
#                 row["RFQ ID"]
#             ))

#         conn.commit()
#         conn.close()

#         st.success("Quotes updated successfully")

#     selected_vendor = edited_df[edited_df["Select Vendor"] == True]

#     try:
#         best_vendor = df.loc[df["Unit Price"].idxmin()]
#         st.success(f"💰 Lowest Quote: {best_vendor['Vendor']} ({best_vendor['Unit Price']})")
#     except:
#         pass
# def manager_approval_section():

#     st.title("🧾 Manager Vendor Approvals")

#     # conn = get_connection()
#     # cursor = conn.cursor()
#     conn, cursor = get_cursor()

#     cursor.execute("""
#     SELECT id, project_id, material_name, vendor_name, unit_price, delivery_time, payment_terms
#     FROM vendor_approvals
#     WHERE status='Pending'
#     """)

#     approvals = cursor.fetchall()

#     if not approvals:
#         st.info("No approvals pending.")
#         conn.close()
#         return

#     for row in approvals:

#         st.subheader(f"Project: {row['project_id']} | Material: {row['material_name']}")

#         st.write(f"Vendor: {row['vendor_name']}")
#         st.write(f"Unit Price: {row['unit_price']}")
#         st.write(f"Delivery: {row['delivery_time']}")
#         st.write(f"Payment Terms: {row['payment_terms']}")

#         col1, col2 = st.columns(2)

#         with col1:
           
#             if st.button(f"✅ Approve {row['id']}"):

#                 cursor.execute("""
#                 UPDATE vendor_approvals
#                 SET status='Approved'
#                 WHERE id=%s
#                 """, (row['id'],))

#                 cursor.execute("""
#                 UPDATE rfq_master
#                 SET
#                     status='Vendor Approved'
#                 WHERE project_id=%s AND material_name=%s
#                 """, (row['project_id'], row['material_name']))

#                 conn.commit()
#                 st.success("Vendor Approved")

#         with col2:
            
#             if st.button(f"❌ Reject {row['id']}"):

#                 cursor.execute("""
#                 UPDATE vendor_approvals
#                 SET status='Rejected'
#                 WHERE id=%s
#                 """, (row['id'],))

#                 cursor.execute("""
#                 UPDATE rfq_master
#                 SET status='Vendor Rejected'
#                 WHERE project_id=%s AND material_name=%s
#                 """, (row['project_id'], row['material_name']))

#                 conn.commit()
#                 st.success("Vendor Rejected")

#     conn.close()
# def costing_section():

#     st.title("💰 Project Costing")

#     # conn = get_connection()
#     # cursor = conn.cursor()
#     conn, cursor = get_cursor()

#     # Select Project
#     cursor.execute("SELECT id, project_id FROM projects")
#     projects = cursor.fetchall()

#     if not projects:
#         st.warning("No projects found.")
#         conn.close()
#         return

#     project_dict = {p["project_id"]: p["id"] for p in projects}

#     selected_project = st.selectbox("Select Project", list(project_dict.keys()))
#     selected_project_id = project_dict[selected_project]
#     st.write("Selected Project ID:", selected_project_id)

#     # Fetch Approved Vendors + RFQ Data
#     cursor.execute("""
#     SELECT 
#         rm.material_name,
#         rm.quantity,
#         rm.uom,
#         va.vendor_name,
#         va.unit_price
#     FROM vendor_approvals va
#     JOIN rfq_master rm 
#         ON rm.project_id = va.project_id 
#         AND LOWER(TRIM(rm.material_name)) = LOWER(TRIM(va.material_name))
#     WHERE va.project_id=%s 
#     AND va.status='Approved'
#     """, (selected_project_id,))

#     rows = cursor.fetchall()

#     if not rows:
#         st.warning("No approved vendors found.")
#         conn.close()
#         return

#     df = pd.DataFrame([dict(r) for r in rows])

#     # Calculate Total Cost per Material
#     df["Total Cost"] = df["quantity"] * df["unit_price"]

#     # Rename for UI
#     df.columns = [
#         "Material",
#         "Quantity",
#         "UOM",
#         "Vendor",
#         "Unit Price",
#         "Total Cost"
#     ]

#     st.subheader("📊 Material-wise Costing")
#     st.dataframe(df, use_container_width=True)

#     # Total Project Cost
#     total_project_cost = df["Total Cost"].sum()

#     st.markdown("---")
#     st.success(f"💰 Total Project Cost: ₹ {total_project_cost:,.2f}")

#     conn.close()
# # =========================
# # DASHBOARD
# # =========================

# def dashboard():

#     menu = st.sidebar.radio(
#         "Navigation",
#         ["Projects", "Materials", "RFQ Tracking", "Quote Comparison", "Manager Approval","Costing"]
#     )

#     if menu == "Projects":
#         project_section()

#     elif menu == "Materials":
#         material_section()

#     elif menu == "RFQ Tracking":
#         rfq_tracking_section()
    
#     elif menu == "Quote Comparison":
#         comparison_section()
    
#     elif menu == "Manager Approval":
#         manager_approval_section()
    
#     elif menu == "Costing":
#         costing_section()

# # =========================
# # APP FLOW
# # =========================

# if not st.session_state.logged_in:

#     login_page()

# else:

#     dashboard()


# import streamlit as st
# import pandas as pd
# from pathlib import Path
# from services.db import get_connection, get_cursor
# from services.email_service import send_rfq_email, send_approval_email

# # =========================
# # PAGE CONFIG — MUST BE FIRST
# # =========================
# st.set_page_config(page_title="Procurement System", layout="wide")

# # Read query params after set_page_config
# query_params = st.query_params
# page = query_params.get("page")


# # =========================
# # SESSION INIT
# # =========================

# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# if "active_project_id" not in st.session_state:
#     st.session_state.active_project_id = None


# # =========================
# # LOAD FILES
# # =========================

# def load_boq():
#     path = Path("data/Design_boq.xlsx")
#     if not path.exists():
#         return None
#     return pd.read_excel(path)


# def load_vendor_data():
#     path = Path("data/past_vendor_data.xlsx")
#     if not path.exists():
#         return None
#     df = pd.read_excel(path)
#     df.columns = df.columns.str.strip()
#     return df


# # =========================
# # LOGIN PAGE
# # =========================

# def login_page():

#     st.title("🔐 Procurement Login")

#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")

#     if st.button("Login"):
#         conn, cursor = get_cursor()
#         cursor.execute(
#             "SELECT * FROM users WHERE username=%s AND password=%s",
#             (username, password)
#         )
#         user = cursor.fetchone()
#         conn.close()

#         if user:
#             st.session_state.logged_in = True
#             st.success("Login successful")
#             st.rerun()
#         else:
#             st.error("Invalid credentials")


# # =========================
# # PROJECT SECTION
# # =========================

# def project_section():

#     st.subheader("📂 Select Project from Design BOQ")

#     boq_df = load_boq()

#     if boq_df is None:
#         st.error("BOQ file not found at data/Design_boq.xlsx")
#         return

#     unique_projects = boq_df["Project_ID"].dropna().unique()

#     selected_project_code = st.selectbox("Select Project ID", unique_projects)
#     st.session_state["selected_project_code"] = selected_project_code

#     if selected_project_code:
#         conn, cursor = get_cursor()

#         cursor.execute(
#             "SELECT * FROM projects WHERE project_id=%s",
#             (selected_project_code,)
#         )
#         existing = cursor.fetchone()

#         if not existing:
#             cursor.execute(
#                 "INSERT INTO projects (project_id, project_name) VALUES (%s, %s)",
#                 (selected_project_code, selected_project_code)
#             )
#             conn.commit()

#         cursor.execute(
#             "SELECT id FROM projects WHERE project_id=%s",
#             (selected_project_code,)
#         )
#         project_id = cursor.fetchone()["id"]
#         conn.close()

#         st.session_state.active_project_id = project_id
#         st.session_state.project_sheet_id = selected_project_code
#         st.success(f"Project {selected_project_code} ready for procurement")


# # =========================
# # MATERIAL SECTION
# # =========================

# def material_section():

#     selected_project_code = st.session_state.get("selected_project_code")

#     if not st.session_state.active_project_id:
#         st.warning("Please select a project first.")
#         return

#     st.subheader("📐 Materials From BOQ")

#     boq_df = load_boq()

#     project_materials = boq_df[boq_df["Project_ID"] == selected_project_code]

#     if project_materials.empty:
#         st.info("No materials found for this project.")
#         return

#     material_names = project_materials["Material_Name"].unique()
#     selected_material = st.selectbox("Select Material", material_names)

#     if not selected_material:
#         return

#     material_row = project_materials[
#         project_materials["Material_Name"] == selected_material
#     ].iloc[0]

#     quantity = material_row["BOQ_Quantity"]
#     uom = material_row["uom"]
#     specification = material_row["Specification"]

#     st.markdown("### Material Details")
#     st.write(f"**Material:** {selected_material}")
#     st.write(f"**Quantity:** {quantity} {uom}")
#     st.write(f"**Specification:** {specification}")

#     st.markdown("### 📊 Past Vendor History")

#     vendor_df = load_vendor_data()

#     if vendor_df is None:
#         st.warning("Past vendor data file not found at data/past_vendor_data.xlsx")
#         return

#     vendor_df["Material_Name"] = vendor_df["Material_Name"].str.strip().str.lower()
#     selected_material_clean = selected_material.strip().lower()

#     filtered_vendors = vendor_df[
#         vendor_df["Material_Name"] == selected_material_clean
#     ].copy()

#     if filtered_vendors.empty:
#         st.warning("No past vendor history found for this material.")
#         return

#     filtered_vendors["Select"] = False

#     edited_df = st.data_editor(filtered_vendors, use_container_width=True)

#     # =========================
#     # SEND RFQ
#     # =========================

#     if st.button("📤 Send RFQ"):

#         selected_rows = edited_df[edited_df["Select"] == True]

#         if selected_rows.empty:
#             st.warning("Select at least one vendor.")
#             return

#         conn, cursor = get_cursor()

#         cursor.execute(
#             """
#             INSERT INTO rfq_master
#                 (project_id, material_name, quantity, uom, specification, rfq_date, status)
#             VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s)
#             """,
#             (
#                 st.session_state.active_project_id,
#                 selected_material,
#                 float(quantity),
#                 str(uom),
#                 str(specification),
#                 "Sent"
#             )
#         )
#         cursor.execute("SELECT lastval() AS rfq_id")
#         rfq_id = cursor.fetchone()["rfq_id"]

#         for _, row in selected_rows.iterrows():
#             vendor_name = row["Vendor_Name"]
#             vendor_email = row["Email"]

#             email_sent = send_rfq_email(
#                 vendor_email,
#                 vendor_name,
#                 selected_material,
#                 quantity,
#                 uom,
#                 specification,
#                 rfq_id,
#                 st.session_state.project_sheet_id
#             )

#             if email_sent:
#                 st.success(f"✅ RFQ sent to {vendor_name}")
#             else:
#                 st.error(f"❌ Failed to send email to {vendor_name}")

#             cursor.execute(
#                 """
#                 INSERT INTO vendor_quotes
#                     (rfq_id, vendor_name, vendor_email, status)
#                 VALUES (%s, %s, %s, %s)
#                 """,
#                 (rfq_id, vendor_name, vendor_email, "RFQ Sent")
#             )

#         conn.commit()
#         conn.close()
#         st.success("RFQ process completed.")


# # =========================
# # RFQ TRACKING
# # =========================

# def rfq_tracking_section():

#     st.title("📊 RFQ Tracking")

#     if st.button("📩 Fetch Vendor Replies"):
#         try:
#             with st.spinner("Reading vendor emails..."):
#                 from services.gmail_service import fetch_rfq_replies
#                 fetch_rfq_replies()
#             st.success("Vendor replies processed successfully")
#         except Exception as e:
#             st.error(f"Error fetching replies: {e}")

#     conn, cursor = get_cursor()

#     cursor.execute("SELECT id, project_id FROM projects ORDER BY id DESC")
#     projects = cursor.fetchall()

#     if not projects:
#         st.info("No projects found.")
#         conn.close()
#         return

#     project_dict = {p["project_id"]: p["id"] for p in projects}
#     selected_project = st.selectbox("Select Project", list(project_dict.keys()))
#     selected_project_id = project_dict[selected_project]

#     cursor.execute("""
#         SELECT
#             rm.rfq_id        AS "RFQ ID",
#             rm.material_name AS "Material",
#             rm.status        AS "RFQ Status",
#             rv.vendor_name   AS "Vendor",
#             rv.status        AS "Vendor Status",
#             rm.approval_status  AS "Approval Status"
#         FROM rfq_master rm
#         LEFT JOIN vendor_quotes rv ON rm.rfq_id = rv.rfq_id
#         WHERE rm.project_id = %s
#         ORDER BY rm.rfq_id DESC
#     """, (selected_project_id,))

#     rows = cursor.fetchall()
#     conn.close()

#     if not rows:
#         st.warning("No RFQs found for this project.")
#         return

#     st.dataframe(pd.DataFrame(rows), use_container_width=True)


# # =========================
# # QUOTE COMPARISON
# # =========================

# def comparison_section():

#     st.title("📊 Vendor Quote Comparison")

#     conn, cursor = get_cursor()

#     cursor.execute("SELECT id, project_id FROM projects ORDER BY id DESC")
#     projects = cursor.fetchall()

#     if not projects:
#         st.warning("No projects found.")
#         conn.close()
#         return

#     project_dict = {p["project_id"]: p["id"] for p in projects}
#     selected_project = st.selectbox("Select Project", list(project_dict.keys()))
#     selected_project_id = project_dict[selected_project]

#     cursor.execute(
#         "SELECT DISTINCT material_name FROM rfq_master WHERE project_id=%s",
#         (selected_project_id,)
#     )
#     materials = cursor.fetchall()

#     if not materials:
#         st.warning("No materials found for this project.")
#         conn.close()
#         return

#     material_list = [m["material_name"] for m in materials]
#     selected_material = st.selectbox("Select Material", material_list)

#     cursor.execute("""
#         SELECT
#             vq.rfq_id,
#             vq.vendor_name,
#             vq.unit_price,
#             vq.delivery_time,
#             vq.payment_terms
#         FROM vendor_quotes vq
#         WHERE vq.rfq_id IN (
#             SELECT rfq_id FROM rfq_master
#             WHERE project_id = %s
#             AND LOWER(TRIM(material_name)) = LOWER(TRIM(%s))
#         )
#     """, (selected_project_id, selected_material))

#     rows = cursor.fetchall()
#     conn.close()

#     if not rows:
#         st.warning("No quotes received yet for this material.")
#         return

#     df = pd.DataFrame([dict(r) for r in rows])
#     df.columns = ["RFQ ID", "Vendor", "Unit Price", "Delivery Time", "Payment Terms"]
#     df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce")
#     df["Select Vendor"] = False

#     # Highlight best price
#     if df["Unit Price"].notna().any():
#         best_idx = df["Unit Price"].idxmin()
#         best_vendor = df.loc[best_idx]
#         st.success(f"💰 Lowest Quote: **{best_vendor['Vendor']}** at ₹ {best_vendor['Unit Price']:,.2f}")

#     edited_df = st.data_editor(
#         df,
#         use_container_width=True,
#         column_config={
#             "RFQ ID": st.column_config.Column(disabled=True),
#             "Vendor": st.column_config.Column(disabled=True),
#             "Unit Price": st.column_config.NumberColumn(format="₹%.2f"),
#             "Delivery Time": st.column_config.TextColumn(),
#             "Payment Terms": st.column_config.TextColumn(),
#             "Select Vendor": st.column_config.CheckboxColumn("Select"),
#         },
#         num_rows="fixed"
#     )

#     col1, col2 = st.columns(2)

#     with col1:
#         if st.button("💾 Save Edited Quotes"):
#             conn, cursor = get_cursor()
#             for _, row in edited_df.iterrows():
#                 cursor.execute("""
#                     UPDATE vendor_quotes
#                     SET unit_price = %s, delivery_time = %s, payment_terms = %s
#                     WHERE rfq_id = %s AND vendor_name = %s
#                 """, (
#                     row["Unit Price"],
#                     row["Delivery Time"],
#                     row["Payment Terms"],
#                     row["RFQ ID"],
#                     row["Vendor"]
#                 ))
#             conn.commit()
#             conn.close()
#             st.success("Quotes updated successfully")

#     with col2:
#         # if st.button("📤 Send Selected Vendor for Approval"):

#         #     selected_rows = edited_df[edited_df["Select Vendor"] == True]

#         #     if selected_rows.empty:
#         #         st.warning("Please select a vendor first.")
#         #         return

#         #     if len(selected_rows) > 1:
#         #         st.warning("Please select only one vendor for approval.")
#         #         return

#         #     vendor_row = selected_rows.iloc[0]

#         #     conn, cursor = get_cursor()

#         #     # Check for duplicate pending approval
#         #     cursor.execute("""
#         #         SELECT id FROM vendor_approvals
#         #         WHERE project_id=%s AND material_name=%s AND vendor_name=%s AND status='Pending'
#         #     """, (selected_project_id, selected_material, vendor_row["Vendor"]))

#         #     existing = cursor.fetchone()

#         #     if existing:
#         #         st.warning("Approval request already sent for this vendor.")
#         #         conn.close()
#         #         return

#         #     cursor.execute("""
#         #         INSERT INTO vendor_approvals
#         #             (project_id, material_name, vendor_name, unit_price,
#         #              delivery_time, payment_terms, status)
#         #         VALUES (%s, %s, %s, %s, %s, %s, %s)
#         #     """, (
#         #         int(selected_project_id),
#         #         selected_material,
#         #         vendor_row["Vendor"],
#         #         vendor_row["Unit Price"],
#         #         vendor_row["Delivery Time"],
#         #         vendor_row["Payment Terms"],
#         #         "Pending"
#         #     ))

#         #     cursor.execute("""
#         #         UPDATE rfq_master
#         #         SET approval_status = 'Pending'
#         #         WHERE project_id=%s AND LOWER(TRIM(material_name)) = LOWER(TRIM(%s))
#         #     """, (selected_project_id, selected_material))

#         #     conn.commit()
#         #     conn.close()

#         #     # Send email — pass project_id integer, material name, vendor name, price
#         #     send_approval_email(
#         #         selected_project_id,
#         #         selected_material,
#         #         vendor_row["Vendor"],
#         #         vendor_row["Unit Price"]
#         #     )

#         #     st.success(f"✅ {vendor_row['Vendor']} sent to manager for approval.")
#         if st.button("📤 Send Selected Vendor for Approval"):

#             selected_rows = edited_df[edited_df["Select Vendor"] == True]

#             if selected_rows.empty:
#                 st.warning("Please select a vendor first.")
#                 return

#             # if len(selected_rows) > 1:
#             #     st.warning("Please select only one vendor for approval.")
#             #     return

#             vendor_row = selected_rows.iloc[0]

#             conn, cursor = get_cursor()

#             try:
#                 cursor.execute("""
#                     SELECT id FROM vendor_approvals
#                     WHERE project_id=%s AND material_name=%s AND vendor_name=%s AND status='Pending'
#                 """, (selected_project_id, selected_material, vendor_row["Vendor"]))

#                 existing = cursor.fetchone()

#                 if existing:
#                     st.warning("Approval request already sent for this vendor.")
#                     conn.close()
#                     return

#                 cursor.execute("""
#                     INSERT INTO vendor_approvals
#                         (project_id, material_name, vendor_name, unit_price,
#                          delivery_time, payment_terms, status)
#                     VALUES (%s, %s, %s, %s, %s, %s, %s)
#                 """, (
#                     selected_project_id,
#                     selected_material,
#                     vendor_row["Vendor"],
#                     float(vendor_row["Unit Price"]),
#                     vendor_row["Delivery Time"],
#                     vendor_row["Payment Terms"],
#                     "Pending"
#                 ))

#                 cursor.execute("""
#                     UPDATE rfq_master
#                     SET approval_status = 'Pending'
#                     WHERE project_id=%s AND LOWER(TRIM(material_name)) = LOWER(TRIM(%s))
#                 """, (selected_project_id, selected_material))

#                 conn.commit()
#                 conn.close()

#                 send_approval_email(
#                     selected_project_id,
#                     selected_material,
#                     vendor_row["Vendor"],
#                     vendor_row["Unit Price"]
#                 )

#                 st.success(f"✅ {vendor_row['Vendor']} sent to manager for approval.")

#             except Exception as e:
#                 conn.rollback()
#                 conn.close()
#                 st.error("Error details:")
#                 st.exception(e)

# # =========================
# # MANAGER APPROVAL
# # =========================

# def manager_approval_section():

#     st.title("🧾 Manager Vendor Approvals")

#     conn, cursor = get_cursor()

#     cursor.execute("""
#         SELECT id, project_id, material_name, vendor_name,
#                unit_price, delivery_time, payment_terms
#         FROM vendor_approvals
#         WHERE status = 'Pending'
#         ORDER BY id DESC
#     """)

#     approvals = cursor.fetchall()

#     if not approvals:
#         st.info("No approvals pending.")
#         conn.close()
#         return

#     for row in approvals:
#         with st.expander(f"Project: {row['project_id']} | Material: {row['material_name']}"):
#             st.write(f"**Vendor:** {row['vendor_name']}")
#             st.write(f"**Unit Price:** ₹ {row['unit_price']}")
#             st.write(f"**Delivery:** {row['delivery_time']}")
#             st.write(f"**Payment Terms:** {row['payment_terms']}")

#             col1, col2 = st.columns(2)

#             with col1:
#                 if st.button(f"✅ Approve", key=f"approve_{row['id']}"):
#                     conn2, cursor2 = get_cursor()
#                     # cursor2.execute(
#                     #     "UPDATE vendor_approvals SET status='Approved' WHERE id=%s",
#                     #     (row["id"],)
#                     # )
#                     # cursor2.execute("""
#                     #     UPDATE rfq_master SET status='Vendor Approved'
#                     #     WHERE project_id=%s AND LOWER(TRIM(material_name))=LOWER(TRIM(%s))
#                     # """, (row["project_id"], row["material_name"]))

#                     cursor2.execute(
#                         "UPDATE vendor_approvals SET status='Approved' WHERE id=%s",
#                         (row["id"],)
#                     )
#                     cursor2.execute("""
#                         UPDATE rfq_master SET status='Vendor Approved', approval_status='Approved'
#                         WHERE project_id=%s AND LOWER(TRIM(material_name))=LOWER(TRIM(%s))
#                     """, (row["project_id"], row["material_name"]))

#                     conn2.commit()
#                     conn2.close()
#                     st.success("Vendor Approved ✅")
#                     st.rerun()

#             with col2:
#                 if st.button(f"❌ Reject", key=f"reject_{row['id']}"):
#                     conn2, cursor2 = get_cursor()
#                     # cursor2.execute(
#                     #     "UPDATE vendor_approvals SET status='Rejected' WHERE id=%s",
#                     #     (row["id"],)
#                     # )
#                     # cursor2.execute("""
#                     #     UPDATE rfq_master SET status='Vendor Rejected'
#                     #     WHERE project_id=%s AND LOWER(TRIM(material_name))=LOWER(TRIM(%s))
#                     # """, (row["project_id"], row["material_name"]))
#                     # conn2.commit()
#                     cursor2.execute(
#                         "UPDATE vendor_approvals SET status='Rejected' WHERE id=%s",
#                        (row["id"],)
#                     )
#                     cursor2.execute("""
#                         UPDATE rfq_master SET status='Vendor Rejected', approval_status='Rejected'
#                         WHERE project_id=%s AND LOWER(TRIM(material_name))=LOWER(TRIM(%s))
#                     """, (row["project_id"], row["material_name"]))

#                     conn2.close()
#                     st.success("Vendor Rejected")
#                     st.rerun()

#     conn.close()


# # =========================
# # COSTING SECTION
# # =========================

# def costing_section():

#     st.title("💰 Project Costing")

#     conn, cursor = get_cursor()

#     cursor.execute("SELECT id, project_id FROM projects ORDER BY id DESC")
#     projects = cursor.fetchall()

#     if not projects:
#         st.warning("No projects found.")
#         conn.close()
#         return

#     project_dict = {p["project_id"]: p["id"] for p in projects}
#     selected_project = st.selectbox("Select Project", list(project_dict.keys()))
#     selected_project_id = project_dict[selected_project]

#     cursor.execute("""
#         SELECT
#             rm.material_name,
#             rm.quantity,
#             rm.uom,
#             va.vendor_name,
#             va.unit_price
#         FROM vendor_approvals va
#         JOIN rfq_master rm
#             ON rm.project_id = va.project_id
#             AND LOWER(TRIM(rm.material_name)) = LOWER(TRIM(va.material_name))
#         WHERE va.project_id = %s AND va.status = 'Approved'
#         ORDER BY rm.material_name
#     """, (selected_project_id,))

#     rows = cursor.fetchall()
#     conn.close()

#     if not rows:
#         st.warning("No approved vendors found for this project.")
#         return

#     df = pd.DataFrame([dict(r) for r in rows])
#     df.columns = ["Material", "Quantity", "UOM", "Vendor", "Unit Price"]
#     df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce")
#     df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
#     df["Total Cost"] = df["Quantity"] * df["Unit Price"]

#     st.subheader("📊 Material-wise Costing")
#     st.dataframe(
#         df.style.format({"Unit Price": "₹{:,.2f}", "Total Cost": "₹{:,.2f}"}),
#         use_container_width=True
#     )

#     st.markdown("---")
#     total = df["Total Cost"].sum()
#     st.success(f"💰 Total Project Cost: ₹ {total:,.2f}")


# # =========================
# # DASHBOARD
# # =========================

# def dashboard():

#     st.sidebar.title("🏗️ Procurement System")
#     menu = st.sidebar.radio(
#         "Navigation",
#         ["Projects", "Materials & RFQ", "RFQ Tracking",
#          "Quote Comparison", "Manager Approval", "Costing"]
#     )

#     if menu == "Projects":
#         project_section()
#     elif menu == "Materials & RFQ":
#         material_section()
#     elif menu == "RFQ Tracking":
#         rfq_tracking_section()
#     elif menu == "Quote Comparison":
#         comparison_section()
#     elif menu == "Manager Approval":
#         manager_approval_section()
#     elif menu == "Costing":
#         costing_section()

#     if st.sidebar.button("🚪 Logout"):
#         st.session_state.logged_in = False
#         st.rerun()


# # =========================
# # APP ENTRY POINT
# # =========================

# if not st.session_state.logged_in:
#     login_page()
# else:
#     dashboard()

# New version #

import streamlit as st
import pandas as pd
from pathlib import Path
from services.db import get_cursor
from services.email_service import (
    send_rfq_email,
    send_reverse_rfq_email,
    send_approval_email,
)

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Procurement System",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
def _init():
    defaults = {
        "section":               None,
        "logged_in":             False,
        "design_logged_in":      False,
        "active_project_id":     None,
        "project_sheet_id":      None,
        "selected_project_code": None,
        "page":                  "projects",
        "design_page":           "boq",
        "show_reverse_form":     False,
        "reverse_rfq_vendors":   [],
        "reverse_rfq_df":        None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ─────────────────────────────────────────────────────────────
# DATA LOADERS
# ─────────────────────────────────────────────────────────────
def load_boq():
    path = Path("data/Design_boq.xlsx")
    if not path.exists():
        return None
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    df["Project_ID"] = df["Project_ID"].astype(str).str.strip()
    return df


def load_vendor_history():
    conn, cursor = get_cursor()
    cursor.execute("SELECT * FROM vendor_history ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return None
    return pd.DataFrame([dict(r) for r in rows])


def append_to_vendor_history(new_rows: list):
    conn, cursor = get_cursor()
    try:
        for row in new_rows:
            cursor.execute("""
                INSERT INTO vendor_history
                    (vendor_name, email, material_name, project_name,
                     project_id, unit_price, quantity, uom,
                     delivery_time, payment_terms, date)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                row.get("Vendor_Name"),
                row.get("Email"),
                row.get("Material_Name"),
                row.get("Project_Name"),
                str(row.get("Project_ID", "")),
                row.get("Unit_Price"),
                row.get("Quantity"),
                row.get("uom", "Nos"),
                row.get("Delivery_Time"),
                row.get("Payment_Terms"),
                row.get("Date"),
            ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error saving vendor history: {e}")
    finally:
        conn.close()


def check_login(username, password):
    conn, cursor = get_cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()
    return user


# ─────────────────────────────────────────────────────────────
# LANDING PAGE
# ─────────────────────────────────────────────────────────────
def landing_page():
    st.markdown("## 🏗️ Procurement Management System")
    st.markdown("Select the section you want to access.")
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown("### 📐 Design")
        st.markdown("Upload BOQ excel files for new projects.")
        if st.button("Open Design Section", use_container_width=True):
            st.session_state.section = "design"
            st.rerun()
    with col3:
        st.markdown("### 🛒 Procurement")
        st.markdown("Manage RFQs, compare quotes, send for approval.")
        if st.button("Open Procurement Section", use_container_width=True):
            st.session_state.section = "procurement"
            st.rerun()


# ─────────────────────────────────────────────────────────────
# DESIGN SECTION  (FIX 1: login required)
# ─────────────────────────────────────────────────────────────
def design_login_page():
    st.markdown("## 📐 Design Section — Login")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Username", key="d_user")
        password = st.text_input("Password", type="password", key="d_pass")
        if st.button("Login", use_container_width=True, key="d_login"):
            if check_login(username, password):
                st.session_state.design_logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")
        if st.button("← Back", use_container_width=True):
            st.session_state.section = None
            st.rerun()


def design_section():
    with st.sidebar:
        st.markdown("### 📐 Design")
        st.markdown("---")
        if st.button("📂 Upload BOQ", use_container_width=True):
            st.session_state.design_page = "boq"
            st.rerun()
        if st.button("📊 View Current BOQ", use_container_width=True):
            st.session_state.design_page = "view"
            st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.design_logged_in = False
            st.rerun()
        if st.button("← Main Menu", use_container_width=True):
            st.session_state.section = None
            st.session_state.design_logged_in = False
            st.rerun()

    if st.session_state.design_page == "view":
        st.markdown("## 📊 Current BOQ")
        boq_df = load_boq()
        if boq_df is None:
            st.info("No BOQ uploaded yet.")
        else:
            st.dataframe(boq_df, use_container_width=True, hide_index=True)
        return

    # Upload BOQ page
    st.markdown("## 📂 Upload Design BOQ")
    st.markdown("""
    **Required Excel columns:**
    | Column | Description |
    |---|---|
    | `Project_ID` | Same value for all rows of the same project (e.g. PROJ001) |
    | `Material_Name` | Name of the material |
    | `BOQ_Quantity` | Required quantity |
    | `uom` | Unit of measure (Nos, kg, m, etc.) |
    | `Specification` | Technical specification |
    """)

    uploaded = st.file_uploader("Upload BOQ Excel (.xlsx)", type=["xlsx"])
    if uploaded:
        try:
            df = pd.read_excel(uploaded)
            df.columns = df.columns.str.strip()
            required = ["Project_ID", "Material_Name", "BOQ_Quantity", "uom", "Specification"]
            missing  = [c for c in required if c not in df.columns]
            if missing:
                st.error(f"Missing columns: {', '.join(missing)}")
                st.info(f"Your columns: {', '.join(df.columns.tolist())}")
                return

            # FIX 2: preserve Project_ID as string, no auto-increment
            df["Project_ID"] = df["Project_ID"].astype(str).str.strip()

            st.success("File validated!")
            st.dataframe(df, use_container_width=True, hide_index=True)

            summary = df.groupby("Project_ID")["Material_Name"].count().reset_index()
            summary.columns = ["Project ID", "Materials"]
            st.markdown("**Project Summary:**")
            st.dataframe(summary, use_container_width=True, hide_index=True)

            if st.button("💾 Save as Active BOQ", use_container_width=True):
                Path("data").mkdir(exist_ok=True)
                df.to_excel("data/Design_boq.xlsx", index=False)
                st.success("BOQ saved!")
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")


# ─────────────────────────────────────────────────────────────
# PROCUREMENT LOGIN
# ─────────────────────────────────────────────────────────────
def procurement_login_page():
    st.markdown("## 🔐 Procurement Login")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Username", key="p_user")
        password = st.text_input("Password", type="password", key="p_pass")
        if st.button("Login", use_container_width=True, key="p_login"):
            if check_login(username, password):
                st.session_state.logged_in = True
                st.session_state.page = "projects"
                st.rerun()
            else:
                st.error("Invalid credentials")
        if st.button("← Back", use_container_width=True):
            st.session_state.section = None
            st.rerun()


# ─────────────────────────────────────────────────────────────
# PROCUREMENT SIDEBAR NAV  (FIX 4: always visible)
# ─────────────────────────────────────────────────────────────
def procurement_nav():
    with st.sidebar:
        st.markdown("### 🛒 Procurement")
        if st.session_state.project_sheet_id:
            st.caption(f"📂 {st.session_state.project_sheet_id}")
        st.markdown("---")

        nav_items = [
            ("projects",   "📂 Projects"),
            ("materials",  "📐 Materials & RFQ"),
            ("tracking",   "📊 RFQ Tracking"),
            ("comparison", "⚖️ Quote Comparison"),
            ("approval",   "🧾 Manager Approval"),
            ("costing",    "💰 Costing"),
        ]

        for key, label in nav_items:
            active = st.session_state.page == key
            if st.button(
                f"› {label}" if active else label,
                use_container_width=True,
                key=f"nav_{key}",
                type="primary" if active else "secondary",
            ):
                st.session_state.page = key
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.active_project_id = None
            st.session_state.page = "projects"
            st.rerun()
        if st.button("← Main Menu", use_container_width=True):
            st.session_state.section = None
            st.session_state.logged_in = False
            st.rerun()


# ─────────────────────────────────────────────────────────────
# PAGE 1 — PROJECTS
# ─────────────────────────────────────────────────────────────
def projects_page():
    st.markdown("## 📂 Select Project")

    boq_df = load_boq()
    if boq_df is None:
        st.error("BOQ file not found. Ask the design team to upload it.")
        return

    unique_projects = boq_df["Project_ID"].dropna().unique()
    selected = st.selectbox("Select Project ID", unique_projects)
    st.session_state.selected_project_code = str(selected).strip()

    if selected:
        conn, cursor = get_cursor()
        selected_str = str(selected).strip()
        cursor.execute("SELECT * FROM projects WHERE project_id=%s", (selected_str,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO projects (project_id, project_name) VALUES (%s, %s)",
                (selected_str, selected_str)
            )
            conn.commit()
        cursor.execute("SELECT id FROM projects WHERE project_id=%s", (selected_str,))
        row = cursor.fetchone()
        conn.close()

        st.session_state.active_project_id = row["id"]
        st.session_state.project_sheet_id  = selected_str

        project_materials = boq_df[boq_df["Project_ID"] == selected_str]
        st.success(f"Project **{selected_str}** — {len(project_materials)} materials")
        st.dataframe(
            project_materials[["Material_Name", "BOQ_Quantity", "uom", "Specification"]],
            use_container_width=True,
            hide_index=True,
        )

        if st.button("Go to Materials & RFQ →", use_container_width=True):
            st.session_state.page = "materials"
            st.rerun()


# ─────────────────────────────────────────────────────────────
# PAGE 2 — MATERIALS & RFQ
# ─────────────────────────────────────────────────────────────
def materials_page():
    st.markdown("## 📐 Materials & RFQ")

    if not st.session_state.active_project_id:
        st.warning("Please select a project first.")
        if st.button("Go to Projects"):
            st.session_state.page = "projects"
            st.rerun()
        return

    boq_df = load_boq()
    if boq_df is None:
        st.error("BOQ file not found.")
        return

    project_code = str(st.session_state.selected_project_code).strip()
    project_materials = boq_df[boq_df["Project_ID"] == project_code]

    if project_materials.empty:
        st.info("No materials in BOQ for this project.")
        return

    selected_material = st.selectbox("Select Material", project_materials["Material_Name"].unique())
    mat_row = project_materials[project_materials["Material_Name"] == selected_material].iloc[0]

    quantity      = mat_row["BOQ_Quantity"]
    uom           = mat_row["uom"]
    specification = mat_row["Specification"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Quantity", f"{quantity} {uom}")
    col2.metric("Material", selected_material)
    col3.metric("Specification", str(specification)[:50])

    # FIX 3: Past vendor history from fixed Excel — no upload section here
    st.markdown("### 📊 Past Vendor History")
    vendor_df = load_vendor_history()

    if vendor_df is None:
        st.warning("No vendor history file (data/past_vendor_data.xlsx).")
        return

    vendor_df["material_name"] = vendor_df["material_name"].str.strip().str.lower()
    mat_clean = selected_material.strip().lower()
    filtered  = vendor_df[vendor_df["material_name"] == mat_clean].copy()

    if filtered.empty:
        st.info(f"No past vendor history for '{selected_material}'.")
        return

    show_cols = [c for c in [
        "vendor_name", "email", "project_name", "project_id",
        "unit_price", "quantity", "date"
    ] if c in filtered.columns]

    filtered["Select"] = False
    edited = st.data_editor(
        filtered[show_cols + ["Select"]],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    if st.button("📤 Send RFQ to Selected Vendors", use_container_width=True):
        selected_rows = edited[edited["Select"] == True]
        if selected_rows.empty:
            st.warning("Select at least one vendor.")
            return

        conn, cursor = get_cursor()
        try:
            cursor.execute("""
                INSERT INTO rfq_master
                    (project_id, material_name, quantity, uom, specification, rfq_date, status)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, 'Sent')
            """, (
                st.session_state.active_project_id,
                selected_material,
                float(quantity),
                str(uom),
                str(specification),
            ))
            cursor.execute("SELECT lastval() AS rfq_id")
            rfq_id = cursor.fetchone()["rfq_id"]

            for _, row in selected_rows.iterrows():
                vname  = row["vendor_name"]
                vemail = row["email"]
                sent = send_rfq_email(
                    vemail, vname, selected_material,
                    quantity, uom, specification,
                    rfq_id, st.session_state.project_sheet_id
                )
                if sent:
                    st.success(f"✅ RFQ sent to {vname}")
                else:
                    st.error(f"❌ Failed: {vname}")

                cursor.execute("""
                    INSERT INTO vendor_quotes (rfq_id, vendor_name, vendor_email, status)
                    VALUES (%s, %s, %s, 'RFQ Sent')
                """, (rfq_id, vname, vemail))

            conn.commit()
            st.success(f"RFQ-{rfq_id} sent! Go to RFQ Tracking to monitor.")

        except Exception as e:
            conn.rollback()
            st.error("Error:")
            st.exception(e)
        finally:
            conn.close()


# ─────────────────────────────────────────────────────────────
# PAGE 3 — RFQ TRACKING
# ─────────────────────────────────────────────────────────────
def tracking_page():
    st.markdown("## 📊 RFQ Tracking")

    col_t, col_b = st.columns([3, 1])
    with col_b:
        if st.button("📩 Fetch Vendor Replies", use_container_width=True):
            try:
                with st.spinner("Scanning inbox..."):
                    from services.gmail_service import fetch_rfq_replies
                    fetch_rfq_replies()
                st.success("Done.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    conn, cursor = get_cursor()
    cursor.execute("SELECT id, project_id FROM projects ORDER BY id DESC")
    projects = cursor.fetchall()
    if not projects:
        st.info("No projects found.")
        conn.close()
        return

    pdict = {p["project_id"]: p["id"] for p in projects}
    sel   = st.selectbox("Select Project", list(pdict.keys()))
    pid   = pdict[sel]

    cursor.execute("""
        SELECT
            rm.rfq_id          AS "RFQ ID",
            rm.material_name   AS "Material",
            rm.rfq_date        AS "RFQ Date",
            rm.status          AS "RFQ Status",
            rv.vendor_name     AS "Vendor",
            rv.status          AS "Vendor Status",
            rm.approval_status AS "Approval Status"
        FROM rfq_master rm
        LEFT JOIN vendor_quotes rv ON rm.rfq_id = rv.rfq_id
        WHERE rm.project_id = %s
        ORDER BY rm.rfq_id DESC
    """, (pid,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        st.warning("No RFQs found.")
        return

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────
# PAGE 4 — QUOTE COMPARISON
# ─────────────────────────────────────────────────────────────
def comparison_page():
    st.markdown("## ⚖️ Quote Comparison")

    conn, cursor = get_cursor()
    cursor.execute("SELECT id, project_id FROM projects ORDER BY id DESC")
    projects = cursor.fetchall()
    if not projects:
        st.warning("No projects found.")
        conn.close()
        return

    pdict = {p["project_id"]: p["id"] for p in projects}
    sel   = st.selectbox("Select Project", list(pdict.keys()))
    pid   = pdict[sel]

    cursor.execute(
        "SELECT DISTINCT material_name FROM rfq_master WHERE project_id=%s", (pid,)
    )
    mats = cursor.fetchall()
    if not mats:
        st.warning("No materials found.")
        conn.close()
        return

    mat = st.selectbox("Select Material", [m["material_name"] for m in mats])

    cursor.execute("""
        SELECT vq.id, vq.rfq_id, vq.vendor_name, vq.vendor_email,
               vq.unit_price, vq.delivery_time, vq.payment_terms,
               vq.status, vq.round
        FROM vendor_quotes vq
        WHERE vq.rfq_id IN (
            SELECT rfq_id FROM rfq_master
            WHERE project_id=%s AND LOWER(TRIM(material_name))=LOWER(TRIM(%s))
        )
        ORDER BY vq.rfq_id, vq.round DESC
    """, (pid, mat))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        st.warning("No quotes yet. Fetch replies from RFQ Tracking page.")
        return

    df = pd.DataFrame([dict(r) for r in rows])
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    valid = df[df["unit_price"].notna()]
    if not valid.empty:
        best = df.loc[df["unit_price"].idxmin()]
        st.success(f"💰 Lowest: **{best['vendor_name']}** — ₹ {best['unit_price']:,.2f}")

    disp = df[["rfq_id","vendor_name","unit_price","delivery_time","payment_terms","status","round"]].copy()
    disp.columns = ["RFQ ID","Vendor","Unit Price (₹)","Delivery Time","Payment Terms","Status","Round"]
    disp["Select"] = False

    edited = st.data_editor(
        disp,
        use_container_width=True,
        hide_index=True,
        column_config={
            "RFQ ID":         st.column_config.Column(disabled=True),
            "Vendor":         st.column_config.Column(disabled=True),
            "Status":         st.column_config.Column(disabled=True),
            "Round":          st.column_config.Column(disabled=True),
            "Unit Price (₹)": st.column_config.NumberColumn(format="₹%.2f"),
        }
    )

    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Save Edits", use_container_width=True):
            conn, cursor = get_cursor()
            try:
                for i, row in edited.iterrows():
                    cursor.execute("""
                        UPDATE vendor_quotes
                        SET unit_price=%s, delivery_time=%s, payment_terms=%s
                        WHERE id=%s
                    """, (row["Unit Price (₹)"], row["Delivery Time"],
                          row["Payment Terms"], int(df.iloc[i]["id"])))
                conn.commit()
                st.success("Saved.")
            except Exception as e:
                conn.rollback()
                st.exception(e)
            finally:
                conn.close()

    with col2:
        if st.button("📨 Send Reverse RFQ", use_container_width=True):
            sel_rows = edited[edited["Select"] == True]
            if sel_rows.empty:
                st.warning("Select vendors first.")
            else:
                st.session_state.reverse_rfq_vendors = sel_rows.index.tolist()
                st.session_state.reverse_rfq_df      = df
                st.session_state.show_reverse_form   = True
                st.rerun()

    with col3:
        if st.button("📤 Send for Approval", use_container_width=True):
            sel_rows = edited[edited["Select"] == True]
            if sel_rows.empty:
                st.warning("Select vendors first.")
            else:
                conn, cursor = get_cursor()
                try:
                    vendors_data = []
                    for i in sel_rows.index:
                        orig = df.iloc[i]
                        cursor.execute("""
                            SELECT id FROM vendor_approvals
                            WHERE project_id=%s AND material_name=%s
                            AND vendor_name=%s AND status='Pending'
                        """, (pid, mat, orig["vendor_name"]))
                        if cursor.fetchone():
                            st.warning(f"Already pending: {orig['vendor_name']}")
                            continue
                        cursor.execute("""
                            INSERT INTO vendor_approvals
                                (project_id, material_name, vendor_name,
                                 unit_price, delivery_time, payment_terms, status)
                            VALUES (%s,%s,%s,%s,%s,%s,'Pending')
                        """, (pid, mat, orig["vendor_name"],
                              float(orig["unit_price"]) if orig["unit_price"] else None,
                              orig["delivery_time"], orig["payment_terms"]))
                        vendors_data.append({
                            "vendor_name":   orig["vendor_name"],
                            "unit_price":    orig["unit_price"] or 0,
                            "delivery_time": orig["delivery_time"],
                            "payment_terms": orig["payment_terms"],
                        })

                    cursor.execute("""
                        UPDATE rfq_master SET approval_status='Pending'
                        WHERE project_id=%s AND LOWER(TRIM(material_name))=LOWER(TRIM(%s))
                    """, (pid, mat))
                    conn.commit()

                    if vendors_data:
                        send_approval_email(pid, mat, vendors_data)
                        st.success(f"✅ {len(vendors_data)} vendor(s) sent for approval.")
                except Exception as e:
                    conn.rollback()
                    st.exception(e)
                finally:
                    conn.close()

    # Reverse RFQ form
    if st.session_state.show_reverse_form:
        st.markdown("---")
        st.markdown("### 📨 Reverse RFQ — Negotiation")
        comments = st.text_area(
            "Comments to send vendor",
            placeholder="Your price is above target. Please resubmit your best offer.",
            height=120
        )
        ca, cb = st.columns(2)
        with ca:
            if st.button("✉️ Send", use_container_width=True):
                if not comments.strip():
                    st.warning("Add comments first.")
                else:
                    rev_df = st.session_state.reverse_rfq_df
                    conn, cursor = get_cursor()
                    try:
                        for i in st.session_state.reverse_rfq_vendors:
                            orig = rev_df.iloc[i]
                            sent = send_reverse_rfq_email(
                                orig["vendor_email"], orig["vendor_name"],
                                mat, int(orig["rfq_id"]),
                                float(orig["unit_price"] or 0), comments
                            )
                            if sent:
                                st.success(f"✅ {orig['vendor_name']}")
                            else:
                                st.error(f"❌ {orig['vendor_name']}")
                            cursor.execute("""
                                INSERT INTO reverse_rfq (rfq_id, vendor_name, vendor_email, comments)
                                VALUES (%s,%s,%s,%s)
                            """, (int(orig["rfq_id"]), orig["vendor_name"],
                                  orig["vendor_email"], comments))
                        conn.commit()
                        st.session_state.show_reverse_form = False
                    except Exception as e:
                        conn.rollback()
                        st.exception(e)
                    finally:
                        conn.close()
        with cb:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_reverse_form = False
                st.rerun()


# ─────────────────────────────────────────────────────────────
# PAGE 5 — MANAGER APPROVAL
# ─────────────────────────────────────────────────────────────
def approval_page():
    st.markdown("## 🧾 Manager Approval")

    conn, cursor = get_cursor()
    cursor.execute("""
        SELECT id, project_id, material_name, vendor_name,
               unit_price, delivery_time, payment_terms
        FROM vendor_approvals WHERE status='Pending' ORDER BY id DESC
    """)
    approvals = cursor.fetchall()
    conn.close()

    if not approvals:
        st.success("No pending approvals.")
        return

    for row in approvals:
        with st.expander(
            f"📦 Project {row['project_id']} | {row['material_name']} | {row['vendor_name']}",
            expanded=True
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Submitted Quote**")
                st.write(f"**Vendor:** {row['vendor_name']}")
                st.write(f"**Unit Price:** ₹ {row['unit_price']:,.2f}" if row['unit_price'] else "N/A")
                st.write(f"**Delivery:** {row['delivery_time'] or 'N/A'}")
                st.write(f"**Payment:** {row['payment_terms'] or 'N/A'}")

            with col2:
                st.markdown("**Historical Prices — same material**")
                hist_df = load_vendor_history()
                if hist_df is not None:
                    hist_df["Material_Name"] = hist_df["Material_Name"].str.strip().str.lower()
                    hist = hist_df[hist_df["Material_Name"] == str(row["material_name"]).strip().lower()]
                    if not hist.empty:
                        show_cols = [c for c in ["Vendor_Name","Project_Name","Unit_Price","Date"]
                                     if c in hist.columns]
                        st.dataframe(hist[show_cols], use_container_width=True, hide_index=True)
                    else:
                        st.info("No historical data for this material.")
                else:
                    st.info("No vendor history file.")

            st.markdown("---")
            b1, b2 = st.columns(2)

            with b1:
                if st.button("✅ Approve", key=f"approve_{row['id']}", use_container_width=True):
                    conn2, cursor2 = get_cursor()
                    try:
                        cursor2.execute(
                            "UPDATE vendor_approvals SET status='Approved' WHERE id=%s",
                            (row["id"],)
                        )
                        cursor2.execute("""
                            UPDATE rfq_master
                            SET status='Vendor Approved', approval_status='Approved'
                            WHERE project_id=%s AND LOWER(TRIM(material_name))=LOWER(TRIM(%s))
                        """, (row["project_id"], row["material_name"]))
                        conn2.commit()

                        # FIX 3: auto-add to vendor history
                        _add_to_history(row)
                        st.success("Approved and added to vendor history!")
                        st.rerun()
                    except Exception as e:
                        conn2.rollback()
                        st.exception(e)
                    finally:
                        conn2.close()

            with b2:
                if st.button("❌ Reject", key=f"reject_{row['id']}", use_container_width=True):
                    conn2, cursor2 = get_cursor()
                    cursor2.execute("UPDATE vendor_approvals SET status='Rejected' WHERE id=%s", (row["id"],))
                    cursor2.execute("""
                        UPDATE rfq_master SET status='Vendor Rejected', approval_status='Rejected'
                        WHERE project_id=%s AND LOWER(TRIM(material_name))=LOWER(TRIM(%s))
                    """, (row["project_id"], row["material_name"]))
                    conn2.commit()
                    conn2.close()
                    st.success("Rejected.")
                    st.rerun()


def _add_to_history(row):
    conn, cursor = get_cursor()
    try:
        cursor.execute("""
            SELECT vq.vendor_email, vq.quantity
            FROM vendor_quotes vq
            JOIN rfq_master rm ON vq.rfq_id = rm.rfq_id
            WHERE rm.project_id=%s AND LOWER(TRIM(rm.material_name))=LOWER(TRIM(%s))
            AND LOWER(vq.vendor_name)=LOWER(%s)
            ORDER BY vq.id DESC LIMIT 1
        """, (row["project_id"], row["material_name"], row["vendor_name"]))
        vrow = cursor.fetchone()

        cursor.execute("SELECT project_id FROM projects WHERE id=%s", (row["project_id"],))
        proj = cursor.fetchone()
        project_name = proj["project_id"] if proj else str(row["project_id"])
    finally:
        conn.close()

    new_row = {
        "Vendor_Name":   row["vendor_name"],
        "Email":         vrow["vendor_email"] if vrow else "",
        "Material_Name": row["material_name"],
        "Project_Name":  project_name,
        "Project_ID":    row["project_id"],
        "Unit_Price":    row["unit_price"],
        "Quantity":      vrow["quantity"] if vrow else "",
        "Date":          pd.Timestamp.now().strftime("%Y-%m-%d"),
        "Delivery_Time": row["delivery_time"],
        "Payment_Terms": row["payment_terms"],
    }
    append_to_vendor_history([new_row])


# ─────────────────────────────────────────────────────────────
# PAGE 6 — COSTING
# ─────────────────────────────────────────────────────────────
def costing_page():
    st.markdown("## 💰 Project Costing")

    conn, cursor = get_cursor()
    cursor.execute("SELECT id, project_id FROM projects ORDER BY id DESC")
    projects = cursor.fetchall()
    if not projects:
        st.warning("No projects found.")
        conn.close()
        return

    pdict = {p["project_id"]: p["id"] for p in projects}
    sel   = st.selectbox("Select Project", list(pdict.keys()))
    pid   = pdict[sel]

    cursor.execute("""
        SELECT rm.material_name, rm.quantity, rm.uom, va.vendor_name, va.unit_price
        FROM vendor_approvals va
        JOIN rfq_master rm
            ON rm.project_id = va.project_id
            AND LOWER(TRIM(rm.material_name)) = LOWER(TRIM(va.material_name))
        WHERE va.project_id=%s AND va.status='Approved'
        ORDER BY rm.material_name
    """, (pid,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        st.warning("No approved vendors yet.")
        return

    df = pd.DataFrame([dict(r) for r in rows])
    df.columns = ["Material", "Quantity", "UOM", "Vendor", "Unit Price"]
    df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce")
    df["Quantity"]   = pd.to_numeric(df["Quantity"],   errors="coerce")
    df["Total Cost"] = df["Quantity"] * df["Unit Price"]

    st.dataframe(
        df.style.format({"Unit Price": "₹{:,.2f}", "Total Cost": "₹{:,.2f}"}),
        use_container_width=True
    )
    st.markdown("---")
    st.success(f"💰 Total Project Cost: ₹ {df['Total Cost'].sum():,.2f}")


# ─────────────────────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────────────────────
def main():
    section = st.session_state.section

    if section is None:
        landing_page()
        return

    if section == "design":
        if not st.session_state.design_logged_in:
            design_login_page()
        else:
            design_section()
        return

    if section == "procurement":
        if not st.session_state.logged_in:
            procurement_login_page()
            return
        procurement_nav()
        page = st.session_state.page
        if page == "projects":
            projects_page()
        elif page == "materials":
            materials_page()
        elif page == "tracking":
            tracking_page()
        elif page == "comparison":
            comparison_page()
        elif page == "approval":
            approval_page()
        elif page == "costing":
            costing_page()
        else:
            projects_page()


main()