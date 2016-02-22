# -*- coding: utf-8 -*-

import re
import datetime
import json

import logutils
import webutils

logger = logutils.create_logger('main')

entries = {}
closed_cards = webutils.get_closed_cards()
for closed_card in closed_cards:
    closed_card_comments = webutils.get_card_comments(closed_card['id'])
    for comment in closed_card_comments:
        matches = re.findall('@\w+\s*:\s*[0-9]+h', comment['data']['text'])
        if matches:
            for match in matches:
                m = re.search('\w+', match.__str__())
                username = m.group(0).lower()
                m = re.search('[0-9]+h', match.__str__())
                hours = m.group(0)[:-1]

                date = datetime.datetime.strptime(comment['date'], '%Y-%m-%dT%H:%M:%S.%fZ')

                if not entries.__contains__(username):
                    entries[username] = {}

                if not entries[username].__contains__(date.year):
                    entries[username][date.year] = {}

                if not entries[username][date.year].__contains__(date.month):
                    entries[username][date.year][date.month] = 0

                entries[username][date.year][date.month] += int(hours)
                logger.debug('Added ' + str(hours) + 'h for user ' + username + ' in ' + str(date.year) + '.' + str(date.month))

for key in entries:
    print webutils.get_user_real_name(key) + ': ' + json.dumps(entries[key])
