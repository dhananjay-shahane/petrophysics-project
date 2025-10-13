import imaplib
import email
from email.header import decode_header
from email_script import *

# your email credentials
username = "rkumar.emails@gmail.com"
# username = "rajatrathore1.emails@gmail.com"
password = "ogyv wrkr pgwr jony"
# specific_sender_email = "rajeshkumar@petrocene.com"
specific_sender_email = "rajatrathore1@gmail.com"
# Connect to the Gmail IMAP server
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(username, password)

# Select the mailbox you want to check
mail.select("inbox")

# Search for unread emails (UNSEEN)
status, messages = mail.search(None, 'ALL')

# Convert the messages to a list of email IDs
email_ids = messages[0].split()

# List to store emails from the specific sender
emails_from_sender = []

# Check if there are any unread emails
if email_ids:
    # Limit to the last 10 unread emails
    last_10_email_ids = email_ids[-10:]  # Get the last 10 emails (from the newest)

    # Iterate through these 10 emails
    for email_id in last_10_email_ids:
        _, msg = mail.fetch(email_id, "(RFC822)")
        for response_part in msg:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else 'utf-8')
                from_ = msg.get("From")

                # Check if the email is from the specific sender and subject starts with "run"
                if specific_sender_email in from_.lower() and subject.lower().startswith("load"):
                    emails_from_sender.append((email_id, subject, from_,msg))

    # If we found emails from the specific sender
    if emails_from_sender:
        # Sort emails by the order they were received (newest first)
        latest_email = emails_from_sender[-1]  # Get the most recent email from that sender
        
        print(f"Latest email from {latest_email[2]} with subject: {latest_email[1]}")
        
        # Extract the email message
        msg = latest_email[3]
        # Store the subject in a variable before looping over the parts
        subject_of_email = latest_email[1]  # This stores the subject of the latest email
        # Initialize variables to store body and attachment
        body = None
        attachment_content = None
        attachment_filename = None

        # Check for the body content (plaintext or HTML)
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Look for the plain text part or the HTML part
                if "attachment" not in content_disposition:  # Skip attachments
                    if content_type == "text/plain":  # Plaintext part
                        body = part.get_payload(decode=True).decode("utf-8")
                        break  # We found the body, stop looking
                    elif content_type == "text/html":  # HTML part
                        body = part.get_payload(decode=True).decode("utf-8")
                        break  # We found the HTML body, stop looking
        else:
            # If it's not multipart, it's a single part message (either text/plain or text/html)
            content_type = msg.get_content_type()
            if content_type == "text/plain":
                body = msg.get_payload(decode=True).decode("utf-8")
            elif content_type == "text/html":
                body = msg.get_payload(decode=True).decode("utf-8")

        # Print or process the body content
        if body:
            print(f"Body of the email: {body[:200]}...")  # Print the first 200 characters as a preview
        else:
            print("No body content found.")

        # Check for attachments
        if msg.is_multipart():
            for part in msg.walk():
                # If the part is an attachment
                content_disposition = str(part.get("Content-Disposition"))
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename and filename.endswith(".las"):  # Check if it's a text file
                        print(f"Found attachment: {filename}")
                        
                        # Get the content of the attachment
                        attachment_content = part.get_payload(decode=True).decode("utf-8")
                        attachment_filename = filename

                        # Process the attachment content using a function from app.py
                        # process_attachment(attachment_content)  # You can adjust this function as needed
                        db = DatabaseQuery()
                        db.load_Single_LAS_File_From_Email(attachment_content)

                        break  # Stop after processing the first text file attachment

        else:
            print("No attachments found in the latest email.")

        # get_current_project()  # Call the function from app.py
        # Check if the subject contains a specific keyword to trigger the task
        if "load las file" in subject_of_email.lower():
            print("Conditions met! Running the task...")
            get_current_project()  # Call the function from app.py
    else:
        print(f"No unread emails from the sender {specific_sender_email}")
else:
    print("No unread emails found.")

# Log out after the process is complete
mail.logout()
