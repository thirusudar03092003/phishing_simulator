# Phishing Email Simulator

## Project Overview
This is a comprehensive phishing email simulator. The tool simulates phishing attack emails for security awareness training, helping organizations train employees to recognize and avoid phishing attempts.

## Features

- **User Management**: Register and authenticate users
- **Email Template Creation**: Create customizable HTML email templates with placeholders
- **Campaign Management**: Set up targeted phishing campaigns
- **Target Management**: Add targets individually or import via CSV
- **Email Sending**: Send simulated phishing emails through a secure SMTP server
- **Tracking System**: Track email opens, link clicks, and form submissions
- **Reporting Dashboard**: Generate detailed reports on campaign performance
- **Educational Reveal Page**: Show users they've been part of a phishing test

## Technology Stack

- **Backend**: Python with Flask framework
- **Database**: SQLAlchemy ORM with SQLite
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Email**: Flask-Mail for email integration
- **Authentication**: Flask-Login for user management
- **Testing**: Mailtrap for email testing

## Project Structure
```
phishing_simulator/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── campaign.html
│   │   ├── template_editor.html
│   │   ├── reports.html
│   │   ├── phishing_page.html
│   │   └── reveal_page.html
│   └── static/
│       ├── css/
│       │   └── main.css
│       ├── js/
│       │   └── main.js
│       └── img/
│           └── Microsoft_Logo_64px.png
├── config.py
├── requirements.txt
└── run.py
```

## Installation & Setup

1. Clone the repository:
```bash
git clone https://github.com/thirusudar03092003/phishing_simulator.git
cd phishing_simulator
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables by creating a `.env` file:
```plaintext
SECRET_KEY=your_secret_key_here
MAIL_SERVER=smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=your_mailtrap_username
MAIL_PASSWORD=your_mailtrap_password
MAIL_USE_TLS=True
MAIL_DEFAULT_SENDER=phishing@example.com
```

5. Run the application:
```bash
python run.py
```

6. Access the application at [http://localhost:5000](http://localhost:5000)

## Usage Guide

### Creating Email Templates
1. Log in to the application
2. Navigate to "Create Template"
3. Design your phishing email using HTML
4. Use placeholders like `{{name}}`, `{{company}}`, and `{{email}}` for personalization
5. Save your template

### Setting Up Campaigns
1. Navigate to "Create Campaign"
2. Enter campaign details and select a template
3. Add targets individually or import via CSV
4. Schedule the campaign or send immediately

### Viewing Reports
1. After sending a campaign, navigate to the "Dashboard"
2. Click "Report" next to any campaign
3. View detailed statistics including open rates, click rates, and submission rates
4. Export reports as CSV for further analysis

## Email Testing with Mailtrap

This project uses Mailtrap for safely testing phishing emails without sending them to real recipients. Mailtrap is a test mail server solution that captures all outgoing emails in a virtual inbox.

### Setting Up Mailtrap

1. Create a free account at [Mailtrap.io](https://mailtrap.io/signin)
2. After signing in, go to your Mailtrap inbox (create one if you don't have it)
3. Click on "SMTP Settings" and copy the credentials for Flask

### Configuring Mailtrap in the Project

1. Update your `.env` file with the Mailtrap credentials:
```plaintext
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=your_mailtrap_username
MAIL_PASSWORD=your_mailtrap_password
MAIL_USE_TLS=True
MAIL_DEFAULT_SENDER=phishing@example.com
```

2. Restart your Flask application after making these changes

### Using Mailtrap for Testing

When you send a campaign from your phishing simulator:

1. All emails will be captured in your Mailtrap inbox instead of being sent to real recipients
2. You can view the emails exactly as they would appear to recipients
3. Mailtrap provides detailed information about:
   - HTML/CSS rendering
   - Spam analysis
   - Link validation
   - MIME structure

This allows you to safely test your phishing templates and ensure they look convincing without risking accidental delivery to real email addresses.

### Benefits of Using Mailtrap

- **Safe Testing Environment**: No risk of accidentally sending phishing emails to real users
- **Spam Score Analysis**: Check if your emails might be flagged by spam filters
- **HTML/CSS Validation**: Ensure your templates render correctly across email clients
- **Team Collaboration**: Share your test inbox with team members (on paid plans)

For production deployment in a real security awareness program, you would replace Mailtrap with an actual SMTP server configured with proper authentication and authorization controls.

## Security Considerations

This tool is intended for educational and security awareness training purposes only. Misuse of this tool may violate laws and regulations. Always ensure:

- You have proper authorization to conduct phishing simulations
- Targets are informed that they may receive security awareness training
- No sensitive information is collected during simulations
- All data is handled in accordance with privacy regulations

## Future Enhancements

- Integration with Active Directory for user management
- AI-generated phishing templates
- Mobile app for campaign monitoring
- Integration with security awareness training platforms
- Advanced analytics and machine learning for target susceptibility scoring

## About the Developer

Developed by Thiru Sudar S L, a B.Tech AI & DS student at Velammal Engineering College, Ambattur. This project demonstrates skills in cybersecurity, web development, and software engineering.

## License

This project is for educational purposes only. Please use responsibly.

