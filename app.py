#API File

from flask import Flask
application = Flask(__name__)

@application.route('/')
def main():
   return "This is oktopus.io APIs"

if __name__ == '__main__':
   application.run(debug=True)
# https://aws.amazon.com/getting-started/hands-on/serve-a-flask-app/
