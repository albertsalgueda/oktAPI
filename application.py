from flask import Flask

# print a nice greeting.
def say_hello(username = "dear username"):
    return '<p>Hello %s!</p>\n' % username

# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>OKTOPUS</title> </head>\n<body>'''
instructions = '''
    <p> This is the official oktopus.io API, read the documentation below </p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default.
application = Flask(__name__)

@application.route("/allocate")
def sample():
    campaigns = {
        1: 0.25, 
        2: 10.3, 
        3: 0.25,
        4: 0.2
    }
    return campaigns

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()