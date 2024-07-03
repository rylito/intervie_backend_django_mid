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

        self.client = Client()
        self.test_obj = inventory_obj

    def fmt(self, timestamp):
        return timestamp.strftime('%Y-%m-%d')

    def test_no_arg(self):
        # test no argument, verify 1 test object exists
        response = self.client.get('/inventory/')
        items = response.json()
        self.assertEqual(len(items), 1)

    def test_earlier(self):
        # test with a day earlier than the creation date
        day_before = self.test_obj.created_at - datetime.timedelta(days=1)
        response = self.client.get('/inventory/', {'after_date': self.fmt(day_before)})
        items = response.json()
        self.assertEqual(len(items), 1)

    def test_later(self):
        # test with a day later than the creation date
        day_after = self.test_obj.created_at + datetime.timedelta(days=1)
        response = self.client.get('/inventory/', {'after_date': self.fmt(day_after)})
        items = response.json()
        self.assertEqual(len(items), 0)

    def test_invalid(self):
        # test invalid date format - should ignore param and list all items
        response = self.client.get('/inventory/', {'after_date': 'invalid_format'})
        items = response.json()
        self.assertEqual(len(items), 1)




