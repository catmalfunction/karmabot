import logging
from sqlalchemy import func
from bot.db import db_session
from bot.db.karma_target import KarmaTarget

TOP_NUMBER = 10


def get_karma(**kwargs):
    """Get a current karma score"""
    karmas_to_check = kwargs.get("text").split()[1:]
    if not len(karmas_to_check):
        karmas_to_check = [kwargs.get("user_id")]

    karma_msg = ""
    session = db_session.create_session()

    for karma_item in karmas_to_check:
        target = session.query(KarmaTarget).filter(
            func.lower(KarmaTarget.target) == func.lower(karma_item)
        ).one_or_none()

        if target:
            karma_msg += f"Karma for `{target.target}` is: {target.karma_points}.\r\n"
        else:
            karma_msg += f"`{karma_item}` has never graced the karma database.\r\n"

    session.close()
    logging.info(f"Checked karma for: {' '.join(karmas_to_check)}.\r\n")
    return karma_msg
