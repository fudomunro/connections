from http import HTTPStatus

from flask import Blueprint, jsonify
from sqlalchemy.orm.exc import NoResultFound
from webargs.flaskparser import use_args

from connections.models.connection import Connection
from connections.models.person import Person
from connections.schemas import ConnectionSchema, ConnectionUpdateSchema, PersonSchema

blueprint = Blueprint('connections', __name__)


def person_json(person):
    return dict([(f, getattr(person, f)) for f in ['id', 'first_name', 'last_name', 'email']])


@blueprint.route('/people', methods=['GET'])
def get_people():
    people_schema = PersonSchema(many=True)
    people = Person.query.all()
    return people_schema.jsonify(people), HTTPStatus.OK


@blueprint.route('/people', methods=['POST'])
@use_args(PersonSchema(), locations=('json',))
def create_person(person):
    person.save()
    return PersonSchema().jsonify(person), HTTPStatus.CREATED


@blueprint.route('/connections', methods=['GET'])
def get_connections():
    connections = Connection.query.all()

    # It didn't seem to make sense to alter the schema just to get an expanded representation
    return jsonify(list({
        'id': connection.id,
        'from_person':
            person_json(Person.query.filter(Person.id == connection.from_person_id).one()),
        'to_person': person_json(Person.query.filter(Person.id == connection.to_person_id).one()),
        'connection_type': connection.connection_type.value
        }
        for connection in connections)), HTTPStatus.OK


@blueprint.route('/connections', methods=['POST'])
@use_args(ConnectionSchema(), locations=('json',))
def create_connection(connection):
    connection.save()
    return ConnectionSchema().jsonify(connection), HTTPStatus.CREATED


UPDATEABLE_FIELDS = ['connection_type']


@blueprint.route('/connections/<connection_id>', methods=['PATCH'])
@use_args(ConnectionUpdateSchema(), locations=('json',))
def update_connection(connection_update, connection_id):
    try:
        connection = Connection.query.filter(Connection.id == connection_id).one()
        for field in UPDATEABLE_FIELDS:
            new_value = getattr(connection_update, field, None)
            if new_value:
                setattr(connection, field, new_value)

        connection.save()
        return '', HTTPStatus.NO_CONTENT
    except NoResultFound:
        return jsonify({'description': 'Resource not found.',
                        'errors': {'connection_id': ['No connection found with this ID']}}),
        HTTPStatus.GONE
