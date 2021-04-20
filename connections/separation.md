# Six degreees of separation

## The Task

> There is a feature request to add to some functionality based on the “six degrees of separation” concept (https://en.wikipedia.org/wiki/Six_Degrees_of_Kevin_Bacon) where given a valid person id and an integer x representing “degrees of separation” it should return a list of people connected within x degrees of separation to that person.
>  - Without writing any code, spec out an endpoint for the above and provide documentation (markdown is fine)
>  - Briefly outline any potential technical challenges with implementing this endpoint. What approach would you recommend for someone trying to implement it? Are there any questions you would ask the Product Owner that would affect your proposed solution?

----

Since we don't have an existing pattern for documenting our API in this project, I'm using this document for both API documentation and discussion of how this feature might be implemented.

## Concerns

The immediate implementation concern would be preventing an infinite loop through repeatedly bouncing between the same people as we traverse the connections graph. Keeping a list of visited people, and ignoring them if they are encountered later should avoid this, as well as ensuring that people are always returned only at the lowest possible degree of separation. 

In general, this seems like a task that could be split up and executed across multiple workers, though that's not likely to be necessary at 6 maximum degrees of separation. That could change if we end up with a massive amount of users with 1000s of connections. However, if the work of traversing the connections graph is handed off to multiple workers, it will make tracking already visited people more complex.

Further on the topic of performance, it shouldn't be too difficult to allow this endpoint to stream results as they are found, rather than waiting for them all at once.

## Questions

 - Do we only want to return the people who are exactly X degrees separated, are all people up to and including that many degrees of separation? (ASSUMPTION: Yes)
   - If Yes: do we strip out people who were found at earlier degrees of separation? (Bob is friends with Sarah and Meg, who are also friends. Does Bob have any 2 degree separations, or only 1 degree?) (ASSUMPTION: Yes)
   - If No: do we need to return the degree of separation along with each person?
 - Is there a maximum supported degrees of separation? (ASSUMPTION: 6)

## API

This seems like it should be implemented similar to mutual_friends:

`/people/<person_id>/connections?degrees_of_separation=<degrees>`

Given a valid `person_id` and an integer between 1 and 6 `degrees`, return all people who are connected to them through exactly `degrees` number of people. Note that this includes the connected person, so 1 degree of separation is people who are directly connected. The result is a list of People, similar to:

```json
[
    {
        "id": 1,
        "first_name": "Alec",
        "last_name": "Munro",
        "email": "alecmunro@gmail.com"
    },
    {...},
    {...},
    ...
]
```

## Implementation

This looks like it would probably work:

```python

def extract_people(person, visited, degrees):
    results = []
    for connection in person.connections:
        if connection.to_person not in visited:
            visited.append(person)
            if degrees == 1:
                results.append(connection.to_person)
            else:
                results.extend(extract_people(connection.to_person, visited, degrees-1))

    return results
            

connections = extract_people(person, [person], 6)
```

On further pondering, it does have a problem because it traverses the graph like a tree, which could lead to the wrong results depending on order. For instance, given these people connected as follows:

 - Bob
   - Sally
     - Jeff
   - Jeff

If we ask for 2 degrees of separation from Bob, we should get no one. However, if it traverses Sally before Jeff when looking through Bob's connections, then it will record Jeff as a valid 2 degree connection, whereas if Jeff gets traversed before Sally, he goes into the already visited list and won't be looked at when Sally is traversed.

This points towards a need to complete traversing each degree of separation before moving to the next one. That is, in the example above, we need to look at Jeff and Sally before moving on to their connections. I think an implementation of that might look something like this:

```python

def extract_people(person, degrees):
    candidates = [person]
    visited = Set()
    for _ in range degrees:
        candidates = {connection.to_person
            for connection in person.connections
            for person in candidates
            if connection.to_person not in visited}
        visited.update(candidates)

    return candidates
            
connections = extract_people(person, 6)
```
