import datetime
from django.test import TestCase, Client
from interview.inventory.models import Inventory, InventoryType, InventoryLanguage
from interview.order.models import Order


class OrderTestCase(TestCase):
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

        order_obj = Order()
        order_obj.inventory = inventory_obj
        order_obj.start_date = datetime.date.today()
        order_obj.embargo_date = order_obj.start_date + datetime.timedelta(days=30)
        order_obj.save()

        self.test_obj = order_obj
        self.client = Client()

    # helper methods

    def fmt_date_offset(self, base_date, days_offset=0):
        adjusted_date = base_date + datetime.timedelta(days=days_offset)
        return adjusted_date.strftime('%Y-%m-%d')

    def list_order_response(self, start_date=None, embargo_date=None):
        params = {}

        for param_key in ('start_date', 'embargo_date'):
            param_val = locals()[param_key]

            if param_val is not None:
                params[param_key] = param_val

        return self.client.get(f'/orders/', params)

    def assert_valid_response_and_count(self, response, expected_item_count):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), expected_item_count)

    # tests

    def test_order_list_range_no_params(self):
        # test no parameters, verify 1 test object is returned
        response = self.list_order_response()
        self.assert_valid_response_and_count(response, 1)

    def test_order_list_range_start_inclusive_no_embargo(self):
        # test only start_date, ensure that inclusive behavior works
        start_date = self.fmt_date_offset(self.test_obj.start_date)
        response = self.list_order_response(start_date=start_date)
        self.assert_valid_response_and_count(response, 1)

    def test_order_list_range_start_later_no_embargo(self):
        # test only start_date, ensure that objects with a start_date < than the param are filtered out
        start_date = self.fmt_date_offset(self.test_obj.start_date, +1)
        response = self.list_order_response(start_date=start_date)
        self.assert_valid_response_and_count(response, 0)

    def test_order_list_range_no_start_embargo_exclusive(self):
        # test only embargo_date, ensure that exclusive behavior works
        embargo_date = self.fmt_date_offset(self.test_obj.embargo_date, +1)
        response = self.list_order_response(embargo_date=embargo_date)
        self.assert_valid_response_and_count(response, 1)

    def test_order_list_range_no_start_embargo_earlier(self):
        # test only embargo_date, ensure that objects with an embargo_date >= than the param are filtered out
        embargo_date = self.fmt_date_offset(self.test_obj.embargo_date)
        response = self.list_order_response(embargo_date=embargo_date)
        self.assert_valid_response_and_count(response, 0)

    def test_order_list_range_both_params_match(self):
        # test both params defining a range that matches the test obj
        start_date = self.fmt_date_offset(self.test_obj.start_date)
        embargo_date = self.fmt_date_offset(self.test_obj.embargo_date, +1)
        response = self.list_order_response(start_date=start_date, embargo_date=embargo_date)
        self.assert_valid_response_and_count(response, 1)

    def test_order_list_range_both_params_no_match_start(self):
        # test both params defining a range that does not match the test obj
        # set start date of range 1 day later than obj
        start_date = self.fmt_date_offset(self.test_obj.start_date, +1)
        embargo_date = self.fmt_date_offset(self.test_obj.embargo_date, +1)
        response = self.list_order_response(start_date=start_date, embargo_date=embargo_date)
        self.assert_valid_response_and_count(response, 0)

    def test_order_list_range_both_params_no_match_embargo(self):
        # test both params defining a range that does not match the test obj
        # set emabargo (end) date of range == to obj. This should exclude the obj due to exclusive behavior
        start_date = self.fmt_date_offset(self.test_obj.start_date)
        embargo_date = self.fmt_date_offset(self.test_obj.embargo_date)
        response = self.list_order_response(start_date=start_date, embargo_date=embargo_date)
        self.assert_valid_response_and_count(response, 0)

    def test_invalid_param_vals(self):
        # test invalid date formats for both params - should return status code of 400
        for param_key in ('start_date', 'embargo_date'):
            response = self.list_order_response(**{param_key: 'invalid_value'})
            self.assertEqual(response.status_code, 400)
