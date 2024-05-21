import os
from flask import Flask, redirect, session, request, url_for
from config import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, REDIRECT_URI, SCOPE, STATE
from calls import Request_OAuth, Request_User_Data, Get_Streams, Get_Channel_Followers

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

    user_info_token = Request_OAuth(
        TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET,
        grant_type='client_credentials',
        redirect_uri=REDIRECT_URI,
        code=code
    )

    if token and 'access_token' in token:
        token = token['access_token']    
        user_data = Request_User_Data(TWITCH_CLIENT_ID, token=token)
        
        if user_data:
            #Who follows me
            channel_followers = Get_Channel_Followers(TWITCH_CLIENT_ID, token, user_data['id'])
            followers_list = [followers['user_name'] for followers in channel_followers]
            followers_string = '\n'.join(followers_list)
            
            #Who i follow
            followed_channels = Get_Streams(TWITCH_CLIENT_ID, token, user_data['id'], 'channels/followed')
            channel_list = [stream['broadcaster_name'] for stream in followed_channels]
            channel_string = '\n'.join(channel_list)
            
            #Streams that i follow that are live right now
            live_streams = Get_Streams(TWITCH_CLIENT_ID, token, user_data['id'], 'streams/followed')
            live_streams_list = [stream['user_name'] for stream in live_streams]
            live_streams_string = '\n'.join(live_streams_list)

            # for channel in followed_channels:
            #     data = Request_User_Data(TWITCH_CLIENT_ID, user_info_token['access_token'], user_id=channel['broadcaster_id'])
            #     channel['type'] = data['type']
            #     channel['broadcaster_type'] = data['broadcaster_type']
            #     channel['description'] = data['description']
            #     channel['profile_image_url'] = data['profile_image_url']
            #     channel['created_at'] = data['created_at']
            #     print('teste ->', data)


            return f"""
            <p>Hello {user_data['login']}, {user_data.get('email', 'not provided')}</p>
            <p>You follow {len(channel_list)} channels:<br>{channel_string}</p>
            <p>Only {len(live_streams_list)} are in live:<br>{live_streams_string}</p>
            <p>You are followed by {len(followers_list)} channels:<br>{followers_string}</p>
            """
        
    return "Failed to retrieve user information."

if __name__ == '__main__':
    app.run(debug=True)
