TEAMS = {
    'team1': [
        # 'foo@example.com',
    ],
}

DEFAULT_TEAM = 'team1'

DEFAULT_GIT_PATH = None

# allow custom over rides NOT checked in to git (in .gitignore)
# to use, create a settings_override.py file and duplicate the
# subset of settings you wish to over-ride there
try:
    from settings_override import *
except ImportError:
    pass
