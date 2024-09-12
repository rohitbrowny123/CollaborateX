from flask import Flask, render_template, redirect, url_for, flash, jsonify, request, session 
from flask_login import login_required, current_user
# from model import AdRequest
from sqlalchemy.exc import SQLAlchemyError 
import uuid

import urllib.request
import json

from flask import abort

from application import app
from datetime import datetime
from application.model import *


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            
            if user.role == 'influencer':
                return redirect(url_for('influencer_dashboard', id=user.id))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'sponsor':
                return redirect(url_for('sponsors_dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Details already exist', 'error')
            return redirect(url_for('home'))
        else:
            new_user = User(username=username, email=email, role=role)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('home'))


@app.route('/dashboard')
def dashboard():
   
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/')
def index():
    # Example of creating and adding an ad request to the database
    ad_request = AdRequest(campaign_id=1, influencer_id=1, requirements='dance', payment_amount=1000.0, status='live')
    db.session.add(ad_request)
    db.session.commit()
    return 'Ad request added successfully!'


@app.route('/add_user')
def add_user():
    new_user = User(username='sam', email='sam@gmail.com', role='user')
    new_user.set_password('sam123')
    db.session.add(new_user)
    db.session.commit()
    return "New user added!"

# Route to view a specific sponsor
@app.route('/view-sponsor/<sponsor_name>')
def view_sponsor(sponsor_name):
    # You can handle logic here to fetch data for the sponsor if needed
    return render_template('sponsors_dashboard.html', name=sponsor_name)


# Route to view a specific influencer
@app.route('/view-influencer/<influencer_name>')
def view_influencer(influencer_name):
    # You can handle logic here to fetch data for the influencer if needed
    return render_template('influencers_dashboard.html', name=influencer_name)

# Route for statistics page
@app.route('/statistics')
def statistics_page():
    active_users = User.query.filter(User.role != 'admin').count()
    total_campaigns = Campaign.query.count()
    public_campaigns = Campaign.query.filter_by(visibility='public').count()
    private_campaigns = Campaign.query.filter_by(visibility='private').count()
    total_ad_requests = AdRequest.query.count()
    pending_ad_requests = AdRequest.query.filter_by(status='Pending').count()
    approved_ad_requests = AdRequest.query.filter_by(status='Approved').count()
    revoked_ad_requests = AdRequest.query.filter_by(status='Revoked').count()
    flagged_users = User.query.filter(User.flag_reason != None).count()

    return render_template('statistics.html', 
                           active_users=active_users,
                           total_campaigns=total_campaigns,
                           public_campaigns=public_campaigns,
                           private_campaigns=private_campaigns,
                           total_ad_requests=total_ad_requests,
                           pending_ad_requests=pending_ad_requests,
                           approved_ad_requests=approved_ad_requests,
                           revoked_ad_requests=revoked_ad_requests,
                           flagged_users=flagged_users)
    
@app.route('/view_users')
def view_users():
    users = User.query.all()
    return render_template('view_users.html', users=users)

@app.route('/manage_campaigns')
def manage_campaigns():
    campaigns = Campaign.query.all()
    return render_template('manage_campaigns.html', campaigns=campaigns)

@app.route('/adminedit_user/<int:id>', methods=['GET', 'POST'])
def adminedit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        
        user.username = username
        user.email = email
        user.role = role
        
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('adminedit_user.html', user=user)


@app.route('/view_campaigns')
def view_campaigns():
    campaigns = Campaign.query.all()  # Example query to fetch all campaigns
    return render_template('sponsorview_campaign.html', campaigns=campaigns)

@app.route('/create_campaign', methods=['GET', 'POST'])
def create_campaign():
    if request.method == 'POST':
        name = request.form['name']
        # description = request.form['description']  # Ensure all fields are retrieved properly
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        budget = float(request.form['budget'])
        visibility = request.form['visibility']
        goals = request.form['goals']
        niche = request.form['niche']  # Ensure 'niche' is retrieved from the form
        sponsor_id = 1  # Assuming a sponsor with ID 1 for demonstration. Adjust as needed.

        new_campaign = Campaign(
            name=name,
            niche=niche,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            visibility=visibility,
            goals=goals,
            sponsor_id=sponsor_id
        )

        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('view_campaigns'))

    return render_template('sponsorcreate_campaign.html')


@app.route('/delete_campaign/<int:campaign_id>', methods=['GET'])
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    try:
        db.session.delete(campaign)
        db.session.commit()
        flash('Campaign deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting campaign: {}'.format(e), 'danger')
    
    return redirect(url_for('manage_campaigns'))


@app.route('/sponsors_dashboard')
def sponsors_dashboard():
    campaigns = Campaign.query.all()
    print(campaigns)  # Check if campaigns are fetched
    return render_template('sponsors_dashboard.html', campaigns=campaigns)

@app.route('/accept_ad_request', methods=['POST'])
def accept_ad_request():
    ad_request_id = request.json['ad_request_id']
    # Assuming you have a method to update status in your AdRequest model
    ad_request = AdRequest.query.get(ad_request_id)
    ad_request.status = 'Approved'
    db.session.commit()
    return jsonify({'message': 'Ad request approved successfully'})

@app.route('/reject_ad_request', methods=['POST'])
def reject_ad_request():
    ad_request_id = request.json['ad_request_id']
    # Assuming you have a method to update status in your AdRequest model
    ad_request = AdRequest.query.get(ad_request_id)
    ad_request.status = 'Revoked'
    db.session.commit()
    return jsonify({'message': 'Ad request rejected successfully'})

@app.route('/sponsor_stat')
def sponsor_stat():
    campaigns = db.session.query(Campaign).all()  # Fetch campaigns from the database
    ad_requests = db.session.query(AdRequest).all()  # Fetch ad requests from the database

    # Preparing data for charts
    campaign_names = [campaign.name for campaign in campaigns]
    campaign_budgets = [campaign.budget for campaign in campaigns]
    ad_request_statuses = {
        "Accepted": sum(1 for ad_request in ad_requests if ad_request.status == 'Accepted'),
        "Rejected": sum(1 for ad_request in ad_requests if ad_request.status == 'Rejected'),
        "Pending": sum(1 for ad_request in ad_requests if ad_request.status == 'Pending')
    }

    return render_template('sponsor_stat.html', 
                           campaign_names=campaign_names, 
                           campaign_budgets=campaign_budgets,
                           ad_request_statuses=ad_request_statuses)

@app.route('/manage_ads')
def manage_ads():
    ad_requests = AdRequest.query.all()
    return render_template('manage_adrequest.html', ad_requests=ad_requests)

@app.route('/manage_flagged')
def manage_flagged():
    # Fetch flagged campaigns and users from the database
    flagged_campaigns = Campaign.query.filter(Campaign.flag_reason.isnot(None)).all()
    flagged_users = User.query.filter(User.flag_reason.isnot(None)).all()
    
    return render_template('adminmanage_flaged.html', flagged_campaigns=flagged_campaigns, flagged_users=flagged_users)

@app.route('/find', methods=['GET', 'POST'])
def find():
    user = None
    campaigns = []
    ad_requests = []
    flagged_users = []
    flagged_campaigns = []

    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            user = User.query.filter_by(username=username).first()
            if user:
                campaigns = Campaign.query.filter_by(sponsor_id=user.id).all()
                ad_requests = AdRequest.query.filter_by(influencer_id=user.id).all()
            else:
                flash('User not found', 'error')
        else:
            flash('Please enter a username', 'error')
    
    flagged_users = User.query.filter(User.flag_reason.isnot(None)).all()
    flagged_campaigns = Campaign.query.filter(Campaign.flag_reason.isnot(None)).all()

    return render_template('admin_find.html', user=user, campaigns=campaigns, ad_requests=ad_requests,
                           flagged_users=flagged_users, flagged_campaigns=flagged_campaigns)


@app.route('/sponsor_find', methods=['GET', 'POST'])
def sponsor_find():
    user = None
    campaigns = []
    ad_requests = []

    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            user = User.query.filter_by(username=username).first()
            if user:
                # Retrieve campaigns associated with the sponsor (could be user or sponsor entity)
                campaigns = Campaign.query.filter_by(sponsor_id=user.id).all()
                # Retrieve ad requests associated with the campaigns
                ad_requests = AdRequest.query.join(Campaign).filter(Campaign.sponsor_id == user.id).all()
            else:
                flash('User not found', 'error')
        else:
            flash('Please enter a username', 'error')
    
    users = User.query.all()

    return render_template('sponsor_find.html', user=user, campaigns=campaigns, ad_requests=ad_requests, users=users)


@app.route('/influencer_dashboard/<int:id>')
def influencer_dashboard(id):
    # Querying the Influencer model assuming it represents users in your application
    influencer = Influencer.query.get(id)
    
    if influencer is None:
        flash(f'Influencer with ID {id} not found.', 'error')
        return redirect(url_for('some_redirect_route'))  # Redirect to another route or handle as needed
    
    return render_template('influencer_dashboard.html', influencer_id=id, influencer_name=influencer.username)


@app.route('/ad_request_details/<int:influencer_id>')
def ad_request_details(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if influencer is None:
        flash(f'Influencer with ID {influencer_id} not found.', 'error')
        return redirect(url_for('some_redirect_route'))  # Replace with an appropriate redirect route

    ad_requests = AdRequest.query.filter_by(influencer_id=influencer_id).all()
    return render_template('ad_request_details.html', ad_requests=ad_requests, influencer_id=influencer_id)


@app.route('/influ_profile', methods=['GET', 'POST'])
def influ_profile():
    influencer_id = session.get('influencer_id')
    influencer = get_influencer(influencer_id)
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        niche = request.form.get('niche')
        reach = request.form.get('reach')
        update_influencer_profile(influencer_id, name, category, niche, reach)
        session['influencer_name'] = name
        return redirect(url_for('influencer_dashboard'))
    
    return render_template('influencerprofile_edit.html', influencer=influencer)

# Create the database and the database table
@app.before_first_request
def create_tables():
    db.create_all()

def get_influencer(influencer_id):
    return Influencer.query.get(influencer_id)

def update_influencer_profile(influencer_id, name, category, niche, reach):
    influencer = Influencer.query.get(influencer_id)
    if influencer:
        influencer.name = name
        influencer.category = category
        influencer.niche = niche
        influencer.reach = reach
        db.session.commit()


@app.route('/search_campaigns')
def search_campaigns():
    campaigns = Campaign.query.all()
    
    # Assuming you have a way to get the current user's ID, for example:
    current_user_id = session.get('user_id')  # or however you store the current user's ID

    return render_template('influencersearch_campaign.html', campaigns=campaigns, current_user_id=current_user_id)


# Function to fetch campaigns from a data source (replace with your actual data source)
def get_campaigns_from_html():
    # Example: assuming campaigns are directly passed from the HTML
    campaigns = request.args.get('campaigns')  # Assuming campaigns are passed as a query parameter
    return campaigns

@app.route('/sponsorview_campaign', methods=['GET'])
def sponsorview_campaign():
    campaigns = get_campaigns_from_html()
    return render_template('sponsorview_campaign.html', campaigns=campaigns)


# Function to generate a unique ID
def generate_unique_id():
    return str(uuid.uuid4().hex)[:10]  # Generate a UUID and take the first 10 characters

@app.route('/influencermake_profile', methods=['GET', 'POST'])
def influencer_make_profile():
    if request.method == 'POST':
        username = request.form.get('name')
        category = request.form.get('category')
        niche = request.form.get('niche')
        followers = request.form.get('followers')
        reach = request.form.get('reach')

        try:
            # Create a new Influencer instance with an explicitly defined id
            new_influencer = Influencer(
                id=generate_unique_id(),  # Generate a unique id
                username=username,
                category=category,
                niche=niche,
                followers=int(followers),
                reach=int(reach)
            )

            # Add new influencer to session and commit to database
            db.session.add(new_influencer)
            db.session.commit()

            return render_template('influencermake_profile.html', success_message='Profile created successfully.')
        
        except SQLAlchemyError as e:
            error = str(e)
            db.session.rollback()  # Rollback changes on error
            return render_template('influencermake_profile.html', error_message=error)

    return render_template('influencermake_profile.html')

# This dictionary will hold the influencer profile data
influencer_data = {}



@app.route('/influencer/profile/<int:id>')
def influencer_current_profile(id):
    influencer = Influencer.query.get(id)
    if not influencer:
        app.logger.error(f'Influencer with ID {id} not found.')
        flash('Influencer not found.')
        return redirect(url_for('dashboard'))  # Redirect to dashboard or appropriate route

    return render_template('influencercurrent_profile.html', influencer=influencer)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    influencer_id = request.args.get('id')  # Assuming you pass influencer id in the URL
    influencer = Influencer.query.get(influencer_id)

    if not influencer:
        app.logger.error(f'Influencer with ID {influencer_id} not found.')
        flash('Influencer not found. Please create a profile first.')
        return redirect(url_for('create_profile'))  # Redirect to appropriate route

    if request.method == 'POST':
        influencer.username = request.form['name']
        influencer.category = request.form['category']
        influencer.niche = request.form['niche']
        influencer.reach = request.form['reach']
        influencer.followers = request.form['followers']  # Make sure to update followers
        db.session.commit()
        app.logger.info(f'Updated influencer: {influencer.username}')
        flash('Profile updated successfully.')
        return redirect(url_for('influencer_current_profile', id=influencer.id))  # Redirect to profile view

    return render_template('profile_edit.html', influencer_data=influencer)



@app.route('/create_ad_request', methods=['GET', 'POST'])
def create_ad_request():
    if request.method == 'POST':
        # Handle the form submission
        campaign_id = request.form['campaign']
        influencer_id = request.form['influencer']
        requirements = request.form['requirements']
        payment_amount = request.form['payment_amount']
        
        new_ad_request = AdRequest(
            campaign_id=campaign_id,
            influencer_id=influencer_id,
            requirements=requirements,
            payment_amount=payment_amount,
            status='Pending'
        )
        db.session.add(new_ad_request)
        db.session.commit()
        
        flash('Ad request created successfully!')
        return redirect(url_for('view_ad_requests'))
    
    # Fetch campaigns and influencers from the database
    campaigns = Campaign.query.all()
    influencers = Influencer.query.all()
    
    # Debug logs
    app.logger.debug(f'Campaigns: {campaigns}')
    app.logger.debug(f'Influencers: {influencers}')
    
    return render_template('sponsorcreate_ad.html', campaigns=campaigns, influencers=influencers)




@app.route('/view_ad_requests')
def view_ad_requests():
    ad_requests = AdRequest.query.all()
    return render_template('sponsorview_ad.html', ad_requests=ad_requests)

@app.route('/delete_ad_request/<int:ad_request_id>', methods=['POST'])
def delete_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    db.session.delete(ad_request)
    db.session.commit()
    return redirect(url_for('view_ad_requests'))


@app.route('/influencer/ad-requests', methods=['GET', 'POST'])
def influencer_ad_requests():
    if request.method == 'POST':
        ad_request_id = request.form.get('ad_request_id')
        action = request.form.get('action')

        ad_request = AdRequest.query.get(ad_request_id)

        if not ad_request:
            flash('Ad request not found.', 'error')
            return jsonify({'message': 'Ad request not found.'}), 404

        if action == 'accept':
            ad_request.status = 'Accepted'
            db.session.commit()
            flash('Ad request accepted successfully.', 'success')
            return jsonify({'message': 'Ad request accepted successfully.', 'status': ad_request.status})
        elif action == 'reject':
            ad_request.status = 'Rejected'
            db.session.commit()
            flash('Ad request rejected successfully.', 'success')
            return jsonify({'message': 'Ad request rejected successfully.', 'status': ad_request.status})

    ad_requests = AdRequest.query.all()
    return render_template('influencerview_adreq.html', ad_requests=ad_requests)

@app.route('/negotiate_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
def negotiate_ad_request(ad_request_id):
    ad_request = AdRequest.query.get(ad_request_id)

    if not ad_request:
        flash('Ad request not found.', 'error')
        return redirect(url_for('influencer_ad_requests'))

    if request.method == 'POST':
        requirements = request.form.get('requirements')
        payment_amount = request.form.get('payment_amount')

        ad_request.requirements = requirements
        ad_request.payment_amount = float(payment_amount)
        ad_request.status = 'Negotiation'

        db.session.commit()
        flash('Ad request modified and sent for negotiation.', 'success')
        return redirect(url_for('influencer_ad_requests'))

    return render_template('negotiate_ad_req.html', ad_request=ad_request)

@app.route('/accept_alternative', methods=['POST'])
def accept_alternative():
    data = request.json
    ad_request_id = data.get('ad_request_id')

    ad_request = AdRequest.query.get(ad_request_id)

    if not ad_request:
        return jsonify({'message': 'Ad request not found.'}), 404

    ad_request.status = 'Accepted'
    db.session.commit()

    return jsonify({'message': 'Ad request accepted successfully.', 'status': ad_request.status})

@app.route('/reject_alternative', methods=['POST'])
def reject_alternative():
    data = request.json
    ad_request_id = data.get('ad_request_id')

    ad_request = AdRequest.query.get(ad_request_id)

    if not ad_request:
        return jsonify({'message': 'Ad request not found.'}), 404

    ad_request.status = 'Rejected'
    db.session.commit()

    return jsonify({'message': 'Ad request rejected successfully.', 'status': ad_request.status})


@app.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'POST':
        # Handle form submission to create a new influencer profile
        username = request.form['username']
        category = request.form['category']
        niche = request.form['niche']
        reach = int(request.form['reach'])
        followers = int(request.form['followers'])
        
        # Example: Create a new Influencer object
        new_influencer = Influencer(username=username, category=category, niche=niche, reach=reach, followers=followers)
        db.session.add(new_influencer)
        db.session.commit()

        # Redirect to influencer dashboard with the newly created influencer's id
        return redirect(url_for('influencer_dashboard', id=new_influencer.id))
    
    return render_template('influencermake_profile.html')

# Assuming you have imports and setup for Flask, SQLAlchemy, etc.

@app.route('/admin/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
def edit_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if request.method == 'POST':
        campaign.name = request.form['name']
        campaign.niche = request.form['niche']
        
        # Convert string dates to datetime.date objects
        campaign.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        campaign.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        
        campaign.budget = float(request.form['budget'])  # Ensure budget is parsed as float
        
        # Update the campaign in the database
        db.session.commit()
        
        # Redirect to admin dashboard or any other relevant page
        return redirect(url_for('manage_campaigns'))  # Adjust as per your application's routes
    
    # Pass the campaign object to the template for rendering the form with current data
    return render_template('adminedit_campaign.html', campaign=campaign)



@app.route('/admin/dashboard')
def admin_dashboard():
    # Example: fetching user from database
    user = User.query.get(1)  # Replace with your actual query to fetch the user
    
    # Render template with user object in context
    return render_template('admin_dashboard.html', user=user)

@app.route('/delete_user/<int:id>', methods=['DELETE', 'POST'])
def delete_user(id):
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user', 'error')
    return redirect(url_for('admin_dashboard'))


@app.route('/edit_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
def edit_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    campaigns = Campaign.query.all()
    influencers = Influencer.query.all()
    
    if request.method == 'POST':
        ad_request.campaign_id = request.form['campaign_id']
        ad_request.influencer_id = request.form['influencer_id']
        ad_request.requirements = request.form['requirements']
        ad_request.payment_amount = request.form['payment_amount']
        ad_request.status = request.form['status']
        
        db.session.commit()
        flash('Ad request updated successfully', 'success')
        return redirect(url_for('manage_ads'))
    
    return render_template('manageadedit_adrequest.html', ad_request=ad_request, campaigns=campaigns, influencers=influencers)


@app.route('/remove_ad_request/<int:ad_request_id>')
def remove_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    db.session.delete(ad_request)
    db.session.commit()
    flash('Ad request deleted successfully', 'success')
    return redirect(url_for('manage_ads'))


# Flask routes with alternative names
@app.route('/sponsor_dashboard')
def sponsor_dashboard():
    campaigns = Campaign.query.all()
    ad_requests = AdRequest.query.all()
    return render_template('sponsor_dashboard.html', campaigns=campaigns, ad_requests=ad_requests)


@app.route('/new_ad_requests')
def new_ad_requests():
    ad_requests = AdRequest.query.all()
    ad_requests_data = [{
        'id': ad.id,
        'influencer': ad.influencer.username,
        'campaign': {
            'id': ad.campaign.id,
            'name': ad.campaign.name
        },
        'status': ad.status
    } for ad in ad_requests]
    return jsonify({'ad_requests': ad_requests_data})

@app.route('/all_campaigns')
def all_campaigns():
    campaigns = Campaign.query.all()
    campaigns_data = [{
        'id': campaign.id,
        'name': campaign.name,
        'niche': campaign.niche,
        'budget': campaign.budget
    } for campaign in campaigns]
    return jsonify({'campaigns': campaigns_data})


# Route to display ad requests details for sponsors
@app.route('/sponsor/ad-requests-details/<int:ad_request_id>')
def sponsor_ad_request_details(ad_request_id):
    # Query ad request details from the database
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    # Render sponsoradreq_view.html template with ad_request details
    return render_template('sponsoradreq_view.html', ad_request=ad_request)


@app.route('/sponsorview_adrequest_details/<int:ad_request_id>', methods=['GET'])
def sponsorview_adrequest_details(ad_request_id):
    try:
        # Construct the URL
        url = f'http://your-influencer-api/ad-requests/{ad_request_id}'
        
        # Fetch data using urllib
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        # Assuming data is retrieved successfully, render template
        return render_template('sponsorview_adrequest_details.html', ad_request=data)
    
    except urllib.error.URLError as e:
        # Handle errors, e.g., API not reachable
        error_message = f"Error fetching data: {e}"
        return f"Error: {error_message}", 500  # Return a simple error response with status code 500

@app.route('/admin_flag')
def admin_flag():
    users = User.query.all()
    campaigns = Campaign.query.all()
    return render_template('admin_flag.html', users=users, campaigns=campaigns)

@app.route('/flag_user/<int:id>', methods=['GET', 'POST'])
def flag_user(id):
    user = User.query.get_or_404(id)
    # Logic to flag the user (update a flag field in the User model, for example)
    user.flagged = True
    db.session.commit()
    flash(f'User {user.username} flagged successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/flag_campaign/<int:id>', methods=['GET', 'POST'])
def flag_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    # Logic to flag the campaign (update a flag field in the Campaign model, for example)
    campaign.flagged = True
    db.session.commit()
    flash(f'Campaign {campaign.name} flagged successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/flag', methods=['POST'])
def flag():
    data = request.get_json()
    item_id = data.get('id')
    item_type = data.get('type')
    reason = data.get('reason')

    if item_type == 'user':
        item = User.query.get(item_id)
    elif item_type == 'campaign':
        item = Campaign.query.get(item_id)
    else:
        return jsonify({'success': False, 'message': 'Invalid type'})

    if item:
        item.flag_reason = reason
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Item not found'})
