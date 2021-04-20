from http import HTTPStatus

from tests.factories import ConnectionFactory, PersonFactory
from tests.functional.people.test_get_people import EXPECTED_FIELDS


def test_can_get_mutual_friends(db, testapp):
    instance = PersonFactory()
    target = PersonFactory()

    # some decoy connections (not mutual)
    ConnectionFactory.create_batch(5, to_person=instance)
    ConnectionFactory.create_batch(5, to_person=target)

    mutual_friends = PersonFactory.create_batch(3)
    for f in mutual_friends:
        ConnectionFactory(from_person=instance, to_person=f, connection_type='friend')
        ConnectionFactory(from_person=target, to_person=f, connection_type='friend')

    # mutual connections, but not friends
    decoy = PersonFactory()
    ConnectionFactory(from_person=instance, to_person=decoy, connection_type='coworker')
    ConnectionFactory(from_person=target, to_person=decoy, connection_type='coworker')

    db.session.commit()

    res = testapp.get(f'/people/{instance.id}/mutual_friends?target_id={target.id}')

    assert res.status_code == HTTPStatus.OK

    for person in res.json:
        for field in EXPECTED_FIELDS:
            assert field in person

    assert len(res.json) == 3

    # This might make sense as a separate test, probably ideally in the unit tests, not here
    switched_res = testapp.get(f'/people/{target.id}/mutual_friends?target_id={instance.id}')

    assert set([p['id'] for p in res.json]) == set([p['id'] for p in switched_res.json])
