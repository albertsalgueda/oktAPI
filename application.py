from asyncio.format_helpers import _format_callback_source
from stat import ST_ATIME
from flask import Flask, session, redirect, url_for, escape, request
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth

from main import *
#Help: https://flask.palletsprojects.com/en/1.1.x/quickstart/#rendering-templates
# export FLASK_APP=application.py
application = Flask(__name__,static_url_path='')
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(application)

auth = HTTPBasicAuth()

USER_DATA = {
    "admin": "topsecret"
}

class Campaign(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    budget = db.Column(db.Float) #represents daily budget
    spent = db.Column(db.Float) #represents total spent
    impressions = db.Column(db.Integer)
    conversions = db.Column(db.Integer)
    roas = db.Column(db.Float)

class State(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    budget = db.Column(db.Float)
    time = db.Column(db.Integer)
    #TODO
    #campaigns = db.Column(db.String(80),unique=True,nullable=False) 
    current_time = db.Column(db.Integer)  

@application.route('/')
def index():
    db.create_all()
    return "This is the official API of oktopus.io for Budget Optimization"


@application.route('/group')
def campaign_group():
    campaign_groups = State.query.all()
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

@application.route('/group',methods=['POST'])
def create_group():
    data = request.get_json(force=True)
    group = State(
        id = data['id'],
        budget = data['budget'],
        time = data['time'],
        campaigns = data['campaigns']) #TODO HERE

    #TODO -> validate that campaigns exist
    db.session.add(group)
    db.session.commit()
    return "Campaign group successfully created."

@application.route('/group/<id>')
def get_group(id):
    campaign_group = State.get_or_404(id)
    group = {
            "id":campaign_group.id,
            "budget":campaign_group.budget,
            "campaigns":campaign_group.campaigns,
            }
    return group

@application.route('/group/<id>',methods=['DELETE'])
def delete_group(id):
    group = ST_ATIME.query.get(id)
    if group is None:
        return {'error':'campaign group does not exist'}
    db.session.delete(group)
    db.session.commit()
    return "Successfully deleted."

@application.route('/group/<id>/budget',methods=['GET'])
def get_budget_allocation(id):
    group = State.query.get(id)
    if group is None:
        return {'error':'campaign group does not exist'}
    return group.budget_allocationç


@application.route('/group/<id>/next',methods=['GET'])
#TODO CALLS AI.act() returns a budget allocation --> self.budget_allocation , and current time step ( self.current_time) 

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