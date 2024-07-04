from django.test import TestCase, Client
from interview.inventory.models import Inventory, InventoryType, InventoryLanguage


class InventoryTestCase(TestCase):
    def setUp(self):
        inventory_type_obj = InventoryType(name='Movie')
        inventory_type_obj.save()

        inventory_language_obj = InventoryLanguage(name='English')
        inventory_language_obj.save()

        # create 10 records to test pagination - for this test it doesn't matter if they are all identical
        for _ in range(10):
            inventory_obj = Inventory()
            inventory_obj.type = inventory_type_obj
            inventory_obj.language = inventory_language_obj
            inventory_obj.metadata = ''
            inventory_obj.save()

        self.test_obj = inventory_obj
        self.client = Client()

    # helper methods

    def list_inventory_response(self, limit=None, offset=None):
        params = {}

        for key_name in ('limit', 'offset'):
            val = locals()[key_name]
            if val is not None:
                params[key_name] = val

        response = self.client.get('/inventory/', params)

        return response

    def assert_valid_response_and_count(self, response, expected_item_count, has_prev=False, has_next=False):
        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data['results']), expected_item_count)
        self.assertEqual(data['previous'] is not None, has_prev)
        self.assertEqual(data['next'] is not None, has_next)

    # tests

    def test_inventory_pagination_no_args(self):
        # no limit param should default to 3
        response = self.list_inventory_response()
        self.assert_valid_response_and_count(response, 3, has_next=True)

    def test_inventory_pagination_next_page(self):
        # test fetching the next page by setting the offset
        response = self.list_inventory_response(offset=3)
        self.assert_valid_response_and_count(response, 3, has_prev=True, has_next=True)

    def test_inventory_pagination_last_page(self):
        # test the last page
        response = self.list_inventory_response(offset=9)
        self.assert_valid_response_and_count(response, 1, has_prev=True)

    def test_inventory_pagination_different_limit(self):
        # test using a different limit param
        response = self.list_inventory_response(limit=5)
        self.assert_valid_response_and_count(response, 5, has_next=True)
