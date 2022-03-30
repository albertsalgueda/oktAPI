# How to run this app using python(3.10).


## Step 1.

### Add mongo connection string in utils/db_connector.py (in MongoClient())

## Step 2.

### pip install -r requirements.txt

## Step 3.

### python initialize.py

## Step 4.

### uvicorn fast:app (Make sure you are in OktAPI folder.)

## Step 5.

### Open the url with /api and login with admin/admin.

# DOCS

### /budget allocation 
{'budget allocation': state.budget:allocation }

### /next 
It requires nothing. 
It should return:
{'remaining budget': state.remaining, 'current time': state.current_time, 'budget allocation': state.budget:allocation }