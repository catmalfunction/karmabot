import logging

from sqlalchemy import func
from bot.settings import SLACK_CLIENT, KARMABOT_ID, SLACK_ID_FORMAT, MAX_POINTS
from .db import db_session
from .db.karma_transaction import KarmaTransaction
from .db.karma_user import KarmaUser
from .db.karma_target import KarmaTarget
from .slack import post_msg, get_available_username, get_channel_name


class GetUserInfoException(Exception):
    pass


class GetTargetInfoException(Exception):
    pass


def _parse_karma_change(karma_change):
    receiver, voting = karma_change

    points = voting.count("+") - voting.count("-")

    return receiver, points


def process_karma_changes(message, karma_changes):
    for karma_change in karma_changes:
        target, points = _parse_karma_change(karma_change)
        try:
            karma = Karma(
                giver_id=message.user_id,
                target=target,
                channel_id=message.channel_id,
            )
        except GetTargetInfoException:
            return

        try:
            text = karma.change_karma(points)
        except Exception as exc:
            text = str(exc)

        post_msg(message.channel_id, text)


class Karma:
    def __init__(self, giver_id, target, channel_id):
        self.session = db_session.create_session()
        self.giver = self.session.query(KarmaUser).get(giver_id)
        self.target = self._find_karma_target(target)
        self.channel_id = channel_id
        self.last_score_maxed_out = False

        if not self.giver:
            self.giver = self._create_karma_user(giver_id)
        if not self.target:
            self.target = self._create_karma_target(target)

    def _find_karma_target(self, target):
        return self.session.query(KarmaTarget).filter(
            func.lower(KarmaTarget.target) == func.lower(target)
        ).one_or_none()

    def _create_karma_target(self, target):
        user = None
        if SLACK_ID_FORMAT.match(target):
            stripped = target.strip("<>@")
            user = self.session.query(KarmaUser).get(stripped)
            if not user:
                user = self._create_karma_user(stripped)
        new_target = KarmaTarget(target=target, user_id=user.user_id if user else None)
        self.session.add(new_target)
        self.session.commit()

        logging.info(f"Created new KarmaTarget: {repr(new_target)}")
        return new_target

    def _create_karma_user(self, user_id):
        user_info = SLACK_CLIENT.api_call("users.info", user=user_id)

        error = user_info.get("error")
        if error is not None:
            logging.info(f"Cannot get user info for {user_id} - error: {error}")
            raise GetUserInfoException

        slack_id = user_info["user"]["id"]
        username = get_available_username(user_info)

        new_user = KarmaUser(user_id=slack_id, username=username)
        self.session.add(new_user)
        self.session.commit()

        logging.info(f"Created new KarmaUser: {repr(new_user)}")
        return new_user

    def _calc_final_score(self, points):
        if abs(points) > MAX_POINTS:
            self.last_score_maxed_out = True
            return MAX_POINTS if points > 0 else -MAX_POINTS
        else:
            self.last_score_maxed_out = False
            return points

    def _create_msg_bot_self_karma(self, points) -> str:
        if points > 0:
            text = (
                f"Thanks {self.giver.username} for the extra karma"
                f", my karma is {self.target.karma_points} now"
            )
        else:
            text = (
                f"Not cool {self.giver.username} lowering my karma "
                f"to {self.target.karma_points}, but you are probably"
                f" right, I will work harder next time"
            )
        return text

    def _create_msg(self, points):
        target_user = self.session.query(KarmaUser).get(self.target.user_id) if self.target.user_id else None
        target_name = target_user.username if target_user else self.target.target

        poses = "'" if target_name.endswith("s") else "'s"
        action = "increase" if points > 0 else "decrease"

        text = (
            f"{target_name}{poses} karma {action}d to "
            f"{self.target.karma_points}"
        )
        if self.last_score_maxed_out:
            text += f" (= max {action} of {MAX_POINTS})"

        return text

    def _save_transaction(self, points):
        transaction = KarmaTransaction(
            giver_id=self.giver.user_id,
            target_id=self.target.target_id,
            channel=get_channel_name(self.channel_id),
            karma=points,
        )
        self.session.add(transaction)
        self.session.commit()

        finished_transaction = (
            self.session.query(KarmaTransaction)
            .order_by(KarmaTransaction.id.desc())
            .first()
        )
        logging.info(repr(finished_transaction))

    def change_karma(self, points):
        """ Updates Karma in the database """
        if not isinstance(points, int):
            err = (
                "Program bug: change_karma should "
                "not be called with a non int for "
                "points arg!"
            )
            raise RuntimeError(err)

        try:
            target_user = self.session.query(KarmaUser).get(self.target.user_id) if self.target.user_id else None
            if target_user and target_user.user_id == self.giver.user_id:
                raise ValueError("Sorry, cannot give karma to self")

            points = self._calc_final_score(points)
            self.target.karma_points += points
            self.session.commit()

            self._save_transaction(points)

            if target_user and target_user.user_id == KARMABOT_ID:
                return self._create_msg_bot_self_karma(points)
            else:
                return self._create_msg(points)

        finally:
            logging.info(
                (
                    f"[Karmachange] {self.giver.user_id} to "
                    f"{self.target.target}: {points}"
                )
            )
            self.session.close()
