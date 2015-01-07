import requests
from requests.auth import HTTPBasicAuth

import configparser
import os


config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.local/ak_github_interest.ini'))

LOGIN = config['github']['login']
PASS = config['github']['password']

to_list = lambda s: [l for l in s.splitlines() if l]

MEMBERS_OF = to_list(config['github']['members_of'])
PR_IN = to_list(config['github']['pull_request_in'])

BASE_URL = 'https://api.github.com/'


def github_list(path):
    page_size = 100
    page_no = 1
    while True:
        params = {'page': page_no, 'per_page': page_size}
        r = requests.get(
            BASE_URL + path,
            params=params,
            auth=HTTPBasicAuth(LOGIN, PASS)
        )
        data = r.json()
        for e in data:
            yield e
        if len(data) < page_size:
            break
        page_no += 1


def find_repos(org):
    return github_list('orgs/%s/repos' % org)


def find_prs(org, repo):
    return github_list('repos/%s/%s/pulls' % (org, repo))


def find_prs_in_orgs():
    for org in PR_IN:
        for repo in find_repos(org):
            for pr in find_prs(org, repo['name']):
                yield pr


def find_users(org):
    return github_list('orgs/%s/members' % org)


def find_logins():
    for org in MEMBERS_OF:
        for user in find_users(org):
            yield user['login']


def find_pr_by_member():
    logins = list(find_logins())
    for pr in find_prs_in_orgs():
        if pr['user']['login'] in logins:
            yield pr

if __name__ == '__main__':
    for pr in find_pr_by_member():
        print(pr['user']['login'], pr['html_url'], pr['state'])
