from http import HTTPStatus

from tests.factories import ConnectionFactory

from connections.models.connection import Connection, ConnectionType


def test_can_update_connection(db, testapp):
    connection = ConnectionFactory(connection_type=ConnectionType.coworker)
    db.session.commit()
    payload = {
        'connection_type': ConnectionType.friend.value,
    }
    res = testapp.patch(f'/connections/{connection.id}', json=payload)

    assert res.status_code == HTTPStatus.NO_CONTENT

    connection = Connection.query.get(connection.id)

    assert connection is not None
    assert connection.connection_type == ConnectionType.friend


def test_bad_connection_id(db, testapp):
    payload = {
        'connection_type': ConnectionType.friend.value,
    }
    # '0' seems like a safe integer value that should never be an ID
    res = testapp.patch(f'/connections/0', json=payload)

    assert res.status_code == HTTPStatus.GONE
    assert res.json == {'description': 'Resource not found.',
                        'errors': {'connection_id': ['No connection found with this ID']}}


def test_bad_connection_type(db, testapp):
    connection = ConnectionFactory(connection_type=ConnectionType.coworker)
    db.session.commit()
    payload = {
        'connection_type': 'godmother',
    }
    res = testapp.patch(f'/connections/{connection.id}', json=payload)

    assert res.status_code == HTTPStatus.BAD_REQUEST
    assert res.json == {'description': 'Input failed validation.',
                        'errors': {'connection_type': ['Invalid enum member godmother']}}

    new_connection = Connection.query.get(connection.id)

    # Confirm it has not been updated
    assert new_connection.updated_at == connection.updated_at
