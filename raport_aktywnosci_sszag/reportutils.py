# -*- coding: utf-8 -*-

from collections import OrderedDict
from matplotlib import rc

import numpy as np
import os
import pylab as plt

import logutils

REPORT_DIR = '../raporty'

logger = logutils.create_logger(__name__)


def make_text_report(reports_by_user, reports_by_year, names_by_users):
    logger.info("Generating text report...")

    text_report = '\n'
    text_report += _build_years_summary(reports_by_year, names_by_users)
    text_report += _build_users_summary(reports_by_user, reports_by_year, names_by_users)

    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)
    filename = REPORT_DIR + '/raport-tekst.txt'
    file = open(filename, 'w')
    file.write(text_report.encode('utf-8'))
    file.close()

    logger.info('Text report saved in ' + filename)


def _build_years_summary(reports_by_year, names_by_users):
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


def _build_users_summary(reports_by_user, reports_by_year, names_by_users):
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


def make_chart_report(reports_by_user, reports_by_year, names_by_users):
    logger.info("Generating chart reports...")

    LABELS_IDX = 0
    VALUES_IDX = 1

    work_hours_by_user = OrderedDict(reports_by_year.items())
    for year in reports_by_year:

        # initialize work hours structure with empty values
        work_hours_by_user[year] = [[] for _ in range(13)] # 0 is for total hours in the year, the rest is for particular months

        # fill work hours structure with actual values
        for user in reports_by_year[year]:
            work_hours_by_user[year][0].append((names_by_users[user], reports_by_year[year][user]))
            for month in reports_by_user[user][year]:
                work_hours_by_user[year][month].append((names_by_users[user], reports_by_user[user][year][month]))

        # generate annual report
        filename = REPORT_DIR + '/raport-wykres-%d.png' % (year)
        labels = [_[LABELS_IDX] for _ in work_hours_by_user[year][0]]
        values = [_[VALUES_IDX] for _ in work_hours_by_user[year][0]]
        _plot_chart(filename, str(year), labels, values)

        # generate monthly reports
        for month in range(1, 13):
            filename = REPORT_DIR + '/raport-wykres-%d-%02d.png' % (year, month)
            if work_hours_by_user[year][month]:
                sorted_work_hours_by_user = sorted(work_hours_by_user[year][month], key=lambda tup: tup[VALUES_IDX], reverse=True)
                labels = [_[LABELS_IDX] for _ in sorted_work_hours_by_user]
                values = [_[VALUES_IDX] for _ in sorted_work_hours_by_user]
                _plot_chart(filename, "%d-%02d" % (year, month), labels, values)


def _plot_chart(filename, title, labels, values):
    x_max = len(labels) + 1
    y_max = max(values)

    rc('font', family='Arial')

    plt.figure(1)
    plt.title(title)
    plt.ylabel('Przepracowane godziny')

    bar = plt.bar(np.arange(1, x_max), values, width=0.8)
    plt.subplots_adjust(bottom=0.3)
    xticks_pos = [patch.get_xy()[0] + 0.5 * patch.get_width() for patch in bar]
    plt.xticks(xticks_pos, labels,  ha='right', rotation=45)
    plt.xlim([0.8, x_max])
    plt.ylim([0, y_max + 0.1 * y_max])

    plt.savefig(filename)
    plt.cla()
    plt.clf()

    logger.info('Chart report saved in ' + filename)
