import sqlalchemy as sa

from bot.db.modelbase import SqlAlchemyBase


class KarmaTarget(SqlAlchemyBase):
    """ Models a target for karma in the DB """

    __tablename__ = "karma_target"

    target_id = sa.Column(sa.Integer, primary_key=True, autoincrement="auto")
    target = sa.Column(sa.String, index=True)

    karma_points = sa.Column(sa.Integer, default=0)
    user_id = sa.Column(sa.String, sa.ForeignKey("karma_user.user_id"), nullable=True)

    def __repr__(self):
        return (
            f"<KarmaTarget> ID: {self.target_id} | Target: {self.target} | "
            f"Karma-Points: {self.karma_points} | User ID (if any): {self.user_id}"
        )

    def __str__(self):
        return self.__repr__()
