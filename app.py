#API File

from flask import Flask
application = Flask(__name__)

@application.route('/')
def hello_world():
   return "This is oktopus.io APIs"

# https://aws.amazon.com/getting-started/hands-on/serve-a-flask-app/
