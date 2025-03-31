from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, current_user, login_required
try:
    from werkzeug.urls import url_parse
except ImportError:
    from urllib.parse import urlparse
    
    def url_parse(url):
        return urlparse(url).netloc

from app import db, mail
from app.models import User, EmailTemplate, Campaign, Target, ClickEvent
from flask_mail import Message
from datetime import datetime
import uuid
import json
import csv
import io

# Blueprint definitions
main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__, url_prefix='/auth')
campaign = Blueprint('campaign', __name__, url_prefix='/campaign')
template = Blueprint('template', __name__, url_prefix='/template')
report = Blueprint('report', __name__, url_prefix='/report')

# Main routes
@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    campaigns = Campaign.query.filter_by(creator_id=current_user.id).all()
    templates = EmailTemplate.query.filter_by(creator_id=current_user.id).all()
    return render_template('dashboard.html', campaigns=campaigns, templates=templates)

# Auth routes
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('auth.register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=request.form.get('remember_me'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        
        return redirect(next_page)
    
    return render_template('login.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# Template routes
@template.route('/create', methods=['GET', 'POST'])
@login_required
def create_template():
    if request.method == 'POST':
        name = request.form.get('name')
        subject = request.form.get('subject')
        body = request.form.get('body')
        
        template = EmailTemplate(
            name=name,
            subject=subject,
            body=body,
            creator_id=current_user.id
        )
        
        db.session.add(template)
        db.session.commit()
        
        flash('Template created successfully!')
        return redirect(url_for('main.dashboard'))
    
    return render_template('template_editor.html')

@template.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_template(id):
    template = EmailTemplate.query.get_or_404(id)
    
    if template.creator_id != current_user.id:
        flash('You do not have permission to edit this template')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        template.name = request.form.get('name')
        template.subject = request.form.get('subject')
        template.body = request.form.get('body')
        template.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Template updated successfully!')
        return redirect(url_for('main.dashboard'))
    
    return render_template('template_editor.html', template=template)

@template.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_template(id):
    template = EmailTemplate.query.get_or_404(id)
    
    if template.creator_id != current_user.id:
        flash('You do not have permission to delete this template')
        return redirect(url_for('main.dashboard'))
    
    db.session.delete(template)
    db.session.commit()
    
    flash('Template deleted successfully!')
    return redirect(url_for('main.dashboard'))

# Campaign routes
@campaign.route('/create', methods=['GET', 'POST'])
@login_required
def create_campaign():
    templates = EmailTemplate.query.filter_by(creator_id=current_user.id).all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        template_id = request.form.get('template_id')
        
        campaign = Campaign(
            name=name,
            description=description,
            template_id=template_id,
            creator_id=current_user.id,
            status='draft'
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        flash('Campaign created successfully!')
        return redirect(url_for('campaign.edit', id=campaign.id))
    
    return render_template('campaign.html', templates=templates, now=datetime.now())


@campaign.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    campaign = Campaign.query.get_or_404(id)
    templates = EmailTemplate.query.filter_by(creator_id=current_user.id).all()
    
    if campaign.creator_id != current_user.id:
        flash('You do not have permission to edit this campaign')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        campaign.name = request.form.get('name')
        campaign.description = request.form.get('description')
        campaign.template_id = request.form.get('template_id')
        
        if request.form.get('scheduled_date') and request.form.get('scheduled_time'):
            date_str = request.form.get('scheduled_date')
            time_str = request.form.get('scheduled_time')
            scheduled_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            campaign.scheduled_at = scheduled_dt
            campaign.status = 'scheduled'
        
        db.session.commit()
        
        flash('Campaign updated successfully!')
        return redirect(url_for('main.dashboard'))
    
    return render_template('campaign.html', campaign=campaign, templates=templates, now=datetime.now())


@campaign.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    campaign = Campaign.query.get_or_404(id)
    
    if campaign.creator_id != current_user.id:
        flash('You do not have permission to delete this campaign')
        return redirect(url_for('main.dashboard'))
    
    db.session.delete(campaign)
    db.session.commit()
    
    flash('Campaign deleted successfully!')
    return redirect(url_for('main.dashboard'))

@campaign.route('/<int:id>/targets', methods=['GET', 'POST'])
@login_required
def manage_targets(id):
    campaign = Campaign.query.get_or_404(id)
    
    if campaign.creator_id != current_user.id:
        flash('You do not have permission to manage targets for this campaign')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        if 'csv_file' in request.files:
            csv_file = request.files['csv_file']
            if csv_file.filename != '':
                csv_data = csv_file.read().decode('utf-8')
                csv_io = io.StringIO(csv_data)
                csv_reader = csv.DictReader(csv_io)
                
                for row in csv_reader:
                    target = Target(
                        name=row.get('name', ''),
                        email=row.get('email', ''),
                        department=row.get('department', ''),
                        campaign_id=campaign.id
                    )
                    db.session.add(target)
                
                db.session.commit()
                flash('Targets imported successfully!')
        else:
            name = request.form.get('name')
            email = request.form.get('email')
            department = request.form.get('department')
            
            target = Target(
                name=name,
                email=email,
                department=department,
                campaign_id=campaign.id
            )
            
            db.session.add(target)
            db.session.commit()
            
            flash('Target added successfully!')
    
    targets = Target.query.filter_by(campaign_id=campaign.id).all()
    return render_template('campaign.html', campaign=campaign, targets=targets, tab='targets', now=datetime.now())


@campaign.route('/<int:id>/send', methods=['POST'])
@login_required
def send_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    
    if campaign.creator_id != current_user.id:
        flash('You do not have permission to send this campaign')
        return redirect(url_for('main.dashboard'))
    
    if campaign.status not in ['draft', 'scheduled']:
        flash('This campaign cannot be sent now')
        return redirect(url_for('campaign.edit', id=campaign.id))
    
    if not campaign.template:
        flash('Please assign an email template to this campaign')
        return redirect(url_for('campaign.edit', id=campaign.id))
    
    if campaign.targets.count() == 0:
        flash('Please add targets to this campaign')
        return redirect(url_for('campaign.manage_targets', id=campaign.id))
    
    # For immediate sending
    if request.form.get('send_now'):
        campaign.status = 'in_progress'
        db.session.commit()
        
        # In a real application, this would be a background task
        send_phishing_emails(campaign.id)
        
        campaign.status = 'completed'
        db.session.commit()
        
        flash('Campaign sent successfully!')
    else:
        # For scheduling
        date_str = request.form.get('scheduled_date')
        time_str = request.form.get('scheduled_time')
        
        if date_str and time_str:
            scheduled_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            campaign.scheduled_at = scheduled_dt
            campaign.status = 'scheduled'
            db.session.commit()
            
            flash('Campaign scheduled successfully!')
        else:
            flash('Please provide a valid schedule date and time')
    
    return redirect(url_for('main.dashboard'))

def send_phishing_emails(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return
    
    template = campaign.template
    tracking_domain = current_app.config.get('TRACKING_DOMAIN', request.host_url.rstrip('/'))
    
    for target in campaign.targets:
        # Generate a unique tracking ID
        tracking_id = str(uuid.uuid4())
        
        # Personalize the email content
        personalized_subject = template.subject.replace('{{name}}', target.name)
        personalized_subject = personalized_subject.replace('{{company}}', 'Company Name')
        
        personalized_body = template.body.replace('{{name}}', target.name)
        personalized_body = personalized_body.replace('{{company}}', 'Microsoft')
        personalized_body = personalized_body.replace('{{email}}', target.email)
        
        # Add tracking pixel and modify links
        tracking_pixel = f'<img src="{tracking_domain}/track/{tracking_id}/pixel" width="1" height="1" />'
        personalized_body = personalized_body.replace('</body>', f'{tracking_pixel}</body>')
        
        # Send the email
        msg = Message(
            subject=personalized_subject,
            recipients=[target.email],
            html=personalized_body
        )
        mail.send(msg)
        
        # Log the send event
        print(f"Would send phishing email to {target.email} with subject: {personalized_subject}")


# Report routes
@report.route('/<int:campaign_id>')
@login_required
def campaign_report(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.creator_id != current_user.id:
        flash('You do not have permission to view this report')
        return redirect(url_for('main.dashboard'))
    
    # Get statistics
    total_targets = campaign.targets.count()
    opened_count = campaign.click_events.filter_by(action='opened').count()
    clicked_count = campaign.click_events.filter_by(action='clicked').count()
    submitted_count = campaign.click_events.filter_by(action='submitted').count()
    
    # Calculate rates
    open_rate = (opened_count / total_targets) * 100 if total_targets > 0 else 0
    click_rate = (clicked_count / total_targets) * 100 if total_targets > 0 else 0
    submission_rate = (submitted_count / total_targets) * 100 if total_targets > 0 else 0
    
    return render_template(
        'reports.html',
        campaign=campaign,
        total_targets=total_targets,
        opened_count=opened_count,
        clicked_count=clicked_count,
        submitted_count=submitted_count,
        open_rate=open_rate,
        click_rate=click_rate,
        submission_rate=submission_rate
    )

@report.route('/<int:campaign_id>/export', methods=['GET'])
@login_required
def export_report(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.creator_id != current_user.id:
        flash('You do not have permission to export this report')
        return redirect(url_for('main.dashboard'))
    
    # Create a CSV string
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Name', 'Email', 'Department', 'Opened', 'Clicked', 'Submitted', 'IP Address', 'User Agent', 'Timestamp'])
    
    # Write data
    for target in campaign.targets:
        opened = campaign.click_events.filter_by(target_id=target.id, action='opened').first()
        clicked = campaign.click_events.filter_by(target_id=target.id, action='clicked').first()
        submitted = campaign.click_events.filter_by(target_id=target.id, action='submitted').first()
        
        writer.writerow([
            target.name,
            target.email,
            target.department,
            'Yes' if opened else 'No',
            'Yes' if clicked else 'No',
            'Yes' if submitted else 'No',
            clicked.ip_address if clicked else '',
            clicked.user_agent if clicked else '',
            clicked.timestamp.strftime('%Y-%m-%d %H:%M:%S') if clicked else ''
        ])
    
    # Create response
    output.seek(0)
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename=campaign_{campaign_id}_report.csv'
    }
@campaign.route('/<int:campaign_id>/target/<int:target_id>/delete', methods=['POST'])
@login_required
def delete_target(campaign_id, target_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    target = Target.query.get_or_404(target_id)
    
    if campaign.creator_id != current_user.id:
        flash('You do not have permission to manage targets for this campaign')
        return redirect(url_for('main.dashboard'))
    
    if target.campaign_id != campaign.id:
        flash('Target does not belong to this campaign')
        return redirect(url_for('campaign.manage_targets', id=campaign.id))
    
    db.session.delete(target)
    db.session.commit()
    
    flash('Target removed successfully!')
    return redirect(url_for('campaign.manage_targets', id=campaign.id))


# Tracking routes
@main.route('/track/<tracking_id>/pixel')
def track_pixel(tracking_id):
    # In a real implementation, you would look up the tracking ID and record an 'opened' event
    # For now, we'll just return a transparent 1x1 pixel
    return '', 200, {'Content-Type': 'image/gif'}

@main.route('/track/<tracking_id>/link')
def track_link(tracking_id):
    # Get the original URL from the query parameters
    original_url = request.args.get('url', '#')
    
    try:
        # Find the most recent campaign
        campaign = Campaign.query.order_by(Campaign.id.desc()).first()
        if campaign:
            # Find a target from this campaign
            target = Target.query.filter_by(campaign_id=campaign.id).first()
            if target:
                # Record the click event
                event = ClickEvent(
                    target_id=target.id,
                    campaign_id=campaign.id,
                    timestamp=datetime.utcnow(),
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string if request.user_agent else None,
                    action='clicked'
                )
                db.session.add(event)
                db.session.commit()
                print(f"Click recorded for target {target.id} in campaign {campaign.id}")
            else:
                print("No target found for this campaign")
        else:
            print("No campaign found")
    except Exception as e:
        print(f"Error recording click: {str(e)}")
    
    # Redirect to the phishing page
    return redirect(url_for('main.phishing_page', tracking_id=tracking_id))

@main.route('/p/<tracking_id>')
def phishing_page(tracking_id):
    # This would be your phishing page (e.g., fake login form)
    return render_template('phishing_page.html', tracking_id=tracking_id)

@main.route('/p/<tracking_id>/submit', methods=['POST'])
def submit_phishing_form(tracking_id):
    # In a real implementation, you would:
    # 1. Look up the tracking ID to get the campaign and target
    # 2. Record a 'submitted' event with the form data
    # 3. Redirect to a reveal page or education page
    
    # For the demo, we'll redirect to a reveal page
    return redirect(url_for('main.reveal_page', tracking_id=tracking_id))

@main.route('/p/<tracking_id>/reveal')
def reveal_page(tracking_id):
    # This would be your educational reveal page
    return render_template('reveal_page.html', tracking_id=tracking_id)
