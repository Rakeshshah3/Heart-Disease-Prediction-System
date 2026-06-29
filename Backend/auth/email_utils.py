import smtplib
import random
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(to_email, otp):

    msg = MIMEMultipart("alternative")

    msg["Subject"] = "Heart Disease Predictor - Verification Code"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background:#f4f6f9; padding:20px;">

        <div style="
            max-width:600px;
            margin:auto;
            background:white;
            border-radius:12px;
            padding:30px;
            box-shadow:0 2px 10px rgba(0,0,0,0.1);
        ">

            <h2 style="color:#2563eb; text-align:center;">
                ❤️ Heart Disease Predictor
            </h2>

            <p>Hello,</p>

            <p>
                A verification code has been generated for your
                <strong>Heart Disease Predictor</strong> account.
            </p>

            <p>
                Please use the verification code below:
            </p>

            <div style="
                background:#f3f4f6;
                padding:20px;
                text-align:center;
                border-radius:8px;
                margin:20px 0;
            ">
                <h1 style="
                    letter-spacing:6px;
                    color:#111827;
                    margin:0;
                ">
                    {otp}
                </h1>
            </div>

            <p>
                This verification code is valid for
                <strong>10 minutes</strong>.
            </p>

            <p>
                If you did not request this verification code,
                please ignore this email.
            </p>

            <hr>

            <p style="color:gray; font-size:12px;">
                Heart Disease Predictor Team<br>
                AI-Powered Health Risk Analysis Platform
            </p>

        </div>

    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)