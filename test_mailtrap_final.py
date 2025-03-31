from flask import Flask
from flask_mail import Mail, Message

# Create app
app = Flask(__name__)

# Configure mail settings with your exact credentials
app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'd7100530dad7a0'
app.config['MAIL_PASSWORD'] = '090ffcbac03d61'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

# Initialize mail
mail = Mail(app)

# Create a test message
with app.app_context():
    try:
        msg = Message(
            subject="Test Email from Flask-Mail",
            sender="phishing@example.com",
            recipients=["test@example.com"]
        )
        msg.body = "This is a test email sent from Flask-Mail with Mailtrap"
        msg.html = "<p>This is a <b>test email</b> sent from Flask-Mail with Mailtrap</p>"
        
        print("Attempting to send email...")
        mail.send(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {str(e)}")
