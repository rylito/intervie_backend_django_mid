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

    def deactivate_order_response(self, order_id):
        return self.client.patch(f'/orders/deactivate/{order_id}/')

    # tests

    def test_order_deactivated(self):
        # ensure initial state of test_obj.is_active = true
        self.assertTrue(self.test_obj.is_active)

        response = self.deactivate_order_response(self.test_obj.pk)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_active'])

    def test_order_not_found(self):
        # use a pk value that is different than self.test_obj
        invalid_pk = self.test_obj.pk + 1

        response = self.deactivate_order_response(invalid_pk)
        self.assertEqual(response.status_code, 404)
