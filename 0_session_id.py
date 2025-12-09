import methods
from simple_salesforce import SalesforceLogin

#Init client
env = 'preview'
sf_credentials = methods.load_credentials(env)

session_id, instance = SalesforceLogin(
    username=sf_credentials['user'],
    password=sf_credentials['password'],
    security_token=sf_credentials['token'],
    domain='test')

print(session_id)
