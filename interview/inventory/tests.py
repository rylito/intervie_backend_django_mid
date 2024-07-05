from django.test import TestCase, Client
from interview.inventory.models import Inventory


class OrderTestCase(TestCase):

    def test_add_inventory_item_through_api(self):

        insert_data = {
            'name': 'test_name',
            'type': {'name': 'test_type_name'},
            'language': {'name': 'test_language_name'},
            'tags': [
                {'name': 'test_tag_name_1', 'is_active': True},
                {'name': 'test_tag_name_2', 'is_active': True}
            ],
            'metadata': {
                'actors': ['Daniel Craig'],
                'imdb_rating': 1.5,
                'rotten_tomatoes_rating': 1,
                'year': 1995,
                'film_locations': ['London']
            }
        }

        response = Client().post('/inventory/', insert_data, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Inventory.objects.count(), 1)

        self.assertTrue('film_locations' in response.json()['metadata'])
