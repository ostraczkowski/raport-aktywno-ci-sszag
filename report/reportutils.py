# -*- coding: utf-8 -*-


import datetime

import logutils

logger = logutils.create_logger(__name__)
now = datetime.datetime.now()
date_now = "%d-%02d-%02dT%02d%02d%02d" % (now.year, now.month, now.day, now.hour, now.minute, now.second)


def build_years_summary(reports_by_year, names_by_users):
    summary = u'ZESTAWIENIA ROCZNE\n'
    summary += '#################################################################\n'
    summary += '\n'
    for year in reports_by_year:
        summary += "%s:\n" % (year)
        summary += '---------------------------------------------------------------\n'
        for username in reports_by_year[year]:
            summary += "%s: %.2fh\n" % (names_by_users[username], reports_by_year[year][username])
        summary += '\n'
    return summary


def build_users_summary(reports_by_user, reports_by_year, names_by_users):
    summary = u'ZESTAWIENIA SZCZEGÓŁOWE CZŁONKÓW\n'
    summary += '#################################################################\n'
    summary += '\n'
    for username in reports_by_user:
        summary += "%s:\n" % (names_by_users[username])
        summary += '---------------------------------------------------------------\n'
        years = reports_by_user[username]
        for year in years:
            summary += "- %d: %.2fh\n" % (year, reports_by_year[year][username])
            months = reports_by_user[username][year]
            for month in months:
                summary += "- %d.%02d: %.2fh\n" % (year, month, reports_by_user[username][year][month])
            summary += '\n'
    return summary


def make_text_report(reports_by_user, reports_by_year, names_by_users):
    logger.info("Generating text report...")

    text_report = '\n'
    text_report += build_years_summary(reports_by_year, names_by_users)
    text_report += build_users_summary(reports_by_user, reports_by_year, names_by_users)

    filename = date_now + '-text-report.txt'
    file = open(filename, 'w')
    file.write(text_report.encode('utf-8'))
    file.close()

    logger.info('Text report saved in ' + filename)


def make_chart_report(reports_by_user, reports_by_year, names_by_users):
    logger.info("Generating chart report...")
    # TODO
    # filename = date_now + '-chart-report.png'
    # logger.info('Chart report saved in ' + filename)
