from connections.database import CreatedUpdatedMixin, CRUDMixin, db, Model
from connections.models.connection import ConnectionType


class Person(Model, CRUDMixin, CreatedUpdatedMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(145), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)

    connections = db.relationship('Connection', foreign_keys='Connection.from_person_id')

    def mutual_friends(self, contact):
        """Given another person *contact*, return a set of people who are friends with both *self*
        and *contact*."""

        friends = [conn.to_person_id for conn in self.connections
                   if conn.connection_type == ConnectionType.friend]
        contact_fiends = [conn.to_person_id for conn in contact.connections
                          if conn.connection_type == ConnectionType.friend]

        return [db.session.query(Person).filter(Person.id == friend).first()
                for friend in set(friends).intersection(set(contact_fiends))]
