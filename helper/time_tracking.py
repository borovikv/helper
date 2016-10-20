import argparse
import csv
import datetime
import os
from collections import defaultdict

import dateutil.parser as dtparse

import helper.jira_helper as jira_helper
import helper.values as v
from helper import settings
from helper.template_utils import render_to_response


def create_table(input_file: str, from_date: datetime.datetime, to_date: datetime.datetime):
    result = defaultdict(dict)
    with open(input_file, 'rU') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row[v.category_field] == v.work_value:
                start_day = dtparse.parse(row[v.start_date_field])
                end_day = dtparse.parse(row[v.end_date_field])
                if start_day >= from_date and end_day < to_date:
                    description = row[v.description_field]

                    bear_dict = result[description]
                    if 'timetracking' not in bear_dict:
                        bear_dict['timetracking'] = defaultdict(float)

                    if start_day.date() != end_day.date():
                        current_day = start_day
                        while current_day < end_day:
                            next_day = datetime.datetime(year=current_day.year, month=current_day.month,
                                                         day=current_day.day + 1)
                            if next_day >= end_day:
                                next_day = end_day
                            elapsed = (next_day - current_day).total_seconds() / 3600.0
                            bear_dict['timetracking'][current_day.strftime('%Y-%m-%d')] += elapsed
                            current_day = next_day
                    else:
                        day = start_day.strftime('%Y-%m-%d')
                        elapsed = float(row[v.elapsing_field])
                        bear_dict['timetracking'][day] += elapsed
    issues = jira_helper.get_tickets_info(result.keys())
    for issue_id in issues:
        result[issue_id].update(issues[issue_id])
    for issue_id in result:
        result[issue_id]['total'] = sum(result[issue_id]['timetracking'].values())
    return dict(result)


def create_timetracking_report(from_date: str = None, to_date: str = None):
    now = datetime.datetime.now()

    if not to_date:
        to_date = datetime.datetime(year=now.year, month=now.month, day=now.day + 1)
    else:
        to_date = dtparse.parse(to_date)

    if not from_date:
        from_date = datetime.datetime(year=now.year, month=now.month, day=1)
    else:
        from_date = dtparse.parse(from_date)

    tickets = create_table('/home/vborovic/Downloads/backup_20161018_154239.csv', from_date, to_date)
    total = sum([t for _, d in tickets.items() for _, t in d['timetracking'].items()])
    s = render_to_response('timetracking.html',
                           {'tickets': tickets, 'total': total, 'from_date': from_date, 'to_date': to_date})
    report_name = 'report_{data}_from_{from_date}_to_{to_date}.html'.format(
        data=now.strftime('%Y-%m-%d'),
        from_date=from_date.strftime('%Y-%m-%d'),
        to_date=to_date.strftime('%Y-%m-%d'))
    with open(os.path.join(settings.OUTPUT_PATH, report_name), 'w') as f:
        f.write(s)


def get_blocks_values_from_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('--from_date', type=str)
    parser.add_argument('--to_date', type=str)
    return vars(parser.parse_args())


if __name__ == "__main__":
    kwargs = get_blocks_values_from_command_line()
    create_timetracking_report(**kwargs)
