import argparse
import os
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader

import helper.emailer as emailer
import helper.jira_helper as jira_helper
from helper import settings


def is_last_week_day():
    import datetime
    now = datetime.datetime.now()
    friday = 5
    if now.isoweekday() == friday:
        return True
    return False


def convert_jira_status_to_email_status(status: str):
    email_status = settings.BEAR_STATUSES[status.lower()]
    if email_status == 'tomorrow' and is_last_week_day():
        return 'monday'
    return email_status


def create_message(*issues, is_html=True):
    tickets_info = jira_helper.get_tickets_info(issues, 'BEAR-')
    tickets_context = defaultdict(list)
    for ticket_id in tickets_info:
        status_context = tickets_context[convert_jira_status_to_email_status(tickets_info[ticket_id]['status'])]
        status_context.append({
            'url': tickets_info[ticket_id]['url'],
            'summary': tickets_info[ticket_id]['summary']
        })
    context = dict(fields=settings.BLOCKS_SEQUENCE, tickets=tickets_context)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(root_dir,'resources')
    if is_html:
        template = Environment(loader=FileSystemLoader(template_path)).get_template('message_daily_progress.html')
    else:
        template = Environment(loader=FileSystemLoader(template_path)).get_template('message_daily_progress.txt')
    return template.render(**context)


def send_message(*issues, no_send=True, test=False):
    text = create_message(*issues, is_html=not no_send)
    if no_send:
        print('-' * 100)
        print(text)
        print('-' * 100)
    else:
        emailer.send_email('Daily progress', text, to=settings.REPORT_TO_EMAILS if not test else [settings.MY_EMAIL])


def get_blocks_values_from_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('issues', default=[], nargs='+')
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--no_send', action='store_true')
    return vars(parser.parse_args())

if __name__ == "__main__":
    kwargs = get_blocks_values_from_command_line()
    issues = kwargs.pop('issues')
    send_message(*issues, **kwargs)
