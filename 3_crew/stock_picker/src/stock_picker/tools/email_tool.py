from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import smtplib
from email.mime.text import MIMEText

class EmailMessage(BaseModel):
    """A message to be sent via email"""
    subject: str = Field(..., description="The subject of the email.")
    body: str = Field(..., description="The body content of the email.")

class EmailTool(BaseTool):
    """A tool for sending emails"""

    def send_email(self, email: EmailMessage):
        """Send an email message"""
        # Implementation for sending email
    name: str = "Send an Email"
    description: str = (
        "This tool is used to send an email to the specified recipient."
    )
    args_schema: Type[BaseModel] = EmailMessage
    # let's use gmail smtp for this example and implement it
    def _run(self, subject: str, body: str) -> str:
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_PASSWORD")
        recipient_email = os.getenv("RECIPIENT_EMAIL")

        print(f"Email Subject: {subject}")
        print(f"Email Body: {body}")

        # Here you would implement the actual email sending logic using smtplib or any email service API
        # we are using gmail smtp
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(gmail_user, gmail_password)
                msg = MIMEText(body)
                msg["Subject"] = subject
                msg["From"] = gmail_user
                msg["To"] = recipient_email
                server.send_message(msg)
        except Exception as e:
            print(f"Error sending email: {e}")
            return '{"email": "failed"}'

        return '{"email": "sent"}'
