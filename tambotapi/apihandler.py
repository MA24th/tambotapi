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

logger = tambotapi.logger
proxy = None


def _get_req_session(reset=False):
    return util.per_thread('req_session', lambda: requests.session(), reset)


def _make_requests(token, make=None, verbs=None, method=None, chatId=None, params=None, files=None):
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
        request_url = base_url.format(method, token)
        logger.debug("Request: method={0} url={1} params={2} files={3}".format(
            method, request_url, params, files))
        result = _get_req_session().request(verbs, request_url, params=params, files=files,
                                            timeout=(connect_timeout, read_timeout), proxies=proxy)
        logger.debug("The server returned: '{0}'".format(
            result.text.encode('utf8')))
        return _check_request(result, method)

    elif make == 'chats':
        base_url = 'https://botapi.tamtam.chat/{0}/{1}?access_token={2}'
        request_url = base_url.format(method, chatId, token)
        logger.debug("Request: method={0} url={1} params={2} files={3}".format(
            method, request_url, params, files))
        result = _get_req_session().request(verbs, request_url, params=params, files=files,
                                            timeout=(connect_timeout, read_timeout), proxies=proxy)
        logger.debug("The server returned: '{0}'".format(
            result.text.encode('utf8')))
        return _check_request(result, method)

    else:
        raise TypeError(f"make '{make}' type Error!!!")


def _check_request(result, method):
    '''
    Checks whether `result` is a valid API response.
    A result is considered invalid if:
        - The server returned an HTTP response code other than 200
        - The content of the result is invalid JSON.
        - The method call was unsuccessful (The JSON 'ok' field equals False)

    :raises ApiException: if one of the above listed cases is applicable
     method: The name of the method called
     result: The returned result of the method request
    :return: The result parsed to a JSON dictionary.
    '''
    if result.status_code != 200:
        msg = 'The server returned HTTP {0} {1}. Response body:\n[{2}]' \
            .format(result.status_code, result.reason, result.text.encode('utf8'))
        raise ApiException(msg, method, result)

    try:
        result_dict = result.json()
    except:
        msg = 'The server returned an invalid JSON response. Response body:\n[{0}]' \
            .format(result.text.encode('utf8'))
        raise ApiException(msg, method, result)
    return result_dict


# _no_encode
def _no_encode(func):
    def wrapper(key, val):
        if key == 'filename':
            return u'{0}={1}'.format(key, val)
        else:
            return func(key, val)

    return wrapper

# ApiException


class ApiException(Exception):
    """
    This class represents an Exception thrown when a call to the TamTam API fails.
    In addition to an informative message, it has a `function_name` and a `result` attribute, which respectively
    contain the name of the failed function and the returned result that made the function to be considered  as
    failed.
    """

    def __init__(self, msg, function_name, result):
        super(ApiException, self).__init__(
            "A request to the TamTam API was unsuccessful. {0}".format(msg))
        self.function_name = function_name
        self.result = result


def get_bot_info(token):
    '''Get current bot info
    HTTP_verbs='get'
    request_url='https://botapi.tamtam.chat/me?access_token={}'
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
    connect_timeout = CONNECT_TIMEOUT
    read_timeout = READ_TIMEOUT
    verbs = r'get'
    method = r'me'
    base_url = 'https://botapi.tamtam.chat/{0}?access_token={1}'
    request_url = base_url.format(method, token)

    payload = None

    logger.debug("Request: method={0} url={1} params={2}".format(
        method, request_url, payload))
    result = _get_req_session().request(verbs, request_url, params=payload,
                                        timeout=(connect_timeout, read_timeout), proxies=proxy)
    logger.debug("The server returned: '{0}'".format(
        result.text.encode('utf8')))
    return _check_request(result, method)


def edit_bot_info(token, name=None, username=None, description=None, commands=None, photo=None):
    '''Edit current bot info
    HTTP_verbs='patch'
    request_url='https://botapi.tamtam.chat/me?access_token={}'
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
    connect_timeout = CONNECT_TIMEOUT
    read_timeout = READ_TIMEOUT
    verbs = r'patch'
    method = r'me'
    base_url = 'https://botapi.tamtam.chat/{0}?access_token={1}'
    request_url = base_url.format(method, token)

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

    logger.debug("Request: method={0} url={1} params={2}".format(
        method, request_url, payload))
    result = _get_req_session().request(verbs, request_url, params=payload,
                                        timeout=(connect_timeout, read_timeout), proxies=proxy)
    logger.debug("The server returned: '{0}'".format(
        result.text.encode('utf8')))
    return _check_request(result, method)


def get_chats(token, count=None, marker=None):
    '''get all chats
    HTTP_verbs='get'
    request_url='https://botapi.tamtam.chat/chats?access_token={}'
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
    connect_timeout = CONNECT_TIMEOUT
    read_timeout = READ_TIMEOUT
    verbs = r'patch'
    method = r'chats'
    base_url = 'https://botapi.tamtam.chat/{0}?access_token={1}'
    request_url = base_url.format(method, token)

    payload = {}
    if count:
        payload['count'] = count
    if marker:
        payload['marker'] = marker

    logger.debug("Request: method={0} url={1} params={2}".format(
        method, request_url, payload))
    result = _get_req_session().request(verbs, request_url, params=payload,
                                        timeout=(connect_timeout, read_timeout), proxies=proxy)
    logger.debug("The server returned: '{0}'".format(
        result.text.encode('utf8')))
    return _check_request(result, method)


def get_chat_info(token, chat_id):
    '''Get chat
    HTTP_verbs='get'
    request_url='https://botapi.tamtam.chat/chats/{chatId}?access_token={}'    
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
    connect_timeout = CONNECT_TIMEOUT
    read_timeout = READ_TIMEOUT
    verbs = r'get'
    method = r'chats'
    base_url = 'https://botapi.tamtam.chat/{0}/{1}?access_token={2}'
    request_url = base_url.format(method, chat_id, token)

    payload = None

    logger.debug("Request: method={0} url={1} params={2}".format(
        method, request_url, payload))
    result = _get_req_session().request(verbs, request_url, params=payload,
                                        timeout=(connect_timeout, read_timeout), proxies=proxy)
    logger.debug("The server returned: '{0}'".format(
        result.text.encode('utf8')))
    return _check_request(result, method)


def edit_chat_info(token, chat_id, icon, title):
    '''Edit chat info
    HTTP_verbs='patch'
    request_url='https://botapi.tamtam.chat/chats/{chatId}?access_token={}'    
    Edits chat info: title, icon, etc…
    PATH PARAMETERS: application/json
    {
        chatId:(integer, requested chat identifer)
    }
    REQUEST BODY SCHEMA: application/json
    {
        icon:(optional, object, Request to attach image. All fields are mutually exclusive
            url:(optional, string, any external image url you want to attach)
            token:(optional, string, token of any existing attachment)
            photos:(optional, object, token were obtained after uploading images
                property_name:(optional, object
                    token:(string, Encoded information of uploaded imager))))
        title:(optional, string [1..200]characters)
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
    connect_timeout = CONNECT_TIMEOUT
    read_timeout = READ_TIMEOUT
    verbs = r'patch'
    method = r'chats'
    base_url = 'https://botapi.tamtam.chat/{0}/{1}?access_token={2}'
    request_url = base_url.format(method, chat_id, token)

    payload = {}
    if icon:
        payload['icon'] = icon
    if title:
        payload['title'] = title

    logger.debug("Request: method={0} url={1} params={2}".format(
        method, request_url, payload))
    result = _get_req_session().request(verbs, request_url, params=payload,
                                        timeout=(connect_timeout, read_timeout), proxies=proxy)
    logger.debug("The server returned: '{0}'".format(
        result.text.encode('utf8')))
    return _check_request(result, method)


def send_chat_action(token, chat_id, action):
    '''Send Action
    HTTP_verbs='post'
    request_url='https://botapi.tamtam.chat/chats/{chatId}/actions?access_token={}'    
    send bot action to chat
    PATH PARAMTERS: application/json
    {
        chatId:(integer, chat identifer)
    }
    REQUEST BODY SCHEMA: application/json
    {
        action:(any, Enum:'typing_on', 'sending_photo', 'sending_video', 'sending_audio', 'sending_file', 'mark_seen'. different actions to send to chat members)
    }
    RESPONSE: application/json
    {
        success:(boolean, true if request was successful. false otherwise)
        message:(optional, string, explanatory message if the result is not succesful)
    }
    '''
    connect_timeout = CONNECT_TIMEOUT
    read_timeout = READ_TIMEOUT
    verbs = r'post'
    method = r'chats'
    base_url = 'https://botapi.tamtam.chat/{0}/{1}/action?access_token={2}'
    request_url = base_url.format(method, chat_id, token)

    payload = {'action': str(action)}

    logger.debug("Request: method={0} url={1} params={2}".format(
        method, request_url, payload))
    result = _get_req_session().request(verbs, request_url, params=payload,
                                        timeout=(connect_timeout, read_timeout), proxies=proxy)
    logger.debug("The server returned: '{0}'".format(
        result.text.encode('utf8')))
    return _check_request(result, method)


def get_chat_membership(token, chat_id):
    '''Get Chat Membership
    HTTP_verbs='get'
    request_url='https://botapi.tamtam.chat/chats/{chatId}/members/me?access_token={}'    
    returns chat membership info for current bot
    PATH PARAMTERS: application/json
    {
        chatId:(integer, chat identifier)
    }
    RESPONSE: application/json
    {
        user_id:(intger, user identifier)
        name:(string, user visible name)
        username:(string, Unique public user name. Can be null if user is not accessible or it is not set)
        avatar_url:(optional, string, URL of avatar)
        full_avatar_url:(optional, string, URL of avatar of a bigger size)
        last_access_time:(integer)
        is_owner:(boolean)
        is_admin:(boolean)
        join_time:(integer)
        permissions:(array of string, items Enum: 'read_all_messages', 'add_remove_members', 'add_admins', 'change_chat_info', 'pin_message', 'write'. permissions in chat if member is admin. null otherwise)
    }    
    '''
    connect_timeout = CONNECT_TIMEOUT
    read_timeout = READ_TIMEOUT
    verbs = r'get'
    method = r'chats'
    base_url = 'https://botapi.tamtam.chat/{0}/{1}/members/me?access_token={2}'
    request_url = base_url.format(method, chat_id, token)

    payload = None

    logger.debug("Request: method={0} url={1} params={2}".format(
        method, request_url, payload))
    result = _get_req_session().request(verbs, request_url, timeout=(
        connect_timeout, read_timeout), parmas=payload, proxies=proxy)
    logger.debug("The server returned: '{0}'".format(
        result.text.encode('utf8')))
    return _check_request(result, method)


def leave_chat(token, chat_id):
    '''leave chat
    HTTP_verbs='delete'
    request_url='https://botapi.tamtam.chat/chats/{chatId}/members/me?access_token={}'    
    Removes bot from chat members.
    PATH PARAMTERS: application/json
    {
        chatId:(integer, chat identifier)
    }
    RESPONSE: application/json
    {
        success:(boolean, true if request was successful, false otherwise)
        message:(optional, string, explanatory message if the result is not successful)
    }    
    '''
    connect_timeout = CONNECT_TIMEOUT
    read_timeout = READ_TIMEOUT
    verbs = r'delete'
    method = r'chats'
    base_url = 'https://botapi.tamtam.chat/{0}/{1}/members/me?access_token={2}'
    request_url = base_url.format(method, chat_id, token)

    payload = None

    logger.debug("Request: method={0} url={1} params={2}".format(
        method, request_url, payload))
    result = _get_req_session().request(verbs, request_url, timeout=(
        connect_timeout, read_timeout), params=payload, proxies=proxy)
    logger.debug("The server returned: '{0}'".format(
        result.text.encode('utf8')))
    return _check_request(result, method)


def get_chat_admins(token, chat_id):
    '''Get chat admins
    HTTP_verbs='get'
    request_url='https://botapi.tamtam.chat/chats/{chatId}/members/admins?access_token={}'    
    Returns all chat administrators. Bot must be adminstrator in requested chat.
    PATH PARAMTERS: application/json
    {
        chatId:(integer, chat identifier)
    }
    RESPONSE: application/json
    {
        members:(array of object, Participants in chat with time of last activity. Visible only for chat admins
            Array [
                user_id:(integer, users identifier)
                name:(string, users visible name)
                username,(string, Unique public user name. Can be null if user is not accessible or it is not set)
                avatar_url:(string, url of avatar)
                full_avatar_url:(string, URL of avatar of a bigger size)
                last_access_time:(integer)
                is_owner:(boolean)
                is_admin:(boolean)
                join_time:(integer)
                permissions:(array of string, items Enum: 'read_all_messages', 'add_remove_members', 'add_admins', 'change_chat_info', 'pin_message', 'write'. permissions in chat if member is admin. null otherwise)

            ])
        marker:(optional, integer, Pointer to the next data page)
    }    
    '''
    connect_timeout = CONNECT_TIMEOUT
    read_timeout = READ_TIMEOUT
    verbs = r'get'
    method = r'chats'
    base_url = 'https://botapi.tamtam.chat/{0}/{1}/members/admins?access_token={2}'
    request_url = base_url.format(method, chat_id, token)

    payload = None

    logger.debug("Request: method={0} url={1} params={2}".format(
        method, request_url, payload))
    result = _get_req_session().request(verbs, request_url, timeout=(
        connect_timeout, read_timeout), params=payload, proxies=proxy)
    logger.debug("The server returned: '{0}'".format(
        result.text.encode('utf8')))
    return _check_request(result, method)


def get_members(token, chat_id, user_ids=None, marker=None, count=None):
    '''Get members
    HTTP_verbs='get'
    request_url='https://botapi.tamtam.chat/chats/{chatId}/members?access_token={}'    
    Returns users participated in chat.
    PATH PARAMTERS: application/json
    {
        chatId:(integer, chat identifier)
    }
    QUERY PARAMETERS:
    {
        user_ids:(optional, array of integer, Comma-separated list of users identifiers to get their membership. When this parameter is passed, both count and marker are ignored)
        marker:(optional, integer, Marker)
        count:(optional, integer [1..100], default '20', count)
    }
    RESPONSE: application/json
    {
        members:(array of object, Participants in chat with time of last activity. Visible only for chat admins
            Array [
                user_id:(integer, users identifier)
                name:(string, users visible name)
                username,(string, Unique public user name. Can be null if user is not accessible or it is not set)
                avatar_url:(string, url of avatar)
                full_avatar_url:(string, URL of avatar of a bigger size)
                last_access_time:(integer)
                is_owner:(boolean)
                is_admin:(boolean)
                join_time:(integer)
                permissions:(array of string, items Enum: 'read_all_messages', 'add_remove_members', 'add_admins', 'change_chat_info', 'pin_message', 'write'. permissions in chat if member is admin. null otherwise)

            ])
        marker:(optional, integer, Pointer to the next data page)
    }    
    '''
    connect_timeout = CONNECT_TIMEOUT
    read_timeout = READ_TIMEOUT
    verbs = r'get'
    method = r'chats'
    base_url = 'https://botapi.tamtam.chat/{0}/{1}/members?access_token={2}'
    request_url = base_url.format(method, chat_id, token)

    payload = {}
    if user_ids:
        payload['user_ids'] = user_ids
    if marker:
        payload['marker'] = marker
    if count:
        payload['count'] = count

    logger.debug("Request: method={0} url={1} params={2}".format(
        method, request_url, payload))
    result = _get_req_session().request(verbs, request_url, params=payload,
                                        timeout=(connect_timeout, read_timeout), proxies=proxy)
    logger.debug("The server returned: '{0}'".format(
        result.text.encode('utf8')))
    return _check_request(result, method)


def add_members(token, chat_id, user_ids):
    '''Add members
    HTTP_verbs='post'
    request_url='https://botapi.tamtam.chat/chats/{chatId}/members?access_token={}'    
    Adds members to chat. Additional permissions may require.
    PATH PARAMTERS: application/json
    {
        chatId:(integer, chat identifier)
    }
    REQUEST BODY SCHEMA:
    {
        user_ids:(array of integer, Comma-separated list of users identifiers)
    }
    RESPONSE: application/json
    {
        success:(boolean, true if request was successful. false otherwis)
        message:(optional, string, Explanatory message if the result is not successful)
    }    
    '''
    connect_timeout = CONNECT_TIMEOUT
    read_timeout = READ_TIMEOUT
    verbs = r'post'
    method = r'chats'
    base_url = 'https://botapi.tamtam.chat/{0}/{1}/members?access_token={2}'
    request_url = base_url.format(method, chat_id, token)

    payload = {'user_ids': user_ids}

    logger.debug("Request: method={0} url={1} params={2}".format(
        method, request_url, payload))
    result = _get_req_session().request(verbs, request_url, params=payload,
                                        timeout=(connect_timeout, read_timeout), proxies=proxy)
    logger.debug("The server returned: '{0}'".format(
        result.text.encode('utf8')))
    return _check_request(result, method)


def remove_member(token, chat_id, user_id):
    '''Remove member
    HTTP_verbs='delete'
    request_url='https://botapi.tamtam.chat/chats/{chatId}/members?access_token={}'    
    Removes member from chat. Additional permissions may require.
    PATH PARAMTERS: application/json
    {
        chatId:(integer, chat identifier)
    }
    QUERY PARAMETERS:
    {
        user_id:(integer, user id to remove from chat)
    }
    RESPONSE: application/json
    {
        success:(boolean, true if request was successful. false otherwis)
        message:(optional, string, Explanatory message if the result is not successful)
    }    
    '''
    connect_timeout = CONNECT_TIMEOUT
    read_timeout = READ_TIMEOUT
    verbs = r'delete'
    method = r'chats'
    base_url = 'https://botapi.tamtam.chat/{0}/{1}/members?access_token={2}'
    request_url = base_url.format(method, chat_id, token)

    payload = {'user_id': user_id}

    logger.debug("Request: method={0} url={1} params={2}".format(
        method, request_url, payload))
    result = _get_req_session().request(verbs, request_url, params=payload,
                                        timeout=(connect_timeout, read_timeout), proxies=proxy)
    logger.debug("The server returned: '{0}'".format(
        result.text.encode('utf8')))
    return _check_request(result, method)


def get_messages(token, chat_id=None, message_ids=None, chat_from=None, to=None, count=None):
    '''Get messages
    HTTP_verbs='get'
    request_url='https://botapi.tamtam.chat/messages?access_token={}'    
    Returns messages in chat: result page and marker referencing to the next page. 
    Messages traversed in reverse direction so the latest message in chat will be first in result array. 
    Therefore if you use 'from' and 'to' parameters, 'to' must be less than 'from'
    QUERY PARAMETERS:
    {
        chat_id:(optional, integer, chat identifier to get messages in chat)
        message_ids:(optional, array of string, comma-separated list of message ids to get)
        from:(optional, integer, start time for requested messages)
        to:(optional, integer, end time for requested messages)
        count:(optional, integer [1..100], maximum amount of messages in response)
    }
    RESPONSE: application/json
    {
        messages:(array of object, list of messages
            Array [
                sender:(optional, object, user who sent this message, can be null if message has been posted on behalf of a channel
                    user_id:(integer, user identifier)
                    name:(string, users visible name)
                    username:(string, unique public user name. can be null if user is not accessible or it is not set))
                recipient:(object, message recipient, could be user of chat
                    chat_id:(integer, chat identifier)
                    chat_type:(any, Enum:'dialog', 'chat', 'channel', chat type)
                    user_id:(user identifier, if message was sent to user))
                timestamp:(integer, Unix-time when message was created)
                link:(optional, object, forwarder or replied message
                    type:(string, Enum: 'forward', 'reply', type of linked message)
                    sender:(optional, object, user sent this message. can be null if message has been posted on behalf of a channel
                        user_id:(integer, users identifier)
                        name:(string, users visible name)
                        username:(string, Unique public user name. Can be null if user is not accessible or it is not set)))
                    chat_id:(optional, integer, Chat where message has been originally posted. For forwarded messages only)
                    message:(object, schema representing body of message
                        mid:(string, Unique identifier of message)
                        seq:(integer, Sequence identifier of message in chat)
                        text:(string, message text)
                        attachments:(array of object, Message attachments. Could be one of Attachment type. can be image, video, audio, file, contact, sticker, share, location, inline_keyboard)
                        reply_to:(Deprected, optional, string, in case this message is reply to another, it is the unique identifier of the replied message)))   
                body:(bject, Body of created message. Tex + attachments. could be null if message contains only forwarded message)
                stat:(optional, object, message statics. available only for channels in GET:/message context)
                url:(optional, string, message public url, can be null for dialogs or non-public chats/channel)]
    } 
    '''
    connect_timeout = CONNECT_TIMEOUT
    read_timeout = READ_TIMEOUT
    verbs = r'get'
    method = r'messages'
    base_url = 'https://botapi.tamtam.chat/{0}?access_token={1}'
    request_url = base_url.format(method, token)

    payload = {}
    if chat_id:
        payload['chatId'] = chat_id
    if message_ids:
        payload['message_ids'] = message_ids
    if chat_from:
        payload['from'] = chat_from
    if to:
        payload['to'] = to
    if count:
        payload['count'] = count

    logger.debug("Request: method={0} url={1} params={2}".format(
        method, request_url, payload))
    result = _get_req_session().request(verbs, request_url, params=payload,
                                        timeout=(connect_timeout, read_timeout), proxies=proxy)
    logger.debug("The server returned: '{0}'".format(
        result.text.encode('utf8')))
    return _check_request(result, method)
