# -*- coding: utf-8 -*-

import re
import datetime

import logutils
import webutils
import reportutils

logger = logutils.create_logger(__name__)


def _read_reports_from_comments():
    reports = {}
    cards = webutils.get_closed_cards()
    for card in cards:
        comments = webutils.get_card_comments(card['id'])
        _update_reports(reports, comments)
    return reports


def _update_reports(reports, comments):
    for comment in comments:
        matches = re.findall('@\w+\s*:\s*[0-9]+[.,]?[0-9]?h', comment['data']['text'])
        if matches:
            for match in matches:
                username = _get_username(match.__str__())
                hours = _get_hours(match.__str__())
                date = _get_date(comment['date'])
                _assure_report_by_user_exists(reports, username, date.year, date.month)
                reports[username][date.year][date.month] += float(hours)
                logger.debug(
                    'Added ' + hours + 'h for user ' + username + ' in ' + str(date.year) + '.' + str(date.month))


def _get_username(text):
    m = re.search('\w+', text)
    return m.group(0).lower()


def _get_hours(text):
    m = re.search('[0-9]+[.,]?[0-9]?h', text)
    hours = m.group(0)[:-1]
    return hours.replace(',', '.')


def _get_date(text):
    return datetime.datetime.strptime(text, '%Y-%m-%dT%H:%M:%S.%fZ')


def _assure_report_by_user_exists(reports, username, year, month):
    if not reports.__contains__(username):
        reports[username] = {}
    if not reports[username].__contains__(year):
        reports[username][year] = {}
    if not reports[username][year].__contains__(month):
        reports[username][year][month] = 0


def _build_reports_by_year(reports_by_user):
    reports_by_year = {}
    for username in reports_by_user:
        years = reports_by_user[username]
        for year in years:
            hours_in_year = 0.0
            months = reports_by_user[username][year]
            for month in months:
                hours_in_year += reports_by_user[username][year][month]
            _assure_report_by_year_exist(reports_by_year, year)
            reports_by_year[year][username] = hours_in_year
    return reports_by_year


def _assure_report_by_year_exist(reports_by_year, year):
    if not reports_by_year.__contains__(year):
        reports_by_year[year] = {}


def _build_names_by_users(reports_by_user):
    names_by_users = {}
    for username in reports_by_user:
        user_real_name = webutils.get_user_real_name(username)
        names_by_users[username] = user_real_name
    return names_by_users


if __name__ == "__main__":
    reports_by_user = _read_reports_from_comments()
    reports_by_year = _build_reports_by_year(reports_by_user)
    names_by_users = _build_names_by_users(reports_by_user)
    reportutils.make_text_report(reports_by_user, reports_by_year, names_by_users)
    reportutils.make_chart_report(reports_by_user, reports_by_year, names_by_users)
