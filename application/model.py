from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash




db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    flag_reason = db.Column(db.Text, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Sponsor(db.Model):
    __tablename__ = 'sponsors'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True)

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    niche = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(10), nullable=False)
    goals = db.Column(db.Text, nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsors.id'), nullable=False)
    ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True)
    flag_reason = db.Column(db.Text, nullable=True)

class Influencer(db.Model):
    __tablename__ = 'influencers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    niche = db.Column(db.String(50), nullable=True)
    reach = db.Column(db.Integer, nullable=False)
    followers = db.Column(db.Integer, nullable=False)
    ad_requests = db.relationship('AdRequest', backref='influencer', lazy=True)

class AdRequest(db.Model):
    __tablename__ = 'ad_requests'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencers.id'), nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    
    
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash




# db = SQLAlchemy()

# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     password_hash = db.Column(db.String(128), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     role = db.Column(db.String(20), nullable=False)
#     flag_reason = db.Column(db.Text, nullable=True)

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)

# class Sponsor(db.Model):
#     __tablename__ = 'sponsors'
#     id = db.Column(db.Integer, primary_key=True)
#     company_name = db.Column(db.String(100), nullable=False)
#     industry = db.Column(db.String(100), nullable=False)
#     budget = db.Column(db.Float, nullable=False)

# # class Influencer(db.Model):
# #     __tablename__ = 'influencers'
# #     id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
# #     username = db.Column(db.String(100), nullable=False)
# #     category = db.Column(db.String(50), nullable=False)
# #     niche = db.Column(db.String(50), nullable=True)
# #     reach = db.Column(db.Integer, nullable=False)
# #     followers = db.Column(db.Integer, nullable=False)
# #     ad_requests = db.relationship('AdRequest', backref='influencer', lazy=True)

# class Influencer(db.Model):
#     __tablename__ = 'influencers'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     username = db.Column(db.String(100), nullable=False)
#     category = db.Column(db.String(50), nullable=False)
#     niche = db.Column(db.String(50), nullable=True)
#     reach = db.Column(db.Integer, nullable=False)
#     followers = db.Column(db.Integer, nullable=False)
#     ad_requests = db.relationship('AdRequest', backref='influencer', lazy=True)

# class Campaign(db.Model):
#     __tablename__ = 'campaigns'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(120), nullable=False)
#     niche = db.Column(db.String(120), nullable=False)
#     start_date = db.Column(db.Date, nullable=False)
#     end_date = db.Column(db.Date, nullable=False)
#     budget = db.Column(db.Float, nullable=False)
#     visibility = db.Column(db.String(10), nullable=False)
#     goals = db.Column(db.Text, nullable=False)  # New column for goals
#     sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsors.id'), nullable=False)
#     ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True)
#     flag_reason = db.Column(db.Text, nullable=True)

# # class AdRequest(db.Model):
# #     __tablename__ = 'ad_requests'
# #     id = db.Column(db.Integer, primary_key=True)
# #     campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
# #     influencer_id = db.Column(db.Integer, db.ForeignKey('influencers.id'), nullable=False)
# #     requirements = db.Column(db.Text, nullable=False)
# #     payment_amount = db.Column(db.Float, nullable=False)
# #     status = db.Column(db.String(20), nullable=False)

# class AdRequest(db.Model):
#     __tablename__ = 'ad_requests'
#     id = db.Column(db.Integer, primary_key=True)
#     campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
#     influencer_id = db.Column(db.Integer, db.ForeignKey('influencers.id'), nullable=False)
#     requirements = db.Column(db.Text, nullable=False)
#     payment_amount = db.Column(db.Float, nullable=False)
#     status = db.Column(db.String(20), nullable=False, default='Pending')