import os

MY_EMAIL = 'vladimir.borovic@yopeso.com'
REPORT_TO_EMAILS = ['kamil@sense360.com', 'ori@sense360.com', MY_EMAIL]
BLOCKS_SEQUENCE = ['blockers', 'done', 'in_progress', 'tomorrow']
BASE_JIRA_URL = 'https://sense360.atlassian.net'
JIRA_LOGIN = MY_EMAIL
JIRA_PASSWORD = os.environ.get('JIRA_PASSWORD')
MY_EMAIL_PASSWORD = os.environ.get('MY_EMAIL_PASSWORD')
