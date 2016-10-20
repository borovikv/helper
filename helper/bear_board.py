import argparse

from collections import defaultdict


import helper.emailer as emailer
import helper.jira_helper as jira_helper
from helper import settings
from helper.template_utils import render_to_response


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
    ext = 'html' if is_html else 'txt'
    return render_to_response('message_daily_progress.' + ext, context)


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
