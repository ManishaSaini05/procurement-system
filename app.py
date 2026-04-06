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

import streamlit as st
import pandas as pd
import uuid
from pathlib import Path
#from services.db import get_connection
from services.db import get_connection, get_cursor
from services.email_service import send_rfq_email
from services.email_service import send_approval_email
query_params = st.query_params
page = query_params.get("page")

st.set_page_config(page_title="Procurement System", layout="wide")


# =========================
# SESSION INIT
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "active_project_id" not in st.session_state:
    st.session_state.active_project_id = None

# =========================
# LOAD FILES
# =========================

@st.cache_data
def load_boq():
    path = Path("data/Design_boq.xlsx")

    if not path.exists():
        return None

    return pd.read_excel(path)


@st.cache_data
def load_vendor_data():
    path = Path("data/past_vendor_data.xlsx")

    if not path.exists():
        return None

    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()

    return df


# =========================
# LOGIN PAGE
# =========================

def login_page():

    st.title("🔐 Procurement Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        # conn = get_connection()
        # cursor = conn.cursor()
        conn, cursor = get_cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:

            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()

        else:

            st.error("Invalid credentials")


# =========================
# PROJECT SECTION
# =========================

def project_section():

    st.subheader("📂 Select Project from Design BOQ")

    boq_df = load_boq()

    if boq_df is None:
        st.error("BOQ file not found.")
        return

    unique_projects = boq_df["Project_ID"].dropna().unique()

    selected_project_code = st.selectbox(
        "Select Project ID",
        unique_projects
        
    )
    #st.session_state.project_sheet_id = selected_project_code
    st.session_state["selected_project_code"] = selected_project_code
    if selected_project_code:

        # conn = get_connection()
        # cursor = conn.cursor()
        conn, cursor = get_cursor()

        cursor.execute(
            "SELECT * FROM projects WHERE project_id=%s",
            (selected_project_code,)
        )

        existing = cursor.fetchone()

        if not existing:

            cursor.execute(
                """
                INSERT INTO projects
                (project_id, project_name)
                VALUES (%s, %s)
                """,
                (selected_project_code, selected_project_code)
            )

            conn.commit()

        cursor.execute(
            "SELECT id FROM projects WHERE project_id=%s",
            (selected_project_code,)
        )

        project_id = cursor.fetchone()["id"]

        conn.close()

        st.session_state.active_project_id = project_id
        st.session_state.project_sheet_id = selected_project_code

        st.success(f"Project {selected_project_code} Ready for Procurement")


# =========================
# MATERIAL SECTION
# =========================

def material_section():
    selected_project_code = st.session_state.get("selected_project_code")
    if not st.session_state.active_project_id:

        st.warning("Please select project first.")
        return

    st.subheader("📐 Materials From BOQ")

    boq_df = load_boq()

    project_materials = boq_df[
        boq_df["Project_ID"] == selected_project_code
    ]

    if project_materials.empty:

        st.info("No materials found for this project.")
        return

    material_names = project_materials["Material_Name"].unique()

    selected_material = st.selectbox(
        "Select Material",
        material_names
    )

    if not selected_material:
        return

    material_row = project_materials[
        project_materials["Material_Name"] == selected_material
    ]

    material_row = material_row.iloc[0]
    quantity = material_row["BOQ_Quantity"]
    uom = material_row["uom"]
    specification = material_row["Specification"]
    
    
    st.markdown("### Material Details")

    st.write(f"**Material:** {selected_material}")
    st.write(f"**Quantity:** {quantity}")
    st.write(f"**Specification:** {specification}")

    st.markdown("### 📊 Past Vendor History")

    vendor_df = load_vendor_data()
    vendor_df.columns = vendor_df.columns.str.strip()

    if vendor_df is None:

        st.warning("Past vendor data file not found.")
        return

    vendor_df["Material_Name"] = vendor_df["Material_Name"].str.strip().str.lower()

    selected_material_clean = selected_material.strip().lower()

    filtered_vendors = vendor_df[
        vendor_df["Material_Name"] == selected_material_clean
    ]

    if filtered_vendors.empty:

        st.warning("No past vendor history found.")
        return

    filtered_vendors = filtered_vendors.copy()
    filtered_vendors["Select"] = False

    edited_df = st.data_editor(
        filtered_vendors,
        use_container_width=True
    )

    # =========================
    # SEND RFQ
    # =========================

    if st.button("Send RFQ"):

        selected_rows = edited_df[edited_df["Select"] == True]

        if selected_rows.empty:

            st.warning("Select at least one vendor.")
            return

        # conn = get_connection()
        # cursor = conn.cursor()
        conn, cursor = get_cursor()

        # rfq_token = str(uuid.uuid4())[:8]

        # cursor.execute(
        #     """
        #     INSERT INTO rfq_master
        #     (project_id, material_name, rfq_date, status)
        #     VALUES (%s, %s, CURRENT_TIMESTAMP, %s)
        #     """,
        #     (
        #         st.session_state.active_project_id,
        #         selected_material,
        #         "sent"
        #     )
        # )

        # rfq_id = cursor.lastrowid
        cursor.execute(
           """
            INSERT INTO rfq_master
            (project_id, material_name, rfq_date, status)
            VALUES (%s, %s, CURRENT_TIMESTAMP, %s)
            RETURNING rfq_id
            """,
            (
                st.session_state.active_project_id,
                selected_material,
                "sent"
            )
        )

        rfq_id = cursor.fetchone()["rfq_id"]

        # SEND EMAILS

        for _, row in selected_rows.iterrows():

            vendor_name = row["Vendor_Name"]
            vendor_email = row["Email"]

            email_sent = send_rfq_email(
                vendor_email,
                vendor_name,
                selected_material,
                quantity, 
                uom,
                specification,
                rfq_id,
                st.session_state.project_sheet_id
            )

            if email_sent:

                st.success(f"RFQ sent to {vendor_name}")

            else:

                st.error(f"Failed to send email to {vendor_name}")

            cursor.execute(
                """
                INSERT INTO vendor_quotes
                (rfq_id, vendor_name, vendor_email, status)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    rfq_id,
                    vendor_name,
                    vendor_email,
                    "RFQ Sent"
                )
            )

        conn.commit()
        conn.close()

        st.success("RFQ process completed.")


# =========================
# RFQ TRACKING
# =========================

def rfq_tracking_section():

    st.title("📊 RFQ Tracking")

    # Fetch vendor replies button
    #if st.button("📩 Fetch Vendor Replies"):
        #with st.spinner("Reading vendor emails..."):
            #from services.gmail_service import fetch_rfq_replies
            #fetch_rfq_replies()
        #st.success("Vendor replies processed successfully")
    if st.button("📩 Fetch Vendor Replies"):
        try:
            with st.spinner("Reading vendor emails..."):
                from services.gmail_service import fetch_rfq_replies
                fetch_rfq_replies()
            st.success("Vendor replies processed successfully")
        except Exception as e:
            st.error("REAL ERROR:")
            st.write(e)
    # conn = get_connection()
    # cursor = conn.cursor()
    conn, cursor = get_cursor()

    cursor.execute("SELECT id, project_id FROM projects")
    projects = cursor.fetchall()

    if not projects:
        st.info("No projects found.")
        conn.close()
        return

    project_dict = {p["project_id"]: p["id"] for p in projects}

    selected_project = st.selectbox(
        "Select Project",
        list(project_dict.keys())
    )

    selected_project_id = project_dict[selected_project]

    #cursor.execute(
         #"""
    #     SELECT
    #         rm.rfq_id,
    #         rm.material_name,
    #         rm.status,
    #         rv.vendor_name,
    #         rv.status
    #     FROM rfq_master rm
    #     LEFT JOIN vendor_quotes rv ON rm.rfq_id = rv.rfq_id
    #     WHERE rm.project_id = %s
    #     ORDER BY rm.rfq_id DESC
    #     """,
    #     (selected_project_id,)
    #)
    cursor.execute("""
        SELECT
            rm.rfq_id AS "RFQ ID",
            rm.material_name AS "Material",
            rm.status AS "RFQ Status",
            rv.vendor_name AS "Vendor",
            rv.status AS "Vendor Status"
        FROM rfq_master rm
        LEFT JOIN vendor_quotes rv ON rm.rfq_id = rv.rfq_id
        WHERE rm.project_id = %s
        ORDER BY rm.rfq_id DESC
        """, (selected_project_id,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        st.warning("No RFQs found.")
        return

    df = pd.DataFrame(rows)

    # df.columns = [
    #     "RFQ ID",
    #     "Material",
    #     "RFQ Status",
    #     "Vendor",
    #     "Vendor Status"
    # ]

    # st.dataframe(df, use_container_width=True)
    #rows = cursor.fetchall()
    #df = pd.DataFrame(rows)

    st.dataframe(df, use_container_width=True)

# def comparison_section():

#     st.title("📊 Vendor Quote Comparison")

#     # conn = get_connection()
#     # cursor = conn.cursor()
#     conn, cursor = get_cursor()

#     # =========================
#     # Select Project
#     # =========================
#     cursor.execute("SELECT id, project_id FROM projects ORDER BY id DESC")
#     projects = cursor.fetchall()

#     if not projects:
#         st.warning("No projects found.")
#         conn.close()
#         return

#     project_dict = {p["project_id"]: p["id"] for p in projects}
#     selected_project = st.selectbox("Select Project", list(project_dict.keys()))
#     selected_project_id = project_dict[selected_project]

#     # =========================
#     # Select Material
#     # =========================
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

#     # cursor.execute("""
#     # SELECT rfq_id, vendor_name, unit_price, delivery_time, payment_terms
#     # FROM vendor_quotes
#     # ORDER BY rfq_id DESC
#     # """)
#     cursor.execute("""
#     SELECT rfq_id, vendor_name, unit_price, delivery_time, payment_terms
#     FROM vendor_quotes
#     WHERE rfq_id IN (
#         SELECT rfq_id FROM rfq_master
#         WHERE project_id = %s AND LOWER(TRIM(material_name)) = LOWER(TRIM(%s))
#     )
#     """, (selected_project_id, selected_material))
    
#     #print("ROWS FROM DB:", rows)
    
#     rows = cursor.fetchall()
#     # df = pd.DataFrame([dict(r) for r in rows])
#     if not rows:
#         st.warning("No quotes found.")
#     return

#     df = pd.DataFrame([dict(r) for r in rows])
#     # =========================
#     # Rename columns for display
#     # =========================
#     df.columns = ["RFQ ID","Vendor", "Unit Price", "Delivery Time", "Payment Terms"]

#     # Add selection column
#     df["Select Vendor"] = False
    
#     df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce")

#     df["Delivery Time"] = df["Delivery Time"].astype(str)
#     df["Payment Terms"] = df["Payment Terms"].astype(str)

#     edited_df = st.data_editor(
#         df,
#         use_container_width=True,
#         num_rows="fixed"
#     )
#     column_config={
#         "RFQ ID": st.column_config.Column(disabled=True),
#         "Vendor": st.column_config.Column(disabled=True),
#         "Unit Price": st.column_config.NumberColumn(),
#         "Delivery Time": st.column_config.TextColumn(),
#         "Payment Terms": st.column_config.TextColumn()
#     },
  
#     if st.button("💾 Save Edited Quotes"):

#         # conn = get_connection()
#         # cursor = conn.cursor()
#         conn, cursor = get_cursor()

#         for _, row in edited_df.iterrows():

#             cursor.execute("""
#             UPDATE vendor_quotes
#             SET
#                 unit_price = %s,
#                 delivery_time = %s,
#                 payment_terms = %s
#             WHERE rfq_id = %s
#             """, (
#                 row["Unit Price"],
#                 row["Delivery Time"],
#                 row["Payment Terms"],
#                 row["RFQ ID"]
#             ))

#         conn.commit()
#         conn.close()

#         st.success("Quotes updated successfully")
#     # Get selected vendor
#     selected_vendor = edited_df[edited_df["Select Vendor"] == True]


#     # =========================
#     # Highlight best price
#     # =========================
#     try:
#         df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce")
#         best_vendor = df.loc[df["Unit Price"].idxmin()]
#         st.success(f"💰 Lowest Quote: {best_vendor['Vendor']} ({best_vendor['Unit Price']})")
#     except:
#         pass
    
#     if st.button("📤 Send Selected Vendor for Approval"):

#         if selected_vendor.empty:
#             st.warning("Please select a vendor first.")
#             return


#         vendor_row = selected_vendor.iloc[0]

#         # conn = get_connection()
#         # cursor = conn.cursor()
#         conn, cursor = get_cursor()

#         # Check if approval already exists
#         cursor.execute("""
#         SELECT * FROM vendor_approvals
#         WHERE project_id=%s AND material_name=%s AND vendor_name=%s AND status='Pending'
#         """, (
#         selected_project_id,
#         selected_material,
#         vendor_row["Vendor"]
#         ))

#         existing = cursor.fetchone()

#         if existing:
#             st.warning("Approval request already sent for this vendor.")
#         else:
#             cursor.execute("""
#             INSERT INTO vendor_approvals
#             (project_id, material_name, vendor_name, unit_price, delivery_time, payment_terms, status)
#             VALUES (%s, %s, %s, %s, %s, %s, %s)
#             """, (
#             selected_project_id,
#             selected_material,
#             vendor_row["Vendor"],
#             vendor_row["Unit Price"],
#             vendor_row["Delivery Time"],
#             vendor_row["Payment Terms"],
#             "Pending"
#             ))

#             conn.commit()
#             st.success("Vendor sent to manager for approval.")

#         cursor.execute("""
#         UPDATE rfq_master
#         SET approval_status='Pending'
#         WHERE project_id=%s AND material_name=%s
#         """, (selected_project_id, selected_material))

#         conn.commit()
#         conn.close()

#         st.success("Vendor sent to manager for approval.")
#         send_approval_email(
#             selected_project_id,
#             selected_material,
#             vendor_row["Vendor"],
#              vendor_row["Unit Price"]
#         )
def comparison_section():

    st.title("📊 Vendor Quote Comparison")

    conn, cursor = get_cursor()

    cursor.execute("SELECT id, project_id FROM projects ORDER BY id DESC")
    projects = cursor.fetchall()

    if not projects:
        st.warning("No projects found.")
        conn.close()
        return

    project_dict = {p["project_id"]: p["id"] for p in projects}
    selected_project = st.selectbox("Select Project", list(project_dict.keys()))
    selected_project_id = project_dict[selected_project]

    cursor.execute(
        "SELECT DISTINCT material_name FROM rfq_master WHERE project_id=%s",
        (selected_project_id,)
    )

    materials = cursor.fetchall()

    if not materials:
        st.warning("No materials found.")
        conn.close()
        return

    material_list = [m["material_name"] for m in materials]
    selected_material = st.selectbox("Select Material", material_list)

    cursor.execute("""
        SELECT rfq_id, vendor_name, unit_price, delivery_time, payment_terms
        FROM vendor_quotes
        WHERE rfq_id IN (
            SELECT rfq_id FROM rfq_master
            WHERE project_id = %s 
            AND LOWER(TRIM(material_name)) = LOWER(TRIM(%s))
        )
    """, (selected_project_id, selected_material))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        st.warning("No quotes found.")
        return

    df = pd.DataFrame([dict(r) for r in rows])

    df.columns = ["RFQ ID","Vendor", "Unit Price", "Delivery Time", "Payment Terms"]

    df["Select Vendor"] = False

    df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce")

    edited_df = st.data_editor(df, use_container_width=True)

    if st.button("💾 Save Edited Quotes"):

        conn, cursor = get_cursor()

        for _, row in edited_df.iterrows():

            cursor.execute("""
                UPDATE vendor_quotes
                SET
                    unit_price = %s,
                    delivery_time = %s,
                    payment_terms = %s
                WHERE rfq_id = %s
            """, (
                row["Unit Price"],
                row["Delivery Time"],
                row["Payment Terms"],
                row["RFQ ID"]
            ))

        conn.commit()
        conn.close()

        st.success("Quotes updated successfully")

    selected_vendor = edited_df[edited_df["Select Vendor"] == True]

    try:
        best_vendor = df.loc[df["Unit Price"].idxmin()]
        st.success(f"💰 Lowest Quote: {best_vendor['Vendor']} ({best_vendor['Unit Price']})")
    except:
        pass
def manager_approval_section():

    st.title("🧾 Manager Vendor Approvals")

    # conn = get_connection()
    # cursor = conn.cursor()
    conn, cursor = get_cursor()

    cursor.execute("""
    SELECT id, project_id, material_name, vendor_name, unit_price, delivery_time, payment_terms
    FROM vendor_approvals
    WHERE status='Pending'
    """)

    approvals = cursor.fetchall()

    if not approvals:
        st.info("No approvals pending.")
        conn.close()
        return

    for row in approvals:

        st.subheader(f"Project: {row['project_id']} | Material: {row['material_name']}")

        st.write(f"Vendor: {row['vendor_name']}")
        st.write(f"Unit Price: {row['unit_price']}")
        st.write(f"Delivery: {row['delivery_time']}")
        st.write(f"Payment Terms: {row['payment_terms']}")

        col1, col2 = st.columns(2)

        with col1:
           
            if st.button(f"✅ Approve {row['id']}"):

                cursor.execute("""
                UPDATE vendor_approvals
                SET status='Approved'
                WHERE id=%s
                """, (row['id'],))

                cursor.execute("""
                UPDATE rfq_master
                SET
                    status='Vendor Approved'
                WHERE project_id=%s AND material_name=%s
                """, (row['project_id'], row['material_name']))

                conn.commit()
                st.success("Vendor Approved")

        with col2:
            
            if st.button(f"❌ Reject {row['id']}"):

                cursor.execute("""
                UPDATE vendor_approvals
                SET status='Rejected'
                WHERE id=%s
                """, (row['id'],))

                cursor.execute("""
                UPDATE rfq_master
                SET status='Vendor Rejected'
                WHERE project_id=%s AND material_name=%s
                """, (row['project_id'], row['material_name']))

                conn.commit()
                st.success("Vendor Rejected")

    conn.close()
def costing_section():

    st.title("💰 Project Costing")

    # conn = get_connection()
    # cursor = conn.cursor()
    conn, cursor = get_cursor()

    # Select Project
    cursor.execute("SELECT id, project_id FROM projects")
    projects = cursor.fetchall()

    if not projects:
        st.warning("No projects found.")
        conn.close()
        return

    project_dict = {p["project_id"]: p["id"] for p in projects}

    selected_project = st.selectbox("Select Project", list(project_dict.keys()))
    selected_project_id = project_dict[selected_project]
    st.write("Selected Project ID:", selected_project_id)

    # Fetch Approved Vendors + RFQ Data
    cursor.execute("""
    SELECT 
        rm.material_name,
        rm.quantity,
        rm.uom,
        va.vendor_name,
        va.unit_price
    FROM vendor_approvals va
    JOIN rfq_master rm 
        ON rm.project_id = va.project_id 
        AND LOWER(TRIM(rm.material_name)) = LOWER(TRIM(va.material_name))
    WHERE va.project_id=%s 
    AND va.status='Approved'
    """, (selected_project_id,))

    rows = cursor.fetchall()

    if not rows:
        st.warning("No approved vendors found.")
        conn.close()
        return

    df = pd.DataFrame([dict(r) for r in rows])

    # Calculate Total Cost per Material
    df["Total Cost"] = df["quantity"] * df["unit_price"]

    # Rename for UI
    df.columns = [
        "Material",
        "Quantity",
        "UOM",
        "Vendor",
        "Unit Price",
        "Total Cost"
    ]

    st.subheader("📊 Material-wise Costing")
    st.dataframe(df, use_container_width=True)

    # Total Project Cost
    total_project_cost = df["Total Cost"].sum()

    st.markdown("---")
    st.success(f"💰 Total Project Cost: ₹ {total_project_cost:,.2f}")

    conn.close()
# =========================
# DASHBOARD
# =========================

def dashboard():

    menu = st.sidebar.radio(
        "Navigation",
        ["Projects", "Materials", "RFQ Tracking", "Quote Comparison", "Manager Approval","Costing"]
    )

    if menu == "Projects":
        project_section()

    elif menu == "Materials":
        material_section()

    elif menu == "RFQ Tracking":
        rfq_tracking_section()
    
    elif menu == "Quote Comparison":
        comparison_section()
    
    elif menu == "Manager Approval":
        manager_approval_section()
    
    elif menu == "Costing":
        costing_section()

# =========================
# APP FLOW
# =========================

if not st.session_state.logged_in:

    login_page()

else:

    dashboard()
