# OptimAI 1.1.1

### Common

There is a class to add details on errors messages. ( I don't thing it has been used )

### Models

Classes for database. 

### Routers

Create API endpoints

### Fast.py

Import all the routers, and run the FastAPi

### initialize.py

We create an admin user. 

### main.py

Contains main logic of the program: Campaign(), State() and AI() classes.

# How to run this app using python(3.10).

## Step 1.

Add mongo connection string in utils/db_connector.py (in MongoClient())

## Step 2.

pip install -r requirements.txt

## Step 3.

python initialize.py

## Step 4.

uvicorn fast:app (Make sure you are in OktAPI folder.)

## Step 5.

Open the url with /api and login with admin/admin.
