# -*- coding: utf-8 -*-

import re
import datetime
import json

import logutils
import webutils

logger = logutils.create_logger('main')


def create_entry_if_needed(entries, username, year, month):
    if not entries.__contains__(username):
        entries[username] = {}
    if not entries[username].__contains__(year):
        entries[username][year] = {}
    if not entries[username][year].__contains__(month):
        entries[username][year][month] = 0


def get_username(str):
    m = re.search('\w+', str)
    return m.group(0).lower()


def get_hours(str):
    m = re.search('[0-9]+h', str)
    return m.group(0)[:-1]


def get_date(str):
    return datetime.datetime.strptime(str, '%Y-%m-%dT%H:%M:%S.%fZ')


def update_entries(entries, comments):
    for comment in comments:
        matches = re.findall('@\w+\s*:\s*[0-9]+h', comment['data']['text'])
        if matches:
            for match in matches:
                username = get_username(match.__str__())
                hours = get_hours(match.__str__())
                date = get_date(comment['date'])
                create_entry_if_needed(entries, username, date.year, date.month)
                entries[username][date.year][date.month] += int(hours)
                logger.debug('Added ' + str(hours) + 'h for user ' + username + ' in ' + str(date.year) + '.' + str(date.month))


def read_entries(cards):
    entries = {}
    for card in cards:
        comments = webutils.get_card_comments(card['id'])
        update_entries(entries, comments)
    return entries


def build_report(entries):
    # TODO
    for key in entries:
        print webutils.get_user_real_name(key) + ': ' + json.dumps(entries[key])


build_report(read_entries(webutils.get_closed_cards()))
