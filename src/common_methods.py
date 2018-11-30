# Retweet Bot common methods used in multiple modules

import datetime

def can_perform_action_today(day_to_complete_action):
    """Checks the current day against the day actions should be performed"""

    if datetime.datetime.today().weekday() == day_to_complete_action or day_to_complete_action == 7:
        return True

    return False