import argparse
from collections import Counter
import subprocess
import sys

import settings


def kwargs_or_default(setting_value):
    if setting_value:
        return dict(default=setting_value)
    return dict(required=True)


def get_stats(args):
    command = [
        'git',
        '--no-pager',
        'log',
        'origin/master',
        '--since="%s days ago"' % args.days,
        '--format="%h %ae%n%s"', # short hash, email, new line, subject line
        '--shortstat',
    ]
    for email in settings.TEAMS[settings.DEFAULT_TEAM]:
        command.append('--author=%s' % email)  # can have multiple
    p = subprocess.Popen(
        command,
        cwd='/Users/cseibert/src/server',
        #shell=True,
        close_fds=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    #p.wait()
    (stdoutdata, stderrdata) = p.communicate()
    print stdoutdata


if __name__ == '__main__':
    #colorama.init(autoreset=True)
    parser = argparse.ArgumentParser(prog='git-stats')
    parser.add_argument('--team', help='Which team from settings to use',
        **kwargs_or_default(settings.DEFAULT_TEAM))
    parser.add_argument('--days', help='How many days back to go', default=30)
    args = parser.parse_args()
    get_stats(args)
