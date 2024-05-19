import requests

def Request_OAuth(client_id, client_secret, redirect_uri, code, grant_type):
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'grant_type': grant_type,
        'redirect_uri': redirect_uri
    }

    response = requests.post('https://id.twitch.tv/oauth2/token', data=params)
    if response.ok: # Indicates if the HTTPS request was successful (status code 200-299 range)
        print('Request_OAuth -> '+ str(response.json()))  # Debugging line
        return response.json()
    else:
        print(f"Failed to fetch token. Status code: {response.status_code}, Response: {response.text}")  # Debugging line
        return None
    
def Request_User_Data(client_id, token, user_id=None):
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {token}'
    }
    param ={
        'id': user_id
    }

    response = requests.get('https://api.twitch.tv/helix/users', headers=headers, params=param)
    print('Request_User_Data -> ' + str(response.json()))
    if response.status_code == 200:
        return response.json()['data'][0]
    else:
        print(f"Failed to fetch user data. Status code: {response.status_code}")  # Debugging line
        return None

def Get_Followed_Channels(client_id, token, user_id, first=100, broadcaster_id=None):
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {token}'
    }

    params = {
        'user_id': user_id,
        'first': first,
        'broadcaster_id': broadcaster_id
    }

    channels = []

    while True:
        response = requests.get('https://api.twitch.tv/helix/channels/followed', headers=headers, params=params)
        data = response.json()

        if 'data' in data:
            channels.extend(data['data'])
        if 'pagination' in data and 'cursor' in data['pagination']:
            params['after'] = data['pagination']['cursor']
        else:
            break
       
    print('Get_Followed_Channels -> ' + str(channels))  # Debugging line

    if response.status_code == 200:
        return channels, response.json()['total'] #response.json()['data']
    else:
        print(f'Failed to fetch user followed channels. Status code: {response.status_code}')  # Debugging line
        return None

def Get_Channel_Followers(client_id, token, broadcaster_id, first=100):
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {token}'
    }

    params = {
        'broadcaster_id': broadcaster_id,
        'first': first
    }

    followers = []

    while True:
        response = requests.get('https://api.twitch.tv/helix/channels/followers', headers=headers, params=params)
        data = response.json()

        if 'data' in data:
            followers.extend(data['data'])
        if 'pagination' in data and 'cursor' in data['pagination']:
            params['after'] = data['pagination']['cursor']
        else:
            break

    print('Get_Channel_Followers -> ' + str(followers))  # Debugging line
       
    if response.status_code == 200:
        return followers, response.json()['total'] #response.json()['data']
    else:
        print(f'Failed to fetch user followers. Status code: {response.status_code}')  # Debugging line
        return None
    
