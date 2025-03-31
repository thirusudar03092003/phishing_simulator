import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Mailtrap credentials
username = "d71b053e0ad7a0"
password = "090ffcbac03d61"
server = "sandbox.smtp.mailtrap.io"
port = 2525

# Create message
msg = MIMEMultipart()
msg['Subject'] = "Test from Python Script"
msg['From'] = "test@example.com"
msg['To'] = "recipient@example.com"

# Add HTML body
html = """
<html>
<body>
    <h1>Hello from Python!</h1>
    <p>This is a test email sent directly using smtplib.</p>
</body>
</html>
"""
msg.attach(MIMEText(html, 'html'))

# Connect to Mailtrap and send
try:
    # Create server connection
    server = smtplib.SMTP(server, port)
    server.set_debuglevel(1)  # Show communication with the server
    
    # Start TLS encryption
    server.starttls()
    
    # Login
    server.login(username, password)
    
    # Send email
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    
    # Disconnect
    server.quit()
    
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
