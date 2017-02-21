import json, requests

from . import config as c
from . import hub

cloudBase='https://cloud2.cozify.fi/ui/0.2/'

# auth flow based on and storing into config
# email -> OTP -> remoteToken -> hub ip -> hubToken
def authenticate():
    email = c.config['Cloud']['email']
    if _needAuth():
        if _requestlogin(email):
            otp = _getotp()
            remoteToken = _emaillogin(email, otp)
            if remoteToken is not None:
                c.ephemeral['Cloud']['remoteToken'] = remoteToken
                c.ephemeralWrite()
                hubIp = _lan_ip(remoteToken)
                if hubIp is not None:
                    hub = hub._hub(remoteToken, hubIp)
                    if hub is not None:
                        hubId = hub['hubId']
                        hubName = hub['name']
                        hubkeys = _hubkeys(remoteToken)
                        if hubKeys is not None:
                            hubToken = hubKeys[hubId]
                            if hubToken:
                                c.ephemeral['Hub'][hubName]['hubToken'] = hubToken



            else:
                # either API error or wrong OTP
                return False
        else:
            # for this request to fail either there's an API error
            # or we're pushing the wrong email
            return False



# determine if current hub-key is valid
# TODO(artanicus): needs implementation, and logic planning
def _needAuth():
    return c.ephemeral['Cloud']['remoteToken'] is not None

def _getotp():
    return input('OTP from your email: ')

# 1:1 implementation of user/requestlogin
# email: cozify account email
# returns success Bool
def _requestlogin(email):
    payload = { 'email': email }
    response = requests.post(cloudBase + 'user/requestlogin', params=payload)
    print(response.url)
    if response.status_code == 200:
        return True
    else:
        print(response.text)
        return False

# 1:1 implementation of user/emaillogin
# email: cozify account email
# otp: OTP provided by user, generated by requestlogin
# returns remote-key or None on failure
def _emaillogin(email, otp):
    payload = {
            'email': email,
            'password': otp
    }

    response = requests.post(cloudBase + 'user/emaillogin', params=payload)
    print(response.url)
    if response.status_code == 200:
        return response.text
    else:
        print(response.text)
        return None

# 1:1 implementation of hub/lan_ip
# remoteToken: cozify Cloud remoteToken
# returns list of hub ip's or None
def _lan_ip(remoteToken):
    headers = {
            'Authorization': remoteToken
    }

    response = requests.get(cloudBase + 'hub/lan_ip', headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(response.text)
        return None

# 1:1 implementation of user/hubkeys
# remoteToken: cozify Cloud remoteToken
# returns map of hubs: { hubId: hubToken }
def _hubkeys(remoteToken):
    headers = {
            'Authorization': remoteToken
    }

    response = requests.get(cloudBase + 'user/hubkeys', headers=headers)
    if response.status_code == 200:
        return json.loads(response.json)
    else:
        print(response.text)
        return None