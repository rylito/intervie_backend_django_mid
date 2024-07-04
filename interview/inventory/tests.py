import datetime
from django.test import TestCase, Client
from interview.inventory.models import Inventory, InventoryType, InventoryLanguage


class InventoryTestCase(TestCase):
    def setUp(self):
        inventory_type_obj = InventoryType(name='Movie')
        inventory_type_obj.save()

        inventory_language_obj = InventoryLanguage(name='English')
        inventory_language_obj.save()

        inventory_obj = Inventory()
        inventory_obj.type = inventory_type_obj
        inventory_obj.language = inventory_language_obj
        inventory_obj.metadata = ''
        inventory_obj.save()

        self.test_obj = inventory_obj
        self.client = Client()

    # helper methods

    def fmt_date_offset(self, days_offset=0):
        adjusted_datetime = self.test_obj.created_at + datetime.timedelta(days=days_offset)
        return adjusted_datetime.strftime('%Y-%m-%d')

    def list_inventory_response(self, after_date_param_val=None):
        params = {}

        if after_date_param_val is not None:
            params['after_date'] = after_date_param_val

        response = self.client.get('/inventory/', params)

        return response

    def assert_valid_response_and_count(self, response, expected_item_count):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), expected_item_count)

    # tests

    def test_list_params_no_arg(self):
        # test no argument, verify 1 test object exists
        response = self.list_inventory_response()
        self.assert_valid_response_and_count(response, 1)

    def test_list_params_earlier(self):
        # test with a day earlier than the creation date
        day_before = self.fmt_date_offset(-1)
        response = self.list_inventory_response(day_before)
        self.assert_valid_response_and_count(response, 1)

    def test_list_params_later(self):
        # test with a day later than the creation date
        day_after = self.fmt_date_offset(+1)
        response = self.list_inventory_response(day_after)
        self.assert_valid_response_and_count(response, 0)

    def test_list_params_invalid(self):
        # test invalid date format - should return status code of 400
        response = self.list_inventory_response('invalid_value')
        self.assertEqual(response.status_code, 400)




