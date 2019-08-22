import argparse
import datetime
from collections import Counter, defaultdict
from itertools import izip_longest
import subprocess
import sys

import colorama

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
    author_added_per_day = defaultdict(lambda: defaultdict(int))
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
        day_str = date[0:10]
        day = datetime.datetime.strptime(day_str, '%Y-%m-%d').date()
        author_added_per_day[author][day] = added
        if not args.just_totals:
            print '%s %s %s' % (day, author, subject)

    if not authors:
        return

    authors_sorted = sorted(authors.items(), key=lambda x: x[1]['added'], reverse=True)
    print '{:}{: <30} {: >12} {: >12} {: >12}  {: <30}'.format(
        '' if args.just_totals else '\n',
        '=== Totals ===',
        'Added',
        'Deleted',
        'Files',
        'Histogram',
    )
    for email, stats in authors_sorted:
        print '{: <30} {: >12} {: >12} {: >12}  {: <30}'.format(
        #print '%s: %s files, %s lines added, %s lines deleted' % (
            email,
            stats['added'],
            stats['deleted'],
            stats['files'],
            get_histogram(author_added_per_day[email], args.days, args.buckets),
        )


def chunk(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return list(izip_longest(*args, fillvalue=fillvalue))


def get_histogram(author_added_per_day, num_days, buckets=30):
    start_date = (datetime.datetime.now() - datetime.timedelta(days=num_days)).date()
    histogram = ''
    # split into X even sized buckets
    buckets = min(buckets, num_days)  # i.e. 10 days == 10 buckets (not 30)
    bucket_size = int(round(num_days / (buckets * 1.0)))
    for days_in_bucket in chunk(range(num_days), bucket_size):
        added = 0
        for day_num in days_in_bucket:
            current_date = start_date + datetime.timedelta(days=day_num)
            added += author_added_per_day.get(current_date, 0)
        char = '.' if added == 0 else '#'
        color = colorama.Style.DIM + colorama.Fore.WHITE
        if added > 10:
            color = colorama.Style.NORMAL
        if added > 100:
            color = colorama.Style.BRIGHT
        if added > 1000:
            color = colorama.Style.BRIGHT + colorama.Fore.RED
        histogram += color + char
    return histogram


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
    colorama.init(autoreset=True)
    parser = argparse.ArgumentParser(prog='git-stats')
    parser.add_argument('--team', help='Which team from settings to use',
        **kwargs_or_default(settings.DEFAULT_TEAM))
    parser.add_argument('--path', help='Path to local git repo',
        **kwargs_or_default(settings.DEFAULT_GIT_PATH))
    parser.add_argument('--days', help='How many days back to go', default=30, type=int)
    parser.add_argument('--buckets', help='How buckets to use for histogram', default=30, type=int)
    parser.add_argument('--just-totals', help='Just print the totals', action='store_true')
    args = parser.parse_args()
    get_stats(args)
