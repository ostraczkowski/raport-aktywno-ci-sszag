# -*- coding: utf-8 -*-


import webutils


def assure_report_by_year_exist(reports_by_year, year):
    if not reports_by_year.__contains__(year):
        reports_by_year[year] = {}


def build_reports_by_year(reports):
    reports_by_year = {}
    for username in reports:
        years = reports[username]
        for year in years:
            hours_in_year = 0.0
            months = reports[username][year]
            for month in months:
                hours_in_year += reports[username][year][month]
            assure_report_by_year_exist(reports_by_year, year)
            reports_by_year[year][username] = hours_in_year
    return reports_by_year


def build_years_summary(reports_by_year):
    summary = 'ZESTAWIENIA ROCZNE\n'
    summary += '#################################################################\n'
    for year in reports_by_year:
        summary += str(year) + ':\n'
        summary += '---------------------------------------------------------------\n'
        for username in reports_by_year[year]:
            user_real_name = webutils.get_user_real_name(username)
            summary += user_real_name + ': ' + str(reports_by_year[year][username]) + 'h\n'
        summary += '\n'
    return summary


def build_users_summary(reports_by_year, reports):
    summary = 'ZESTAWIENIA SZCZEGÓŁOWE CZŁONKÓW\n'
    summary += '#################################################################\n'
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
    result = '\n'
    result += build_years_summary(reports_by_year)
    result += build_users_summary(reports_by_year, reports)
    print result
