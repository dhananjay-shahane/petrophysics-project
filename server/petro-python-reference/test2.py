import win32com.client

# Initialize Outlook
outlook = win32com.client.Dispatch("Outlook.Application")
namespace = outlook.GetNamespace("MAPI")
inbox = namespace.GetDefaultFolder(6)  # 6 = Inbox

# Get last 10 emails
messages = inbox.Items
messages.Sort("[ReceivedTime]", True)  # Sort by newest first

print("\n📩 Checking latest 10 emails:\n")
for i in range(min(10, messages.Count)):
    msg = messages.Item(i + 1)
    print(f"{i+1}. {msg.Subject} from {msg.SenderEmailAddress} at {msg.ReceivedTime}")
    
target_email = "rajeshkumar@petrocene.com"  # Change to your actual email

for account in namespace.Folders:
    if account.Name.lower() == target_email.lower():
        inbox = account.Folders["Inbox"]  # Get the Inbox
        print(f"✅ Target Inbox Found: {inbox.Name}")
        break