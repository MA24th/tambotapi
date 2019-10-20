import requests
import json



def _make_requests(token, make=None, verbs=None, method=None, chatid=None):
    '''
    HTTP verbs
        DELETE — deleting resources
        GET — getting resources, parameters are transmitted via URL
        PATCH — patching resources
        POST — creation of resources (for example, sending new messages)
        PUT — editing resources
    BOT method
        me
        chats 
            -chatid [Requested chat identifie]
        messages
        answers
        subscriptions
        updates
        upload
    '''
    if make == 'basic':
        base_url = 'https://botapi.tamtam.chat/{0}?access_token={1}'
        make_request = base_url.format(method, token)
        if verbs == 'delete':
            r = requests.delete(make_request)
            return _check_request(token, r, make, verbs)
        elif verbs == 'get':
            r = requests.get(make_request)
            return _check_request(token, r, make, verbs)
        elif verbs == 'patch':
            r = requests.patch(make_request)
            return _check_request(token, r, make, verbs)
        elif verbs == 'post':
            r = requests.post(make_request)
            return _check_request(token, r, make, verbs)
        elif verbs == 'put':
            r = requests.put(make_request)
            return _check_request(token, r, make, verbs)
        else:
            raise TypeError(f"verbs '{verbs}' type Error!!!")

    elif make == 'advns':
        base_url = 'https://botapi.tamtam.chat/{0}/{1}?access_token={2}'
        make_request = base_url.format(method, chatid, token)
        if verbs == 'delete':
            r = requests.delete(make_request)
            return _check_request(token, r, make, verbs)
        elif verbs == 'get':
            r = requests.get(make_request)
            return _check_request(token, r, make, verbs)
        elif verbs == 'patch':
            r = requests.patch(make_request)
            return _check_request(token, r, make, verbs)
        elif verbs == 'post':
            r = requests.post(make_request)
            return _check_request(token, r, make, verbs)
        elif verbs == 'put':
            r = requests.put(make_request)
            return _check_request(token, r, make, verbs)
        else:
            raise TypeError(f"verbs '{verbs}' type Error!!!")
    else:
        raise TypeError(f"make '{make}' type Error!!!")


def _check_request(token, r, make, verbs):
    '''
    param:HTTP response codes
        200 — successful operation
        400 — invalid request
        401 — authentication error
        404 — resource not found
        405 — method is not allowed
        429 — the number of requests is exceeded
        503 — service unavailable
    '''
    print(r.status_code)
    if r.status_code == 200:
        result_json = r.json()
        return result_json
    elif r.status_code == 400:
        raise TypeError(f"Invalid Request, make={make} verbs={verbs}!!!")
    elif r.status_code == 401:
        raise TypeError(f"Authentication Error, token={token}!!!")
    elif r.status_code == 404:
        raise ValueError(f"Resource not found!!!")
    elif r.status_code == 405:
        raise ValueError(f"Method is not allowed!!!")
    elif r.status_code == 429:
        raise RuntimeError("The number of requests is exceeded!!!")
    elif r.status_code == 503:
        raise RuntimeError("Service Unavailable!!!")
    else:
        raise ValueError('Error Unspecified!!!')


# bots
# Get current bot info
def get_me(token):
    '''
    HTTP_verbs='get'
    request_url='https://botapi.tamtam.chat/me'
    Returns info about current bot. 
    Current bot can be identified by access token. 
    Method returns bot identifier, name and avatar (if any)
    RESPONSE: application/json
        {
        user_id:(integer, users identifier),
        name:(sting, users visible name),
        username:(string, Unique public user name. Can be null if user is not accessible or it is not set),
        avatar_url:(optional, string, URL of avatar),
        full_avatar_url:(optional, string, URL of avatar of a bigger size),
        commands:(optional, array of object, commands supported by bot
                Array [
                    name:(strng [1..64]characters, command name) 
                    descripton:(optional, string [1..128]characters, command description)
                ]),
        description:(optional, sting <= 16000 characters, bot description)
        }
    '''
    return _make_requests(token, make='basic', verbs='get', method='me')