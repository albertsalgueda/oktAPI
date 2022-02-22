from flask import Flask
from flask import render_template

#Help: https://flask.palletsprojects.com/en/1.1.x/quickstart/#rendering-templates



application = Flask(__name__)

# EB looks for an 'application' callable by default.
@application.route("/")
def hello():
    return "This is the official Oktopus API, try /budget_allocation, /campaign to get sample data."

@application.route("/home")
def home():
    return render_template("home.html")

@application.route("/budget_allocation")
def allocation():
    alloc = {
        "1": 0.25, 
        "2": 0.3, 
        "3": 0.25,
        "4": 0.2
    }
    return alloc

@application.route("/campaign")
def campaign():
    camp = {
        "campaign_id": 1,
        "budget": 100,
        "spent": 10,
        "impressions": 54345,
        "conversions": 543,
        "roi": 1.4
    }
    return camp


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()