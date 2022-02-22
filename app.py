#API File

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
   return "This is oktopus.io APIs"

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5000)

# https://aws.amazon.com/getting-started/hands-on/serve-a-flask-app/
