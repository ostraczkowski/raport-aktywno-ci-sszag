# -*- coding: utf-8 -*-

from collections import OrderedDict
import re
import datetime

import logutils
import webutils
import reportutils

logger = logutils.create_logger(__name__)


def _read_reports_from_comments():
    """Private function to read user reports from Trello comments. Report example: '@oskar: 15h [2015-02]."""
    reports = {}
    cards = webutils.get_closed_cards()
    for card in cards:
        comments = webutils.get_card_comments(card['id'])
        _update_reports(reports, comments)
    return reports


def _update_reports(reports, comments):
    """Private function to update user reports which were already processed with reports from passed comments."""
    for comment in comments:
        matches = re.findall('@\w+\s*:\s*\d+[.,]?\d*h\s*\[\d{4}-\d{2}\]', comment['data']['text'])
        if matches:
            for match in matches:
                username = _get_username(match.__str__())
                hours = _get_hours(match.__str__())
                date = _get_date_from_report(match.__str__())
                _update_user_report(reports, username, hours, date)
            continue

        matches = re.findall('@\w+\s*:\s*\d+[.,]?\d*h', comment['data']['text'])
        if matches:
            for match in matches:
                username = _get_username(match.__str__())
                hours = _get_hours(match.__str__())
                date = _get_date_from_comment(comment['date'])
                _update_user_report(reports, username, hours, date)



def _update_user_report(reports, username, hours, date):
    _assure_report_by_user_exists(reports, username, date.year, date.month)
    reports[username][date.year][date.month] += float(hours)
    logger.debug('Added ' + hours + 'h for user ' + username + ' in ' + str(date.year) + '.' + str(date.month))


def _get_username(text):
    """Private function which returns username extracted from user report."""
    m = re.search('\w+', text)
    return m.group(0).lower()


def _get_hours(text):
    """Private function which returns hours extracted from user report."""
    m = re.search('\d+[.,]?\d*h', text)
    hours = m.group(0)[:-1]
    return hours.replace(',', '.')


def _get_date_from_report(text):
    """Private function which returns date extracted from user report (optional)."""
    m = re.search('\d{4}-\d{2}', text)
    return datetime.datetime.strptime(m.group(0), '%Y-%m')

def _get_date_from_comment(text):
    """Private function which returns date extracted from the comment."""
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


def _sort_reports_by_user(reports):
    sorted_by_user = OrderedDict(sorted(reports.items(), key=lambda t: t[0]))
    for user in sorted_by_user:
        sorted_by_year = OrderedDict(sorted(sorted_by_user[user].items(), key=lambda t: t[0], reverse=True))
        for year in sorted_by_year:
            sorted_by_month = OrderedDict(sorted(sorted_by_year[year].items(), key=lambda t: t[0]))
            sorted_by_year[year] = sorted_by_month
        sorted_by_user[user] = sorted_by_year
    return sorted_by_user


def _sort_reports_by_year(reports):
    sorted_by_year = OrderedDict(sorted(reports.items(), key=lambda t: t[0], reverse=True))
    for year in sorted_by_year:
        sorted_by_value = OrderedDict(sorted(sorted_by_year[year].items(), key=lambda t: t[1], reverse=True))
        sorted_by_year[year] = sorted_by_value
    return sorted_by_year


if __name__ == "__main__":
    reports_by_user = _sort_reports_by_user(_read_reports_from_comments())
    reports_by_year = _sort_reports_by_year(_build_reports_by_year(reports_by_user))
    names_by_users = _build_names_by_users(reports_by_user)
    reportutils.make_text_report(reports_by_user, reports_by_year, names_by_users)
    reportutils.make_chart_report(reports_by_user, reports_by_year, names_by_users)
