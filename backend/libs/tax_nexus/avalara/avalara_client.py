from avalara import AvataxClient
from settings.minimal import env

AVALARA_USERNAME = env.str('AVALARA_USERNAME', default='FAKE')
AVALARA_PASSWORD = env.str('AVALARA_PASSWORD', default='FAKE')
AVALARA_ENVIRONMENT = env.str('AVALARA_ENVIRONMENT', default='sandbox')

AvalaraClient = AvataxClient("tinydotcom", "1.0", '', AVALARA_ENVIRONMENT)\
    .add_credentials(AVALARA_USERNAME, AVALARA_PASSWORD)
