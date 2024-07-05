import datetime
from django.test import TestCase, Client
from interview.inventory.models import Inventory, InventoryType, InventoryLanguage
from interview.order.models import Order, OrderTag


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

        order_objs = []

        for _ in range(2):
            order_obj = Order()
            order_obj.inventory = inventory_obj
            order_obj.start_date = datetime.date.today()
            order_obj.embargo_date = order_obj.start_date + datetime.timedelta(days=30)
            order_obj.save()

            order_objs.append(order_obj)

        for i in range(5):
            order_objs[0].tags.create(name=f"Tag{i+1}")

        # array with 2 Order instances: 1st has 5 tags, 2nd has 0 tags
        self.test_objs = order_objs

        self.max_pk = max(obj.pk for obj in order_objs)

        self.client = Client()

    # helper methods

    def list_order_tags_for_order_response(self, order_id, approach, tags_required=False):
        url = f'/orders/{order_id}/tags-{approach}/'

        if tags_required:
            url += '?tags_required=1'

        return self.client.get(url)

    def assert_valid_response_and_count(self, response, expected_item_count):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), expected_item_count)

    # tests

    # approach 1

    def test_existing_order_with_tags_approach_1(self):
        # order object with 5 tags, 1st implementation
        response = self.list_order_tags_for_order_response(self.test_objs[0].pk, 1)
        self.assert_valid_response_and_count(response, 5)

    def test_existing_order_no_tags_approach_1(self):
        # order object with 0 tags, 1st implementation
        response = self.list_order_tags_for_order_response(self.test_objs[1].pk, 1)
        self.assert_valid_response_and_count(response, 0)

    def test_invalid_order_approach_1(self):
        # invalid order ID, 1st implementation
        response = self.list_order_tags_for_order_response(self.max_pk + 1, 1)
        self.assertEqual(response.status_code, 404)

    # approach 2: tags_required=False

    def test_existing_order_with_tags_approach_2(self):
        # order object with 5 tags, 2nd implementation: tags_required=False
        response = self.list_order_tags_for_order_response(self.test_objs[0].pk, 2)
        self.assert_valid_response_and_count(response, 5)

    def test_existing_order_no_tags_approach_2(self):
        # order object with 0 tags, 2nd implementation: tags_required=False
        response = self.list_order_tags_for_order_response(self.test_objs[1].pk, 2)
        self.assert_valid_response_and_count(response, 0)

    def test_invalid_order_approach_2(self):
        # invalid order ID, 2nd implementation: tags_required=False
        response = self.list_order_tags_for_order_response(self.max_pk + 1, 2)
        self.assert_valid_response_and_count(response, 0) # will return empty, not 404

    # approach 2: tags_required=True

    def test_existing_order_with_tags_approach_2_tags_required(self):
        # order object with 5 tags, 2nd implementation: tags_required=True
        response = self.list_order_tags_for_order_response(self.test_objs[0].pk, 2, True)
        self.assert_valid_response_and_count(response, 5)

    def test_existing_order_no_tags_approach_2_tags_required(self):
        # order object with 0 tags, 2nd implementation: tags_required=True
        response = self.list_order_tags_for_order_response(self.test_objs[1].pk, 2, True)
        self.assertEqual(response.status_code, 404) # will raise 404

    def test_invalid_order_approach_2_tags_required(self):
        # invalid order ID, 2nd implementation: tags_required=True
        response = self.list_order_tags_for_order_response(self.max_pk + 1, 2, True)
        self.assertEqual(response.status_code, 404) # will raise 404
