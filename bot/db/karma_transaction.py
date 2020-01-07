import datetime

import sqlalchemy as sa
from sqlalchemy import Integer

from bot.db.modelbase import SqlAlchemyBase


class KarmaTransaction(SqlAlchemyBase):
    """ Models a karma transaction in the DB """

    __tablename__ = "karma_transaction"

    id: int = sa.Column(
        sa.BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    giver_id = sa.Column(sa.String, sa.ForeignKey("karma_user.user_id"), nullable=False)
    target_id = sa.Column(
        sa.Integer, sa.ForeignKey("karma_target.target_id"), nullable=False
    )

    # data
    timestamp = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    channel = sa.Column(sa.String)
    karma = sa.Column(sa.Integer, nullable=False)

    def __repr__(self):
        return (
            f"[KarmaTransaction] ID: {self.id} | {self.giver_id} -> "
            f"{self.target_id} | {self.timestamp} | Karma: {self.karma}"
        )

    def __str__(self):
        return self.__repr__()
