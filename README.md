# git-stat

## Quickstart

```bash
python git-stats.py --path /path/to/my/git-repo --days 30
```

## Specify a subset of authors

Create a `settings_override.py`, and include the following:

```bash
TEAMS = {
    'team1': [
        'user1@example.com',
        'user2@example.com',
    ],
}
```

Then, run `python git-stats.py --team team1`
