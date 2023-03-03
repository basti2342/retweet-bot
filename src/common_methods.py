# Retweet Bot common methods used in multiple modules

import datetime

def can_perform_action_today(days_to_complete_action):
    """Checks the current day against the day actions should be performed"""

    if datetime.datetime.today().weekday() in days_to_complete_action or 7 in days_to_complete_action:
        return True

    return False

def can_perform_action_this_month(months_to_complete_action):
    """Checks the current month against the month that actions should be performed"""

    if datetime.datetime.today().month in months_to_complete_action or 13 in months_to_complete_action:
        return True

    return False