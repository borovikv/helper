import csv

import datetime
from collections import defaultdict

import dateutil.parser as dtparse
import pprint
import helper.jira_helper as jira_helper
import helper.values as v


def create_table(input_file: str, from_date: str = None, to_date: str = None):
    now = datetime.datetime.now()
    if not to_date:
        to_date = datetime.datetime(year=now.year, month=now.month, day=now.day)
    else:
        to_date = dtparse.parse(to_date)

    if not from_date:
        from_date = datetime.datetime(year=now.year, month=now.month, day=1)
    else:
        from_date = dtparse.parse(from_date)

    result = defaultdict(dict)
    with open(input_file, 'rU') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row[v.category_field] == v.work_value:
                start_day = dtparse.parse(row[v.start_date_field])
                end_day = dtparse.parse(row[v.end_date_field])
                if start_day >= from_date and end_day <= to_date:
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
    return dict(result)


pprint.pprint(create_table('/home/vborovic/Downloads/backup_20161018_154239.csv', '2016-10-16'))
