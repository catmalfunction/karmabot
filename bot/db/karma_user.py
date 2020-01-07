import sqlalchemy as sa

from bot.db.modelbase import SqlAlchemyBase


class KarmaUser(SqlAlchemyBase):
    """ Models a slack user with karma in the DB """

    __tablename__ = "karma_user"

    user_id = sa.Column(sa.String, primary_key=True)
    username = sa.Column(sa.String)

    def formatted_user_id(self):
        """ Formats user id for use in slack messages """
        return f"<@{self.user_id}>"

    def __repr__(self):
        return (
            f"<KarmaUser> ID: {self.user_id} | Username: {self.username}"
        )

    def __str__(self):
        return self.__repr__()
