import os
from flask import Flask, redirect, session, request, url_for
from config import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, REDIRECT_URI, SCOPE, STATE
from calls import Request_OAuth, Request_User_Data, Get_Followed_Channels, Get_Channel_Followers

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
      # Ensure the state is in a URL-safe format
    session['oauth_state'] = STATE
    print(f"Generated state: {STATE}")  # Debugging line
    print(f"Session after setting state: {session}")  # Debugging line
    auth_url = (
        'https://id.twitch.tv/oauth2/authorize'
        f'?response_type=code&client_id={TWITCH_CLIENT_ID}'
        f'&redirect_uri={REDIRECT_URI}&scope={SCOPE}'
        f'&state={STATE}'
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')

    print(f"Received state: {state}, Code: {code}")  # Debugging line
    stored_state = session.get('oauth_state')
    print(f"Stored state: {stored_state}, Session: {session}")  # Debugging line

    if not code:
        return "Missing code parameter.", 400

    #Need to fix
    #if state != stored_state:
    #    return "Invalid state parameter.", 400

    token = Request_OAuth(
        TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET,
        grant_type='authorization_code',
        redirect_uri=REDIRECT_URI,
        code=code
    )
    if token and 'access_token' in token:
        user_data = Request_User_Data(TWITCH_CLIENT_ID, token['access_token'])
        if user_data:
            print('aqui user_data -> ' + str(user_data['id']))

            followed_channels_data, total_followed_channels = Get_Followed_Channels(TWITCH_CLIENT_ID, token['access_token'], user_data['id'])
            channel_list = [stream['broadcaster_name'] for stream in followed_channels_data]
            channel_string = '\n'.join(channel_list)
            
            channel_followers, total_channel_followers = Get_Channel_Followers(TWITCH_CLIENT_ID, token['access_token'], user_data['id'])
            followers_list = [followers['user_name'] for followers in channel_followers]
            followers_string = '\n'.join(followers_list)
            
            return f"""
            <p>Hello {user_data['login']}, {user_data.get('email', 'not provided')}</p>
            <p>You follow {total_followed_channels} channels:<br>{channel_string}</p>
            <p>You are followed by {total_channel_followers} channels:<br>{followers_string}</p>
            """
    return "Failed to retrieve user information."

if __name__ == '__main__':
    app.run(debug=True)
