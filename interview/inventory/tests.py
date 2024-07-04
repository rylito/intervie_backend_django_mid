import datetime
from django.test import TestCase, Client
from interview.inventory.models import Inventory, InventoryType, InventoryLanguage


def fmt_date_offset(timestamp, days_offset=0):
    adjusted_datetime = timestamp + datetime.timedelta(days=days_offset)
    return adjusted_datetime.strftime('%Y-%m-%d')


def list_inventory_response(after_date_param_val=None):
    params = {}

    if after_date_param_val is not None:
        params['after_date'] = after_date_param_val

    response = Client().get('/inventory/', params)

    return response.json()


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

    def test_list_params_no_arg(self):
        # test no argument, verify 1 test object exists
        items = list_inventory_response()
        self.assertEqual(len(items), 1)

    def test_list_params_earlier(self):
        # test with a day earlier than the creation date
        day_before = fmt_date_offset(self.test_obj.created_at, -1)
        items = list_inventory_response(day_before)
        self.assertEqual(len(items), 1)

    def test_list_params_later(self):
        # test with a day later than the creation date
        day_after = fmt_date_offset(self.test_obj.created_at, +1)
        items = list_inventory_response(day_after)
        self.assertEqual(len(items), 0)

    def test_list_params_invalid(self):
        # test invalid date format - should ignore param and list all items
        items = list_inventory_response('invalid_value')
        self.assertEqual(len(items), 1)




