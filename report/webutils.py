# -*- coding: utf-8 -*-

import requests
import json
import logutils

BASE_URL = 'https://api.trello.com/1'
BOARD_ID = '524adf089e1491f3360008c8'
CLOSED_CARDS_LIST_ID = '524adf089e1491f3360008cb'

# TODO odczytac z zewnetrznego pliku
APP_KEY = 'f34058aafb06bd8bf617f1e698e2f954'
APP_TOKEN = 'a903a79b2aa6952569cadb6f411e3b275af97e22ba9503c8c16e97cf43588967'

logger = logutils.create_logger('webutils')


def get_user_real_name(username):
    logger.info("Getting real name for user '" + username + "'...")
    command = 'boards/' + BOARD_ID + "/members"
    params = {'fields': 'fullName,username'}
    response = get_request_response(command, params)
    object = json.loads(response.text)
    for item in object:
        if item['username'] == username:
            return item['fullName']
    return username


def get_closed_cards():
    logger.info("Getting all closed cards...")
    command = 'lists/' + CLOSED_CARDS_LIST_ID + '/cards'
    params = {'fields': 'id'}
    response = get_request_response(command, params)
    return get_as_object(response)


def get_card_comments(card_id):
    logger.info("Getting all comments for card with id '" + card_id + "'...")
    command = 'cards/' + card_id + '/actions'
    params = {'fields': 'date,data', 'filter': 'commentCard'}
    response = get_request_response(command, params)
    return get_as_object(response)


def get_request_response(command, extra_params=None):
    auth_params = {'key': APP_KEY, 'token': APP_TOKEN}
    final_params = auth_params
    if extra_params:
        final_params.update(extra_params)
    url = BASE_URL + '/' + command
    return requests.get(url, params=final_params)


def get_as_object(response):
    object = json.loads(response.text)
    result = []
    for item in object:
        logger.debug(item)
        result.append(item)
    return result
