# Challenge 8 Explanation
By Ryli Dunlap

## Introduction
For this challenge, I am going to work through the problem and explain my process here as if I was mentoring a junoir developer

The scenario is that they are stuck attempting to insert a new Inventory item through the API

## Setting up a test
Let's set up a test first so that we have a way to test the endpoint. Of course, we could also use some other tool (including browser plugins) to generate POST requests, but it's a good idea to set up a test anyways.

In addition, Django's built-in testing tools automatically handle setting up and tearing down a test database on every run, so this keeps us from possibly contaminating the local database with cruft since we will be testing inserts. It also avoids the problem of having to create unique values for every POST attempt while testing in order to avoid Integrity errors due to uniqueness constraints.

If an insert is successful and we want to test it again, the previous test insert could conflict with the new insert since those values already exist.

For example, in this sample project, many of the `name` fields are unique. Rather than having to change the names in the test data for every test insert to avoid errors, we can simply take advantage of the fact that Django's testing tools will create a fresh test database instance for us on every test run.

> See `/interview/inventory/tests.py` on this branch for the test file that I have created and that we will use for this exercise.

## Adding a metadata field

The instructions for Challenge 8 list the fields that should be included in the `metadata` field. This is a JSON field that is validated using a `pydantic` model defined in `/interview/inventory/schemas.py`.

The description for Challange 8 lists a field that is not present in the schema, so let's add `film_locations`:

```python
class InventoryMetaData(BaseModel):
    year: int
    actors: list[str]
    imdb_rating: Decimal
    rotten_tomatoes_rating: int
    film_locations: list[str] # added this 
```

If we fail to add this field, then the `pydantic` validation will exclude it from the `metadata`.

> Note that the test includes a sample `film_locations` value, and checks that it is present in the inserted data

## Debugging

Let's run the test and see what happens: `./manage.py test`

Uh oh. It fails: 

```
    self.assertEqual(response.status_code, 201)
AssertionError: 400 != 201
```

The HTPP status code is something other than 201 (Created). 400 is Bad Request. We have an error somewhere, but the test output doesn't tell us anything more than that the status codes don't match.

Let's run the test again with a flag to launch [pdb](https://docs.python.org/3/library/pdb.html) on failure so we can inspect the response object: `./manage.py test --pdb`

We can type `response.json()` at the `Pdb` prompt in order to inspect the response JSON. Type `exit` to quit the debugger:

```
-> self.assertEqual(response.status_code, 201)
(Pdb) response.json()
{'metadata': ['Value must be valid JSON.']}
(Pdb) exit
```

Apparently, there's an issue with invalid JSON somethere. We'll fix that first.

### Fixing the JSON Error

Let's look at the `InventoryListCreateView` in `/interview/inventory/views.py` to determine where the JSON encoding/decoding might be failing. Let's get a better understanding of what's happening here:

```python
try:
    metadata = InventoryMetaData(**request.data['metadata'])
except Exception as e:
    return Response({'error': str(e)}, status=400)

request.data['metadata'] = metadata.dict()
serializer = self.serializer_class(data=request.data)
```

I think it's time to open a shell and step through this: `./manage.py shell`

Let's import `json` and the `InventoryMetaData` class and experiment with these using our test data:

```python
>>> import json
>>> from interview.inventory.schemas import InventoryMetaData
>>> metadata_json = '{"actors": ["Daniel Craig"], "imdb_rating": 1.5, "rotten_tomatoes_rating": 1, "year": 1995, "film_locations": ["London"]}'
>>> # DRF deserializes JSON into Python objects in the view, let's simulate that here
>>> metadata_python = json.loads(metadata_json)
>>> metadata_python
{'actors': ['Daniel Craig'], 'imdb_rating': 1.5, 'rotten_tomatoes_rating': 1, 'year': 1995, 'film_locations': ['London']}
>>> # Now let's instantiate the pydantic schema with this data
>>> imd = InventoryMetaData(**metadata_python)
>>> imd
InventoryMetaData(year=1995, actors=['Daniel Craig'], imdb_rating=Decimal('1.5'), rotten_tomatoes_rating=1, film_locations=['London'])
>>> # The next thing that happens in the view is that the .dict() method is called
>>> imd_dict = imd.dict()
>>> imd_dict
{'year': 1995, 'actors': ['Daniel Craig'], 'imdb_rating': Decimal('1.5'), 'rotten_tomatoes_rating': 1, 'film_locations': ['London']}
>>> # The view then sets this dict as the metadata key on request.data
>>> # This data is then used to instantiate a serializer class.
>>> # The serializer is using a JSON field for the metadata, which means the .dict() data
>>> # is converted back to JSON
>>> json.dumps(imd_dict)
Traceback (most recent call last):
  File "<console>", line 1, in <module>
  File "/usr/lib/python3.9/json/__init__.py", line 231, in dumps
    return _default_encoder.encode(obj)
  File "/usr/lib/python3.9/json/encoder.py", line 199, in encode
    chunks = self.iterencode(o, _one_shot=True)
  File "/usr/lib/python3.9/json/encoder.py", line 257, in iterencode
    return _iterencode(o, 0)
  File "/usr/lib/python3.9/json/encoder.py", line 179, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
TypeError: Object of type Decimal is not JSON serializable
```

There's our problem. The `.dict()` method on the `InventoryMetaData` instance is returning a field as a python `Decimal` type which is not serializable to JSON. 

Let's try something... I wonder if `pydantic` objects are able to serialize JSON directly. If so, it should be 'smart' enough to handle the serialization of the `Decimal` field gracefully since `json.dumps()` is unable to:

```python
>>> imd_json = imd.json()
>>> imd_json
'{"year": 1995, "actors": ["Daniel Craig"], "imdb_rating": 1.5, "rotten_tomatoes_rating": 1, "film_locations": ["London"]}'
```

Hey, look at that! The `pydantic` object has a method that does handle the serialization of the `Decimal` type gracefully. We should use `.json()` rather than `.dict()` on the `InventoryMetaData` instance.

However, there's still one 'gotcha' here. If we set this JSON string as the Python data to then be serialized back to JSON, it will be saved in the JSON field in the database as a JSON string containing escaped JSON!

```python
>>> # When the data is passed to the DRF serializer, it will attempt to convert the
>>> # metadata data to JSON for storage in the JSON field
>>> json.dumps(imd_json)
'"{\\"year\\": 1995, \\"actors\\": [\\"Daniel Craig\\"], \\"imdb_rating\\": 1.5, \\"rotten_tomatoes_rating\\": 1, \\"film_locations\\": [\\"London\\"]}"'
```

We want a JSON object in the JSON field --- not a JSON string of escaped JSON data!

A fix here is to convert the JSON generated by the `.json()` method back to a Python object, so that it will then be serialized by DRF correctly into a JSON object for insertion into the JSON database field:

```python
>>> json.loads(imd_json)
{'year': 1995, 'actors': ['Daniel Craig'], 'imdb_rating': 1.5, 'rotten_tomatoes_rating': 1, 'film_locations': ['London']}
>>> # If we convert to Python data, the metadata will then be correctly re-serialized
>>> # to a JSON object
>>> json.dumps(_)
'{"year": 1995, "actors": ["Daniel Craig"], "imdb_rating": 1.5, "rotten_tomatoes_rating": 1, "film_locations": ["London"]}'
```

Let's apply the fix to the approriate line in `views.py`:

```python
request.data['metadata'] = json.loads(metadata.json())
```
Don't forget to add `import json` in the imports as well.

> An alternative approach would be to just omit this line. This would still validate missing and invalid fields in the metadata, but the request data would then be used as-is if it passes the pydantic validation. This means that extra fields that might exist in the data but aren't part of the schema would make their way into the metadadata field of the database. In contrast, by altering this line, we benefit from the pydantic schema model stripping out fields and cruft that aren't part of the metadata schema

Let's re-run the test and see where we're at now: `./manage.py test`

This time we don't even need to use the debugger to inspect the response object, because we didn't even make it to that point. This exception is now raised by the view:

```
AssertionError: The `.create()` method does not support writable nested
fields by default. Write an explicit `.create()` method for serializer
`interview.inventory.serializers.InventorySerializer`, or set`read_only=True`
on nested serializer fields.
```

### Fixing the Nested Fields Error

In cases like this, documentation is your best friend. Luckily, this is a very well-known (and well-documented) issue. The DRF docs have an entire section on this topic here: https://www.django-rest-framework.org/api-guide/serializers/#dealing-with-nested-objects

That section in the docs goes on to emphasize:

> Because the behavior of nested creates and updates can be ambiguous, and may require complex dependencies between related models, REST framework 3 requires you to always write these methods explicitly. The default ModelSerializer .create() and .update() methods do not include support for writable nested representations.

So, this isn't really a bug, but rather an intentional design aspect of DRF. Essentially, because our serializer contains nested serializers representing FK relationships, we have to write this method ourselvs in order to handle the specific order in which objects should be created and inserted.

Luckily, the DRF docs have an example of how to do just this. It even shows how to handle M2M relationships, like what we have between the `Inventory` and `InventoryTag` models: https://www.django-rest-framework.org/api-guide/relations/#writable-nested-serializers

Our `Inventory` model has 2 FK relations to `InventoryType` and `InventoryLanguage`. These need to be created and saved in the database first prior to creating and saving the `Inventory` record.

The `Inventory` model also has a M2M relationship with `InventoryTag`. Once the `Inventory` record is saved, `InventoryTag` records can be created and the M2M relationship added via the intermediate table in the database used to track M2M relationships. 

The linked DRF docs show that the `create()` method that we need to add to the `InventorySerilizer` class accepts a `validated_data` argument. This object has a `.pop()` method. It's important to remove keys represting FK and M2M relationships from `validated_data` using `.pop()` before passing the remaining values as the fields to instantiate (or create) an `Inventory` object.

In other words, we need to 'pop' the keys out representing nested FK relationships, use the popped data to create and save these objects to the database in the correct order, and then pass the created objects (or their Pks) as the arguments when instantiating or creating the `Inventory` object.

You should end up with a function like this added to `InventorySerializer` in `/interview/inventory/serializers.py`:

```python
def create(self, validated_data):
        # pop the nested relation data from the validated_data
        inventory_type_data = validated_data.pop('type')
        language_data = validated_data.pop('language')
        tags_data = validated_data.pop('tags')

        # create these two related objects that Inventory references
        inventory_type_obj = InventoryType.objects.create(**inventory_type_data)
        language_obj = InventoryLanguage.objects.create(**language_data)

        # create the Inventory object now that the relations are created
        inventory_obj = Inventory.objects.create(
            type=inventory_type_obj,
            language=language_obj,
            **validated_data
        )

        # now create the m2m relations
        for tag_data in tags_data:
            inventory_obj.tags.create(**tag_data)

        return inventory_obj
```

Now let's run the test again with that function in place: `./manage.py test`

```
Found 1 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.
----------------------------------------------------------------------
Ran 1 test in 0.022s

OK
Destroying test database for alias 'default'...
```

That's what we want to see!

Now that the serializer 'knows' how to handle the nested relationships thanks to our custom implementation of `create()`, it is able to insert the data into the database from a POST request via the API.
