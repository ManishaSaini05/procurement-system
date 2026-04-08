# import smtplib
# from email.mime.text import MIMEText

# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 465

# SENDER_EMAIL = "manisha.s@fractalenergy.in"
# SENDER_PASSWORD = "ohji ygoi uuju qesr"


# def send_rfq_email(vendor_email, vendor_name, material_name, quantity, uom, specification,rfq_id, project_id):

#     subject = f"RFQ-{rfq_id} | {project_id} | {material_name}"

# #     body = f"""
# # Dear {vendor_name},

# # We request your quotation for the following material.

# # Material: {material_name}
# # Project: {project_id}

# # Unit Price - 
# # Delivery - 
# # Payment Terms - 

# # Please reply to this email with your quotation.

# # RFQ Reference: {rfq_id}
# # RFQ TOKEN: {rfq_token}

# # Regards
# # Procurement Team
# # """
#     body = f"""
# <p>Dear {vendor_name},</p>

# <p>We request your quotation for the following material requirement.</p>

# <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;">
# <tr style="background-color:#f2f2f2;">
# <th>Material</th>
# <th>Quantity</th>
# <th>UOM</th>
# <th>Specification</th>
# </tr>

# <tr>
# <td>{material_name}</td>
# <td>{quantity}</td>
# <td>{uom}</td>
# <td>{specification}</td>


# </tr>

# </table>

# <br>

# <p>Please provide the following details in your quotation:</p>

# <ul>
# <li>Unit Price</li>
# <li>Delivery Time</li>
# <li>Payment Terms</li>
# </ul>

# <p>Please reply to this email with your quotation.</p>
# """

#     msg = MIMEText(body,"html")
#     msg["Subject"] = subject
#     msg["From"] = SENDER_EMAIL
#     msg["To"] = vendor_email

#     try:
#         server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
#         server.login(SENDER_EMAIL, SENDER_PASSWORD)
#         server.sendmail(SENDER_EMAIL, vendor_email, msg.as_string())
#         server.quit()

#         print("Email sent to:", vendor_email)

#         return True

#     except Exception as e:
#         print("Email error:", e)
#         return False


# MANAGER_EMAIL = "manisha.s@fractalenergy.in"


# # def send_comparison_email(project, material, df):

# #     table_html = df.to_html(index=False)

# #     subject = f"Vendor Comparison Approval - {project} - {material}"

# #     body = f"""
# #     <h3>Vendor Quote Comparison</h3>
# #     <p><b>Project:</b> {project}</p>
# #     <p><b>Material:</b> {material}</p>
# #     {table_html}
# #     <p>Please review and approve the vendor.</p>
# #     """

# #     msg = MIMEText(body, "html")
# #     msg["Subject"] = subject
# #     msg["From"] = "your_email@gmail.com"
# #     msg["To"] = MANAGER_EMAIL

# #     # server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
# #     # server.login("your_email@gmail.com", "your_app_password")
# #     server.sendmail(msg["From"], [msg["To"]], msg.as_string())
# #     server.quit()
# APP_URL = "http://localhost:8501/?page=approval"

# def send_approval_email(project, material, vendor, unit_price):

#     body = f"""
#     <p>Vendors have sent the quotations, please review and provide approval.</p>

#     <p>
#     <a href="{APP_URL}"
#        style="padding:10px 16px;background-color:#2e7d32;color:white;text-decoration:none;border-radius:6px;">
#        Open Approval Page
#     </a>
#     </p>
#     """

#     msg = MIMEText(body, "html")
#     msg["Subject"] = "Vendor Approval Required"
#     msg["From"] = SENDER_EMAIL
#     msg["To"] = MANAGER_EMAIL

#     server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
#     server.login(SENDER_EMAIL, SENDER_PASSWORD)
#     server.sendmail(msg["From"], [msg["To"]], msg.as_string())
#     server.quit()

# import smtplib
# import streamlit as st
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# # =====================================
# # EMAIL CONFIG — pulled from st.secrets
# # Add these keys to your .streamlit/secrets.toml:
# #   SENDER_EMAIL = "you@gmail.com"
# #   SENDER_PASSWORD = "your_app_password"
# #   MANAGER_EMAIL = "manager@company.com"
# # =====================================

# APP_URL = "http://localhost:8501/?page=approval"


# def _get_email_config():
#     return (
#         st.secrets["SENDER_EMAIL"],
#         st.secrets["APP_PASSWORD"],
#         st.secrets["MANAGER_EMAIL"],
#     )


# # =====================================
# # SEND RFQ EMAIL TO VENDOR
# # =====================================

# def send_rfq_email(vendor_email, vendor_name, material, quantity, uom, specification, rfq_id, project_id):

#     SENDER_EMAIL, APP_PASSWORD, _ = _get_email_config()

#     try:
#         body = f"""
#         <p>Dear {vendor_name},</p>

#         <p>We request your quotation for the following material:</p>

#         <table border="1" cellpadding="6" cellspacing="0">
#             <tr><th>Project</th><td>{project_id}</td></tr>
#             <tr><th>Material</th><td>{material}</td></tr>
#             <tr><th>Quantity</th><td>{quantity} {uom}</td></tr>
#             <tr><th>Specification</th><td>{specification}</td></tr>
#             <tr><th>RFQ Reference</th><td>RFQ-{rfq_id}</td></tr>
#         </table>

#         <p>Please reply to this email with your best price, delivery timeline, and payment terms.</p>
#         <p>Use subject line: <strong>RFQ-{rfq_id}</strong> in your reply.</p>

#         <p>Regards,<br>Procurement Team</p>
#         """

#         msg = MIMEMultipart("alternative")
#         msg["Subject"] = f"Request for Quotation - RFQ-{rfq_id} - {material}"
#         msg["From"] = SENDER_EMAIL
#         msg["To"] = vendor_email
#         msg.attach(MIMEText(body, "html"))

#         with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#             server.login(SENDER_EMAIL, APP_PASSWORD)
#             server.sendmail(SENDER_EMAIL, [vendor_email], msg.as_string())

#         return True

#     except Exception as e:
#         print(f"Failed to send RFQ email to {vendor_email}: {e}")
#         return False


# # =====================================
# # SEND APPROVAL EMAIL TO MANAGER
# # =====================================

# def send_approval_email(project_id, material, vendor, unit_price):

#     SENDER_EMAIL, APP_PASSWORD, MANAGER_EMAIL = _get_email_config()

#     try:
#         body = f"""
#         <p>A vendor quote requires your approval.</p>

#         <table border="1" cellpadding="6" cellspacing="0">
#             <tr><th>Project</th><td>{project_id}</td></tr>
#             <tr><th>Material</th><td>{material}</td></tr>
#             <tr><th>Recommended Vendor</th><td>{vendor}</td></tr>
#             <tr><th>Unit Price</th><td>₹ {unit_price}</td></tr>
#         </table>

#         <p>
#         <a href="{APP_URL}"
#            style="padding:10px 16px;background-color:#2e7d32;color:white;
#                   text-decoration:none;border-radius:6px;">
#            Open Approval Page
#         </a>
#         </p>
#         """

#         msg = MIMEMultipart("alternative")
#         msg["Subject"] = f"Vendor Approval Required — {material} ({project_id})"
#         msg["From"] = SENDER_EMAIL
#         msg["To"] = MANAGER_EMAIL
#         msg.attach(MIMEText(body, "html"))

#         with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#             server.login(SENDER_EMAIL, APP_PASSWORD)
#             server.sendmail(SENDER_EMAIL, [MANAGER_EMAIL], msg.as_string())

#         return True

#     except Exception as e:
#         print(f"Failed to send approval email: {e}")
#         return False

# New version #

import smtplib
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

APP_URL = "https://procurement-system-fractal-energy.streamlit.app/"  # CHANGE THIS to your Streamlit app URL


def _cfg():
    return (
        st.secrets["SENDER_EMAIL"],
        st.secrets["SENDER_PASSWORD"],
        st.secrets["MANAGER_EMAIL"],
    )


def _send(to_email, subject, body_html):
    sender, password, _ = _cfg()
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = sender
        msg["To"]      = to_email
        msg.attach(MIMEText(body_html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(sender, password)
            s.sendmail(sender, [to_email], msg.as_string())
        return True
    except Exception as e:
        print(f"Email send failed to {to_email}: {e}")
        return False


# ── RFQ to vendor ──────────────────────────────────────────
def send_rfq_email(vendor_email, vendor_name, material,
                   quantity, uom, specification, rfq_id, project_id):
    body = f"""
    <p>Dear {vendor_name},</p>
    <p>We request your best quotation for the following material:</p>
    <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse">
      <tr><th>Project</th><td>{project_id}</td></tr>
      <tr><th>Material</th><td>{material}</td></tr>
      <tr><th>Quantity</th><td>{quantity} {uom}</td></tr>
      <tr><th>Specification</th><td>{specification}</td></tr>
      <tr><th>RFQ Reference</th><td><b>RFQ-{rfq_id}</b></td></tr>
    </table>
    <p>Please reply with your unit price, delivery timeline, and payment terms.<br>
    Use <b>RFQ-{rfq_id}</b> in your reply subject line.</p>
    <p>Regards,<br>Procurement Team</p>
    """
    return _send(vendor_email, f"Request for Quotation — RFQ-{rfq_id} — {material}", body)


# ── Reverse RFQ (negotiation) ──────────────────────────────
def send_reverse_rfq_email(vendor_email, vendor_name, material,
                            rfq_id, current_price, comments):
    body = f"""
    <p>Dear {vendor_name},</p>
    <p>Thank you for your quotation for <b>{material}</b> (RFQ-{rfq_id}).</p>
    <p>Your quoted price of <b>₹ {current_price:,.2f}</b> is currently above our target.</p>
    <p><b>Our comments / requirements:</b><br>{comments}</p>
    <p>We request you to review and resubmit your best competitive price.<br>
    Please reply using subject line: <b>RFQ-{rfq_id}</b></p>
    <p>Regards,<br>Procurement Team</p>
    """
    return _send(vendor_email, f"Re: RFQ-{rfq_id} — Revised Quote Request — {material}", body)


# ── Approval email to manager ──────────────────────────────
def send_approval_email(project_id, material, vendors_data):
    """
    vendors_data: list of dicts with vendor_name, unit_price, delivery_time, payment_terms
    """
    _, _, manager = _cfg()

    rows = ""
    for v in vendors_data:
        rows += f"""
        <tr>
          <td>{v['vendor_name']}</td>
          <td>₹ {float(v['unit_price']):,.2f}</td>
          <td>{v.get('delivery_time','')}</td>
          <td>{v.get('payment_terms','')}</td>
        </tr>"""

    body = f"""
    <p>Vendor quotes for <b>{material}</b> (Project: {project_id}) require your approval.</p>
    <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse">
      <tr style="background:#f0f0f0">
        <th>Vendor</th><th>Unit Price</th><th>Delivery</th><th>Payment Terms</th>
      </tr>
      {rows}
    </table>
    <p>
      <a href="{APP_URL}?page=approval"
         style="padding:10px 20px;background:#2e7d32;color:white;
                text-decoration:none;border-radius:6px;display:inline-block;margin-top:12px">
        Open Approval Page
      </a>
    </p>
    <p>Regards,<br>Procurement Team</p>
    """
    subject = f"Vendor Approval Required — {material} (Project {project_id})"
    return _send(manager, subject, body)