from factory import Faker, SelfAttribute, Sequence, SubFactory
from factory.alchemy import SQLAlchemyModelFactory

from connections.database import db
from connections.models.connection import Connection
from connections.models.person import Person


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:

        abstract = True
        sqlalchemy_session = db.session


class PersonFactory(BaseFactory):
    """Person factory."""

    email = Sequence(lambda n: f'person{n}@example.com')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    date_of_birth = Faker('date')

    class Meta:

        model = Person
        force_flush = True


class ConnectionFactory(BaseFactory):
    """Connection factory."""

    connection_type = 'friend'

    from_person_id = SelfAttribute('from_person.id')
    from_person = SubFactory(PersonFactory)
    to_person_id = SelfAttribute('to_person.id')
    to_person = SubFactory(PersonFactory)

    class Meta:

        model = Connection
        exclude = ('from_person', 'to_person')
