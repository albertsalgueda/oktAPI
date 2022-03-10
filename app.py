from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

#Help: https://flask.palletsprojects.com/en/1.1.x/quickstart/#rendering-templates

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


class Campaign(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    budget = db.Column(db.Float)
    spent = db.Column(db.Float)
    impressions = db.Column(db.Integer)
    conversions = db.Column(db.Integer)
    roas = db.Column(db.Float)

    def __repr__(self):
        return f"{self.id} - {self.roas}"


@app.route('/')
def index():
    return "This is the official API of oktopus.io for Budget"

@app.route('/campaigns')
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

@app.route('/campaigns',methods=['POST'])
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

@app.route('/campaigns/<id>')
def get_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    return {"id":campaign.id,"budget":campaign.budget,"spent":campaign.spent,"impressions":campaign.impressions,"conversions":campaign.conversions,"roas":campaign.roas}

@app.route('/campaigns/<id>',methods=['DELETE'])
def delete(id):
    campaign = Campaign.query.get(id)
    if campaign is None:
        return {'error':'campaign does not exist'}
    db.session.delete(campaign)
    db.session.commit()
    return "Successfully deleted."

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = False
    app.run()