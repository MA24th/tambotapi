import requests
import json

try:
    from requests.packages.urllib3 import fields

    format_header_param = fields.format_header_param
except ImportError:
    format_header_param = None

import tambotapi
#from tambotapi import types
from tambotapi import util

CONNECT_TIMEOUT = 3.5
READ_TIMEOUT = 9999
proxy = None


def _get_req_session(reset=False):
    return util.per_thread('req_session', lambda: requests.session(), reset)


def _make_requests(token, make=None, method=None, chatId=None,  verbs=None, params=None, files=None):
    '''
    Makes a request to the TamTam API.
    token: The bot's API token. (Created with @PrimeBot)
    make:
        -basic: base_url = 'https://botapi.tamtam.chat/{0}?access_token={1}'
        -chats: 'https://botapi.tamtam.chat/{0}/{1}?access_token={2}'
            -chadId chats: identifier
    HTTP verbs:
        -delete: deleting resources
        -get: getting resources, parameters are transmitted via URL
        -patch: patching resources
        -post: creation of resources (for example, sending new messages)
        -put: editing resources
    BOT method: Name of the API method to be called
        me
        chats 
            -chatid [Requested chat identifie]
        messages
        answers
        subscriptions
        updates
        upload
    params: Optional parameters. Should be a dictionary with key-value pairs.
    files: Optional files.
    :return: The result parsed to a JSON dictionary.
    '''
    read_timeout = READ_TIMEOUT
    connect_timeout = CONNECT_TIMEOUT
    if files and format_header_param:
        fields.format_header_param = _no_encode(format_header_param)
    if params:
        if 'timeout' in params:
            read_timeout = params['timeout'] + 10
        if 'connect-timeout' in params:
            connect_timeout = params['connect-timeout'] + 10

    if make == 'basic':
        base_url = 'https://botapi.tamtam.chat/{0}?access_token={1}'
        make_request = base_url.format(method, token)
        r = _get_req_session().request(verbs, make_request, params=params, files=files,
                                       timeout=(connect_timeout, read_timeout), proxies=proxy)
        return _check_request(token, r, make, verbs)

    elif make == 'chats':
        base_url = 'https://botapi.tamtam.chat/{0}/{1}?access_token={2}'
        make_request = base_url.format(method, chatId, token)
        r = _get_req_session().request(verbs, make_request, params=params, files=files,
                                       timeout=(connect_timeout, read_timeout), proxies=proxy)
        return _check_request(token, r, make, verbs)
        
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

# _no_encode


def _no_encode(func):
    def wrapper(key, val):
        if key == 'filename':
            return u'{0}={1}'.format(key, val)
        else:
            return func(key, val)

    return wrapper

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
    return _make_requests(token, make='basic', method='me', verbs='get')

# Edit current bot info


def patch_me(token, name=None, username=None, description=None, commands=None, photo=None):
    '''
    HTTP_verbs='patch'
    request_url='https://botapi.tamtam.chat/me'
    Edits current bot info. 
    Fill only the fields you want to update. 
    All remaining fields will stay untouched
    REQUEST BODY SCHEMA: application/json
        {
        'name':(optional, string [1..64]characters, Visible name of bot)
        'username':(optional, string [4..64]characters, Bot unique identifier. It can be any string 4-64 characters long containing any digit, letter or special symbols: "-" or "_". It must starts with a letter )
        'description':(optional, string [1..16000]characters, Bot description up to 16k characters long)
        'commands:(optional, array of object, Commands supported by bot. Pass empty list if you want to remove commands
            Array [
                name: string [ 1 .. 64 ]characters, Command name
                description: optional, string [1..128]characters Optional command description
                ])
        'photo':(optional, object, Request to set bot photo
            'url':(optional, string, Any external image URL you want to attach)
            'token':(optional string, Nullable Token of any existing attachment)
            'photos':(optional, object, Tokens were obtained after uploading images
               'property name':(optional, object photo token
                    'token':(string, Encoded information of uploaded image))))
        }
    RESPONSE: application/json
    {
        user_id:(intger, user identifier)
        name:(string, user visible name)
        username:(string, Unique public user name. Can be null if user is not accessible or it is not set)
        avatar_url:(optional, string, URL of avatar)
        full_avatar_url:(optional, string, URL of avatar of a bigger size)
        commands:(optional, array of object, commands supported by bot
            Array [
                name:(string [1..64]characters, command name)
                description:(optional, string [1..128]characters, command description)
            ])
        description:(optional, string <= 16000 characers, bot description)
    }
    '''
    payload = {}
    if name:
        payload['name'] = name
    if username:
        payload['username'] = username
    if description:
        payload['description'] = description
    if commands:
        payload['commands'] = commands
    if photo:
        payload['photo'] = photo
    return _make_requests(token, make='basic', method='me', verbs='patch', params=payload)


# Chats
# get all chats
def get_chats(token, count=None, marker=None):
    '''
    HTTP_verbs='get'
    request_url='https://botapi.tamtam.chat/chats'
    Returns information about chats that bot participated in: 
        a result list and marker points to the next page
    QUERY PARAMETERS: application/json
    {
        count:(optional, integer [1..100] default 50, numaber of chats requested)
        marker:(optional, integer, points to next data page, null for the first page)
    }
    RESPONSE: application/json
    {
        chats:(array of object, list of requested chats
            Array[
                chat_id:(integer, chats identifier)
                type:(any, Enum:'dialog','chat','channel', type of chat, one of:dialog, chat, channel)
                status:(any, Enum:'active', 'removed', 'left', 'closed', 'suspended', chat status one of: active: bot is active member of chat, removed: bot was kicked, left: bot intentionally left chat, closed: chat was closed)
                title:(string, visible title of chat, can be null for dialogs)
                icon:(object, icon of chat
                    url:(string, url of image))
                last_event_time:(integer, time of last event occurred if chat)
                participants_count:(integer, number of people in chat, always 2 for dialog chat type)
                owner_id:(optional, integer, identifier of chat owner, visible only for chat admins)
                participants:(optional, object, participants in chat with time of last activity, can be null when you request list of chats, visible for chat admins only
                    property_name:(optional, integer))
                is_puplic:(boolean, is current chat publicly availabel, always false for dialogs)
                link:(optional, string, link of chat if it is public)
                description:(any, chat description)
                dialog_with_user:(optional, object, another user in conversation for dialog type chats only
                    user_id:(integer, users identifier)
                    name:(string, users visible name)
                    username:(string, Unique public user name. Can be null if user is not accessible or it is not set)
                    avatar_url:(optional, string, url of avatar)
                    full_avatar_url:(optional, string, url of avatar of a bigger size)    
                    )])
        marker:(integer, Reference to the next page of requested chats)
    }
    '''
    payload = {}
    if count:
        payload['count'] = count
    if marker:
        payload['marker'] = marker
    return _make_requests(token, make='basic', method='chats', verbs='get', params=payload)

# get chat


def get_chat(token, chat_id):
    '''
    HTTP_verbs='get'
    request_url='https://botapi.tamtam.chat/chats/{chatId}'    
    Returns info about chat.
    PATH PARAMETERS: application/json
    {
        chatId:(integer, requested chat identifer)
    }
    RESPONES: application/json
    {
        chat_id:(integer, chat identifer)
        type:(any, Enum:'dialog', 'chat, 'channel', type of chat one of:)
        status:(any, Enum:'active', 'removed', 'left', 'closed', 'suspended', chat status: active:bot is active member of chat, removed:bot was kicked, left:bot intentionallly left chat, closed:chat was closed)
        title:(string, visible title of chat, can be null for dialogs)
        icon:(object, icon of chat
            url:(string, url of image))
        last_event_time:(integer, time of last event occurred if chat)
        participants_count:(integer, number of people in chat, always 2 for dialog chat type)
        owner_id:(optional, integer, identifier of chat owner, visible only for chat admins)
        participants:(optional, object, participants in chat with time of last activity, can be null when you request list of chats, visible for chat admins only
            property_name:(optional, integer))
        is_puplic:(boolean, is current chat publicly availabel, always false for dialogs)
        link:(optional, string, link of chat if it is public)
        description:(any, chat description)
        dialog_with_user:(optional, object, another user in conversation for dialog type chats only
            user_id:(integer, users identifier)
            name:(string, users visible name)
            username:(string, Unique public user name. Can be null if user is not accessible or it is not set)
            avatar_url:(optional, string, url of avatar)
            full_avatar_url:(optional, string, url of avatar of a bigger size))

    }
    '''
    return _make_requests(token, make='chats', method='chats', chatId=chat_id, verbs='get')


print(get_me(token=r''))
# get_chat(token=r'', 12334)
