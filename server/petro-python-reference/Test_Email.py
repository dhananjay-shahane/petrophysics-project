import send_email
import pythoncom
import win32com.client
import time
# send_email.Send_Email()
TARGET_EMAIL = "rajeshkumar@petrocene.com"  # Change this to your Outlook account email


if __name__ == "__main__":
    print(f"📡 Checking for new emails in {TARGET_EMAIL} every 10 seconds...")

    while True:
        send_email.check_new_emails()
        time.sleep(10)  # Check every 10 seconds