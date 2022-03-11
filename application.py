from flask import Flask, session, redirect, url_for, escape, request
from flask_sqlalchemy import SQLAlchemy

#Help: https://flask.palletsprojects.com/en/1.1.x/quickstart/#rendering-templates
# export FLASK_APP=application.py
application = Flask(__name__,static_url_path='')
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(application)

session = {}
session['username'] = 'admin'

class Campaign(db.Model,):
    id = db.Column(db.Integer,primary_key=True)
    budget = db.Column(db.Float) #represents daily budget
    spent = db.Column(db.Float) #represents total spent
    impressions = db.Column(db.Integer)
    conversions = db.Column(db.Integer)
    roas = db.Column(db.Float)

    def __init__(self,id,budget,spent,impressions,conversions,roas):
        #falta determinar como podemos saber el tiempo que lleva la campaña 
        self.id = id    
        self.budget = budget #daily budget
        self.spent = spent
        self.impressions = impressions
        self.conversions = conversions
        self.roi = roas

class CampaignGroup(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    budget = db.Column(db.Float)
    time = db.Column(db.Integer)
    campaigns = db.Column(db.String(80),unique=True,nullable=False)
    
    

    

@application.route('/')
def index():
    db.create_all()
    return "This is the official API of oktopus.io for Budget Optimization"


@application.route('/login', methods = ['GET', 'POST'])
def login():
   if request.method == 'POST':
      session['username'] = request.form['username']
      return redirect(url_for('index'))
   return '''
   <form action = "" method = "post">
      <p><input type = text name = username/></p>
      <p<<input type = submit value = Login/></p>
   </form>	
'''
@application.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('index'))


@application.route('/campaign_group')
def campaign_group():
    campaign_groups = CampaignGroup.query.all()
    if campaign_groups is None:
        return {'error':'group does not exist'}
    output = []
    for campaign_group in campaign_groups:
        campaign_data = {
            "id":campaign_group.id,
            "budget":campaign_group.budget,
            "time":campaign_group.time,
            "campaigns": campaign_group.campaigns
            }
        output.append(campaign_data)
    return {"campaigns":output}

@application.route('/campaign_group',methods=['POST'])
def create_group():
    data = request.get_json(force=True)
    group = CampaignGroup(
        id = data['id'],
        budget = data['budget'],
        time = data['time'],
        campaigns = data['campaigns'])

    #TODO -> validate that campaigns exist

    db.session.add(group)
    db.session.commit()
    return "Campaign group successfully created."

@application.route('/campaign_group/<id>')
def get_group(id):
    campaign_group = CampaignGroup.get_or_404(id)
    group = {
            "id":campaign_group.id,
            "budget":campaign_group.budget,
            "campaigns":campaign_group.campaigns,
            }
    return group

@application.route('/campaign_group/<id>',methods=['DELETE'])
def delete_group(id):
    group = CampaignGroup.query.get(id)
    if group is None:
        return {'error':'campaign does not exist'}
    db.session.delete(group)
    db.session.commit()
    return "Successfully deleted."


@application.route('/campaigns')
def campaigns():
    campaigns = Campaign.query.all()
    output = []
    for campaign in campaigns:
        campaign_data = {
            "id":campaign.id,
            "budget":campaign.budget,
            "spent":campaign.spent,
            "impressions":campaign.impressions,
            "conversions":campaign.conversions,
            "roas":campaign.roas
            }
        output.append(campaign_data)
    return {"campaigns":output}


@application.route('/campaigns',methods=['POST'])
def add_campaigns():
    data = request.get_json(force=True)
    campaign = Campaign(
        id = int(data['id']), 
        budget = data['budget'],
        spent = data['spent'], 
        impressions = data['impressions'], 
        conversions = data['conversions'], 
        roas = data['roas'])
    #db.session.rollback()
    db.session.add(campaign)
    db.session.commit()
    return "Successfully added."

@application.route('/campaigns/<id>')
def get_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    return {"id":campaign.id,"budget":campaign.budget,"spent":campaign.spent,"impressions":campaign.impressions,"conversions":campaign.conversions,"roas":campaign.roas}

@application.route('/campaigns/<id>',methods=['DELETE'])
def delete(id):
    campaign = Campaign.query.get(id)
    if campaign is None:
        return {'error':'campaign does not exist'}
    db.session.delete(campaign)
    db.session.commit()
    return "Successfully deleted."

@application.route('/campaigns/<id>',methods=['PUT'])
def update_campaign(id):
    data = request.get_json(force=True)
    campaign = Campaign.query.get(id)
    if campaign is None:
        return {'error':'campaign does not exist'}
    campaign.budget = data['budget']
    campaign.spent = data['spent'] 
    campaign.impressions = data['impressions'] 
    campaign.conversions = data['conversions'] 
    campaign.roas = data['roas']
    db.session.commit()
    return "Successfully updated."

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = False
    application.run()