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

        order_tag_objs = []

        for i in range(2):
            order_tag_obj = OrderTag(name=f'Tag{i+1}')
            order_tag_obj.save()

            order_tag_objs.append(order_tag_obj)

        order_tag_objs[0].orders.set(order_objs)

        # array with 2 OrderTag instances: 1st has 2 Orders, 2nd has 0 Orders
        self.test_objs = order_tag_objs

        self.max_pk = max(obj.pk for obj in order_tag_objs)

        self.client = Client()

    # helper methods

    def list_orders_for_order_tag_response(self, order_tag_id):
        return self.client.get(f'/orders/tags/{order_tag_id}/orders/')

    def assert_valid_response_and_count(self, response, expected_item_count):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), expected_item_count)

    # tests

    def test_existing_order_tag_with_orders(self):
        # OrderTag object with 2 orders
        response = self.list_orders_for_order_tag_response(self.test_objs[0].pk)
        self.assert_valid_response_and_count(response, 2)

    def test_existing_order_tag_no_orders(self):
        # OrderTag object with 0 orders
        response = self.list_orders_for_order_tag_response(self.test_objs[1].pk)
        self.assert_valid_response_and_count(response, 0)

    def test_invalid_order_tag(self):
        # invalid OrderTag ID
        response = self.list_orders_for_order_tag_response(self.max_pk + 1)
        self.assertEqual(response.status_code, 404)
