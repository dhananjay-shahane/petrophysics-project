import win32com.client
import time

# Initialize Outlook
outlook = win32com.client.Dispatch("Outlook.Application")
namespace = outlook.GetNamespace("MAPI")

# Define target email account
target_email = "rajeshkumar@petrocene.com"

# Locate the correct Inbox
inbox = None
for account in namespace.Folders:
    if account.Name.lower() == target_email.lower():
        inbox = account.Folders["Inbox"]
        print(f"✅ Target Inbox Found: {inbox.Name}")
        break

if not inbox:
    print("❌ Error: Could not find the target inbox.")
    exit()

# Store the latest email count
previous_email_count = inbox.Items.Count

print("📡 Email Listener Started... Monitoring for new emails.\n")

# Polling loop
while True:
    time.sleep(10)  # Wait for 10 seconds before checking again
    
    # Get the latest email count
    current_email_count = inbox.Items.Count
    
    if current_email_count > previous_email_count:
        print(f"📩 New Email Detected! (Total Emails: {current_email_count})")
        
        # Fetch the latest email
        latest_email = inbox.Items.GetLast()
        
        # Print details
        print(f"📬 Subject: {latest_email.Subject}")
        print(f"📧 From: {latest_email.SenderName}")
        print(f"📅 Received: {latest_email.ReceivedTime}")
        
        # Update email count
        previous_email_count = current_email_count
    else:
        print("⏳ No new emails detected...")
