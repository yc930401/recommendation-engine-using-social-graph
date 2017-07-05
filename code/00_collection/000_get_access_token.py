from rauth import OAuth2Service
import config
import re
import webbrowser

# Get a real client_id and client_secret from:
# https://developer.foursquare.com/overview/auth#registration

foursquare = OAuth2Service(
    client_id=config.client_id,
    client_secret=config.client_secret,
    name='foursquare',
    authorize_url='https://foursquare.com/oauth2/authenticate',
    access_token_url='https://foursquare.com/oauth2/access_token',
    base_url='https://api.foursquare.com/v2/')

# This should redirect to your app, may function as a demo
# without updating, but be sure to update once you're done
# experimenting!
redirect_uri = 'http://localhost:8080'

params = {'response_type': 'token',
          'redirect_uri': redirect_uri}

authorize_url = foursquare.get_authorize_url(**params)

print ('Visit this URL in your browser: ' + authorize_url)
webbrowser.open(authorize_url);
