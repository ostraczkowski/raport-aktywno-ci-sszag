# -*- coding: utf-8 -*-

import re
import datetime

import logutils
import webutils

USER_REPORT_PATTERN = '@\w+\s*:\s*[0-9]+h'

logger = logutils.create_logger('main')


def assure_report_exists(reports, username, year, month):
    if not reports.__contains__(username):
        reports[username] = {}
    if not reports[username].__contains__(year):
        reports[username][year] = {}
    if not reports[username][year].__contains__(month):
        reports[username][year][month] = 0


def get_username(text):
    m = re.search('\w+', text)
    return m.group(0).lower()


def get_hours(text):
    m = re.search('[0-9]+h', text)
    return m.group(0)[:-1]


def get_date(text):
    return datetime.datetime.strptime(text, '%Y-%m-%dT%H:%M:%S.%fZ')


def update_reports(reports, comments):
    for comment in comments:
        matches = re.findall(USER_REPORT_PATTERN, comment['data']['text'])
        if matches:
            for match in matches:
                username = get_username(match.__str__())
                hours = get_hours(match.__str__())
                date = get_date(comment['date'])
                assure_report_exists(reports, username, date.year, date.month)
                reports[username][date.year][date.month] += int(hours)
                logger.debug('Added ' + str(hours) + 'h for user ' + username + ' in ' + str(date.year) + '.' + str(date.month))


def read_reports_from_comments():
    reports = {}
    cards = webutils.get_closed_cards()
    for card in cards:
        comments = webutils.get_card_comments(card['id'])
        update_reports(reports, comments)
    return reports


def assure_report_by_year_exist(reports_by_year, year):
    if not reports_by_year.__contains__(year):
        reports_by_year[year] = {}


def build_reports_by_year(reports):
    reports_by_year = {}
    for username in reports:
        years = reports[username]
        for year in years:
            hours_in_year = 0
            months = reports[username][year]
            for month in months:
                hours_in_year += reports[username][year][month]
            assure_report_by_year_exist(reports_by_year, year)
            reports_by_year[year][username] = hours_in_year
    return reports_by_year

def build_years_summary(reports_by_year):
    summary = ''
    for year in reports_by_year:
        summary += str(year) + ':\n'
        summary += '---------------------------------------------------------------\n'
        for username in reports_by_year[year]:
            user_real_name = webutils.get_user_real_name(username)
            summary += user_real_name + ': ' + str(reports_by_year[year][username]) + 'h\n'
        summary += '\n'
    return summary


def build_users_summary(reports_by_year, reports):
    summary = ''
    for username in reports:
        user_real_name = webutils.get_user_real_name(username)
        summary += user_real_name + ':\n'
        summary += '---------------------------------------------------------------\n'
        years = reports[username]
        for year in years:
            summary += '- ' + str(year) + ': ' + str(reports_by_year[year][username]) + 'h\n'
            months = reports[username][year]
            for month in months:
                summary += '- ' + str(year) + '.' + str(month) + ': ' + str(reports[username][year][month]) + 'h\n'
            summary += '\n'
    return summary


def print_final_report(reports):
    reports_by_year = build_reports_by_year(reports)
    result = build_years_summary(reports_by_year)
    result += build_users_summary(reports_by_year, reports)
    print result


print_final_report(read_reports_from_comments())
