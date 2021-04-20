from http import HTTPStatus

from flask import Blueprint, jsonify
from webargs.flaskparser import use_args

from connections.models.connection import Connection
from connections.models.person import Person
from connections.schemas import ConnectionSchema, PersonSchema

blueprint = Blueprint('connections', __name__)


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
    # TODO: is many needed here?
    connection_schema = ConnectionSchema(many=True)
    people_schema = PersonSchema(many=True)
    connections = Connection.query.all()
    person_json = lambda p: dict([(f, getattr(p, f)) for f in ['id', 'first_name', 'last_name', 'email']])

    # It didn't seem to make sense to alter the schema just to get an expanded representation of a person
    return jsonify(list({
        'id': connection.id,
        'from_person': person_json(Person.query.filter(Person.id==connection.from_person_id).one()),
        'to_person': person_json(Person.query.filter(Person.id==connection.to_person_id).one()),
        'connection_type': connection.connection_type.value
    }
    for connection in connections)), HTTPStatus.OK


@blueprint.route('/connections', methods=['POST'])
@use_args(ConnectionSchema(), locations=('json',))
def create_connection(connection):
    connection.save()
    return ConnectionSchema().jsonify(connection), HTTPStatus.CREATED
