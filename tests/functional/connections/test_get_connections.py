from http import HTTPStatus

from connections.models.connection import ConnectionType
from tests.factories import ConnectionFactory, PersonFactory
# Importing from other tests is usually fine, but only if they are all being run together
from tests.functional.people.test_get_people import EXPECTED_FIELDS as EXPECTED_PERSON_FIELDS

EXPECTED_FIELDS = [
    'id',
    'from_person',
    'to_person',
    'connection_type',
]


def test_can_get_connections(db, testapp):
    ConnectionFactory.create_batch(10)
    db.session.commit()

    res = testapp.get('/connections')

    assert res.status_code == HTTPStatus.OK

    assert len(res.json) == 10
    for connection in res.json:
        for field in EXPECTED_FIELDS:
            assert field in connection


def test_can_get_connection_people(db, testapp):
    from_person = PersonFactory()
    to_person = PersonFactory()
    ConnectionFactory(from_person=from_person, to_person=to_person, connection_type=ConnectionType.friend)
    db.session.commit()

    res = testapp.get('/connections')

    assert res.status_code == HTTPStatus.OK

    # Because we're not currently tearing down between tests, this is 11
    assert len(res.json) == 11
    
    connection = res.json[10]

    assert connection['from_person']['id'] == from_person.id
    assert connection['to_person']['id'] == to_person.id
    assert connection['connection_type'] == ConnectionType.friend.value

    for field in EXPECTED_PERSON_FIELDS:
        assert field in connection['to_person']
        assert field in connection['from_person']