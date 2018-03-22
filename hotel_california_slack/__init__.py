from os import environ
from time import sleep
from typing import Dict, Union

from slackclient import SlackClient

_SLACK_BOT_TOKEN = environ["SLACK_BOT_TOKEN"]
_SLACK_OAUTH_TOKEN = environ["SLACK_OAUTH_TOKEN"]
_CHANNEL_CACHE = {}
_USER_CACHE = {}
_SLACK_BOT_CLIENT = SlackClient(_SLACK_BOT_TOKEN)
_SLACK_OAUTH_CLIENT = SlackClient(_SLACK_OAUTH_TOKEN)
_VALID_CHANNELS = ['hotel-california', 'hotel-california-test']


def get_channel_info(channel: str) -> Union[Dict, None]:
    channel_info = None
    channel_resp = _SLACK_BOT_CLIENT.api_call("channels.info", channel=channel)

    if channel_resp.get('ok'):
        channel_info = channel_resp.get('channel')

    return channel_info


def get_group_info(channel: str) -> Union[Dict, None]:
    group_info = None
    group_resp = _SLACK_BOT_CLIENT.api_call("groups.info", channel=channel)

    if group_resp.get('ok'):
        group_info = group_resp.get('group')

    return group_info


def get_user_info(user: str) -> Union[Dict, None]:
    user_info = None
    user_resp = _SLACK_BOT_CLIENT.api_call("users.info", user=user)

    if user_resp.get('ok'):
        user_info = user_resp.get('user')

    return user_info


def invite_user(user: str, channel: str, channel_type: str):
    if channel_type == 'C':
        _SLACK_OAUTH_CLIENT.api_call("channels.invite", channel=channel, user=user)
    elif channel_type == 'G':
        _SLACK_OAUTH_CLIENT.api_call("groups.invite", channel=channel, user=user)


def lookup_channel(channel: str, channel_type: str) -> Union[str, None]:
    channel_name = None

    if channel not in _CHANNEL_CACHE:

        if channel_type == 'C':
            channel_info = get_channel_info(channel)
            if channel_info:
                channel_name = channel_info.get('name')

        elif channel_type == 'G':
            channel_info = get_group_info(channel)
            if channel_info:
                channel_name = channel_info.get('name')

        if channel_name:
            _CHANNEL_CACHE[channel] = channel_name
    else:
        channel_name = _CHANNEL_CACHE[channel]

    return channel_name


def lookup_user(user: str) -> Union[str, None]:
    user_name = None

    if user not in _USER_CACHE:

        user_info = get_user_info(user)
        if user_info:
            user_name = user_info.get('name')

        if user_name:
            _USER_CACHE[user] = user_name
    else:
        user_name = _USER_CACHE[user]

    return user_name


def member_joined(event: Dict):
    channel = event.get('channel')
    channel_type = event.get('channel_type')
    user = event.get('user')

    if not channel:
        return
    channel_name = lookup_channel(channel, channel_type)

    if channel_name in _VALID_CHANNELS:
        _SLACK_BOT_CLIENT.rtm_send_message(channel_name, '<@{}>, welcome to the Hotel California'.format(user))


def member_left(event: Dict):
    channel = event.get('channel')
    channel_type = event.get('channel_type')
    user = event.get('user')

    if not channel:
        return
    channel_name = lookup_channel(channel, channel_type)

    if channel_name in _VALID_CHANNELS:
        invite_user(user, channel, channel_type)
        _SLACK_BOT_CLIENT.rtm_send_message(channel_name, '<@{}>, "You can check out any time you like, but you can '
                                                         'never leave!"'.format(user))


def main():
    if _SLACK_BOT_CLIENT.rtm_connect(auto_reconnect=True):
        while True:
            for event in _SLACK_BOT_CLIENT.rtm_read():
                event_type = event.get('type')
                if event_type == 'member_joined_channel':
                    member_joined(event)
                elif event_type == 'member_left_channel':
                    member_left(event)
            sleep(1)

    else:
        print("Connection Failed")
