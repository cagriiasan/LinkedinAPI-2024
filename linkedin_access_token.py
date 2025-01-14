import json
import random
import requests
import string
from urllib.parse import urlparse, parse_qs

def auth(credentials):
    creds = read_creds(credentials)
    client_id, client_secret = creds['client_id'], creds['client_secret']
    redirect_uri = creds['redirect_uri']
    api_url = 'https://www.linkedin.com/oauth/v2'

    if 'access_token' not in creds.keys():
        args = client_id, client_secret, redirect_uri
        auth_code = authorize(api_url, *args)
        access_token = refresh_token(auth_code, *args)
        creds.update({'access_token': access_token})
        save_token(credentials, creds)
    else:
        access_token = creds['access_token']
        print("Access Token found in credentials.json:", access_token)  

    return access_token

def headers(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'cache-control': 'no-cache',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    return headers

def read_creds(filename):
    with open(filename) as f:
        credentials = json.load(f)
    return credentials

def save_token(filename, data):
    data = json.dumps(data, indent=4)
    with open(filename, 'w') as f:
        f.write(data)

def create_CSRF_token():
    letters = string.ascii_lowercase
    token = ''.join(random.choice(letters) for i in range(20))
    return token

def open_url(url):
    import webbrowser
    print(url)
    webbrowser.open(url)

def authorize(api_url, client_id, client_secret, redirect_uri):
    csrf_token = create_CSRF_token()
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': csrf_token,
        'scope': 'openid,profile,w_member_social,email'
    }

    response = requests.get(f'{api_url}/authorization', params=params)

    open_url(response.url)

    redirect_response = input('Paste the full redirect URL here:')
    auth_code = parse_redirect_uri(redirect_response)
    return auth_code

def parse_redirect_uri(redirect_response):
    url = urlparse(redirect_response)
    query = parse_qs(url.query)
    if 'code' in query:
        return query['code'][0]
    else:
        raise ValueError('Authorization code not found in the redirect URL.')

def refresh_token(auth_code, client_id, client_secret, redirect_uri):
    access_token_url = 'https://www.linkedin.com/oauth/v2/accessToken'

    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(access_token_url, data=data, timeout=30)
    if response.ok:
        response_data = response.json()
        access_token = response_data.get('access_token')
        if access_token:
            return access_token
        else:
            raise ValueError('Access token not found in the response.')
    else:
        response.raise_for_status()

if __name__ == '__main__':
    credentials = r".\credentials.json"
    access_token = auth(credentials)
