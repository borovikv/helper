from jira import JIRA
import os

from jira.exceptions import JIRAError

from helper import settings


def get_tickets_info(issues_ids, prefix=''):
    jira = JIRA(options={'server': settings.BASE_JIRA_URL}, basic_auth=(settings.JIRA_LOGIN, settings.JIRA_PASSWORD))
    result = {}
    for id in issues_ids:
        issue_id = prefix + str(id)
        try:
            issue = jira.issue(issue_id)
            result[id] = {
                'url': '{url}/{issue_id}'.format(url=os.path.join(settings.BASE_JIRA_URL, 'browse'), issue_id=issue_id),
                'summary': issue.fields.summary,
                'issue': issue
            }
        except JIRAError:
            pass
    return result
