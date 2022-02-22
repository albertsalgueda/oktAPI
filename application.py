from flask import Flask

# EB looks for an 'application' callable by default.
application = Flask(__name__)

@application.route("/")
def hello():
    return "This is the official Oktopus API, try /budget_allocation, /campaign to get sample data."

@application.route("/budget_allocation")
def allocation():
    alloc = {
        "1": 0.25, 
        "2": 10.3, 
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