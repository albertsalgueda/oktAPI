import os

print('Testing User-related methods')
os.system('pytest test_users.py')
print('Testing campaign-related methods')
os.system('pytest test_campaign.py')

print('Testing completed.')