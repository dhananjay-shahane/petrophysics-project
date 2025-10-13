import win32com.client
import pythoncom
TARGET_EMAIL = "rajeshkumar@petrocene.com"  # Change this to your Outlook email
FOLDER_NAME = "Inbox"  # Change if needed
ALLOWED_SENDERS = ["rkumar.emails@gmail.com"]

class EmailEventHandler:
    def OnItemAdd(self, item):
        try:
            if hasattr(item, "Class") and item.Class == 43:  # 43 = MailItem
                sender_email = item.SenderEmailAddress.lower()
                if sender_email in [email.lower() for email in ALLOWED_SENDERS]:
                    print(f"\n📩 New Email from {sender_email}:")
                    print(f"   🏷️ Subject: {item.Subject}")
                    print(f"   📜 Body Preview: {item.Body[:200]}...\n")
                    item.Unread = False  # Mark email as read
                    item.Save()
                else:
                    print(f"❌ Ignored email from: {sender_email}")
        except Exception as e:
            print(f"⚠️ Error processing email: {e}")

def get_inbox(target_email):
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    for folder in outlook.Folders:
        if target_email.lower() in folder.Name.lower():
            return folder.Folders["Inbox"]
    return None

def main():
    inbox = get_inbox(TARGET_EMAIL)
    if not inbox:
        print(f"❌ Could not find the inbox for {TARGET_EMAIL}")
        return

    print(f"📡 Listening for new emails in {TARGET_EMAIL}...")

    items = inbox.Items
    event_handler = win32com.client.WithEvents(items, EmailEventHandler)

    # Run the event loop
    while True:
        pythoncom.PumpWaitingMessages()

if __name__ == "__main__":
    main()