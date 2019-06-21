import argparse
from collections import Counter, defaultdict
import subprocess
import sys

import settings


def kwargs_or_default(setting_value):
    if setting_value:
        return dict(default=setting_value)
    return dict(required=True)


def _extract_num(str, word):
    if word not in str:
        return 0
    return int(str.split(' ' + word)[0].split(' ')[-1])


def get_stats(args):
    authors = defaultdict(Counter)
    emails = settings.TEAMS[args.team]
    stdout = get_git_stdout(args.path, emails, args.days)
    lines = stdout.split('\n')[:-1]  # empty line at end
    lines.reverse()  # pop off back
    while lines:
        hash = lines.pop()
        author = lines.pop()
        date = lines.pop()
        subject = lines.pop()
        _empty = lines.pop()
        stats_str = lines.pop()
        files = _extract_num(stats_str, 'file')
        added = _extract_num(stats_str, 'insertion')
        deleted = _extract_num(stats_str, 'deletion')
        authors[author].update(dict(
            files=files,
            added=added,
            deleted=deleted,

        ))
        if not args.just_totals:
            print '%s %s %s' % (date[0:10], author, subject)

    if not authors:
        return

    authors_sorted = sorted(authors.items(), key=lambda x: x[1]['files'], reverse=True)
    print '{:}{: <30} {: >10} {: >15} {: >15}'.format(
        '' if args.just_totals else '\n',
        '=== Totals ===',
        'Files',
        'Lines Added',
        'Lines Deleted',
    )
    for email, stats in authors_sorted:
        print '{: <30} {: >10} {: >15} {: >15}'.format(
        #print '%s: %s files, %s lines added, %s lines deleted' % (
            email,
            stats['files'],
            stats['added'],
            stats['deleted'],
        )



def get_git_stdout(path, emails, days):
    command = [
        'git',
        '--no-pager',
        'log',
        'origin/master',
        '--since="%s days ago"' % args.days,
        '--format=%h%n%ae%n%ai%n%s', # short hash, email, new line, subject line
        '--shortstat',
    ]
    for email in emails:
        command.append('--author=%s' % email)  # can have multiple
    p = subprocess.Popen(
        command,
        cwd=path,
        #shell=True,
        close_fds=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    #p.wait()
    (stdoutdata, stderrdata) = p.communicate()
    if stderrdata:
        print stderrdata
        sys.exit(1)
    return stdoutdata


if __name__ == '__main__':
    #colorama.init(autoreset=True)
    parser = argparse.ArgumentParser(prog='git-stats')
    parser.add_argument('--team', help='Which team from settings to use',
        **kwargs_or_default(settings.DEFAULT_TEAM))
    parser.add_argument('--path', help='Path to local git repo',
        **kwargs_or_default(settings.DEFAULT_GIT_PATH))
    parser.add_argument('--days', help='How many days back to go', default=30)
    parser.add_argument('--just-totals', help='Just print the totals', action='store_true')
    args = parser.parse_args()
    get_stats(args)
