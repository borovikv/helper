import re
import argparse
import os

import helper.emailer as emailer
import helper.jira_helper as jira_helper
from helper import settings


def create_message(send=False, **blocks):
    all_tickets = [i for _, ids in blocks.items() for i in ids]
    tickets_info = jira_helper.get_tickets_info(all_tickets, 'BEAR-')
    text = ''
    for block in settings.BLOCKS_SEQUENCE:
        text += '<h3>{header}</h3>\n'.format(header=block.replace('_', ' ').capitalize())
        if blocks[block]:
            text += '<ul>'
        for ticket_id in blocks[block]:
            ticket_info = tickets_info[ticket_id]
            text += '<li><a href="{url}">{url}</a> - {summary}</li>'.format(
                url=ticket_info['url'],
                summary=ticket_info['summary']
            )
            text += '\n'

        if not blocks[block]:
            text += '-\n'
        else:
            text += '</ul>'
        text += '\n'
    if send:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root_dir,'resources/message_daily_progress.html')) as f:
            message_text = f.read()
        return message_text.format(text=text)
    return text


def send_message(no_test=False, send=False, **blocks):
    text = create_message(send=send, **blocks)
    if send:
        emailer.send_email('Daily progress', text, to=settings.REPORT_TO_EMAILS if no_test else [settings.MY_EMAIL])
    else:
        s = re.sub('<[^<]+?>', '', text)
        print('-' * 100)
        print(s)
        print('-' * 100)


def get_blocks_values_from_command_line():
    parser = argparse.ArgumentParser()
    for block_name in settings.BLOCKS_SEQUENCE:
        parser.add_argument('--%s' % block_name, default=[], nargs='+')
    parser.add_argument('--no_test', action='store_true')
    parser.add_argument('--send', action='store_true')
    return vars(parser.parse_args())

if __name__ == "__main__":
    kwargs = get_blocks_values_from_command_line()
    send_message(**kwargs)
