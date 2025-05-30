"""
This module contains tests for the inventory app's models.
"""

import datetime
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time

from django.contrib.auth.models import User, Group
from inventory.models import Item, ItemHistory, ItemRequest, PurchaseOrderItem, UsedItem


class ItemModelTests(TestCase):
    """
    Tests for Item model
    """
    @classmethod
    def setUpTestData(cls):
        cls.item1 = Item.objects.create(
            manufacturer="Test MFG1",
            model="Test Model1",
            part_or_unit=Item.UNIT,
            quantity=1,
            unit_price=100.00,
        )
        cls.item2 = Item.objects.create(
            manufacturer="Test MFG2",
            model="Test Model2",
            part_or_unit=Item.PART,
            quantity=5,
            min_quantity=10,
            unit_price=0.50,
        )
        cls.item3 = Item.objects.create(
            manufacturer="Test MFG3",
            model="Test Model3",
            part_or_unit=Item.PART,
            part_number="Test Part Number",
        )

        cls.technician_group = Group.objects.get(name="Technician")

        cls.user = User.objects.create_user(
            username="testtechnician", password="password"
        )
        cls.user.groups.add(cls.technician_group)

        cls.client = Client()

    def test_item_unit(self):
        """
        Test that an item (unit) can be created.
        """
        self.assertTrue(isinstance(self.item1, Item))
        self.assertEqual(str(self.item1), "Test MFG1, Test Model1")

    def test_create_item_part_blankpartnumber(self):
        """
        Test that an item (part) can be created without a part number.
        """
        self.assertTrue(isinstance(self.item2, Item))
        self.assertEqual(str(self.item2), "Test MFG2, Test Model2 ")

    def test_create_item_part_nonblankpartnumber(self):
        """
        Test that an item (part) can be created with a part number.
        """
        self.assertTrue(isinstance(self.item3, Item))
        self.assertEqual(
            str(self.item3), "Test MFG3, Test Model3 Test Part Number"
        )

    def test_item_quantity(self):
        """
        Test that the item quantity is correct.

        For the first item, this should be 1.
        For the second item, this should be 5.
        For the third item, this should be 0 as it was not specified upon creation.
        """
        self.assertEqual(
            self.item1.quantity,
            1,
            "The quantity of the first item should be 1.",
        )
        self.assertEqual(
            self.item2.quantity,
            5,
            "The quantity of the second item should be 5.",
        )
        self.assertEqual(
            self.item3.quantity,
            0,
            "The quantity of the third item should be 0 (default value).",
        )

    def test_item_is_low_stock(self):
        """
        Test that an item low in stock has its property `low_stock` set as True.
        """
        self.assertTrue(self.item2.low_stock)

    def test_item_is_not_low_stock(self):
        """
        Test that an item not low in stock has its property `low_stock` set as False.
        """
        self.assertFalse(self.item1.low_stock)

    def test_item_unit_price(self):
        """
        Test that the item unit price is correct.

        For the first item, this should be 100.00.
        For the secod item, this should be 0.50.
        For the third item, this should be 0.01 becuase a price hasn't been specified for creation.
        """
        self.assertEqual(
            self.item1.unit_price,
            100.00,
            "The unit price of the first item should be 100.00.",
        )
        self.assertEqual(
            self.item2.unit_price,
            0.50,
            "The unit price of the second item should be 0.50.",
        )
        self.assertEqual(
            float(self.item3.unit_price),
            0.01,
            "Thie unit price of the third item should be 0.01 (the default value).",
        )

    def test_item_model_part_num(self):
        """
        Test that the `model_part_num` property is correctly set.

        For the first item, this should be "Test Model1 ". 
            (Space included because it's a unit.)
        For the second item, this should be "Test Model2 ". 
            (Space include because no part number has been specified.)
        For the third item, this should be "Test Model3 Test Part Number".
        """
        self.assertEqual(
            self.item1.model_part_num,
            "Test Model1 ",
            "The model_part_num property of the first item should be 'Test Model1 '.",
        )
        self.assertEqual(
            self.item2.model_part_num,
            "Test Model2 ",
            "The model_part_num property of the second item should be 'Test Model2 '.",
        )
        self.assertEqual(
            self.item3.model_part_num,
            "Test Model3 Test Part Number",
            "The model_part_num property of the third item should be 'Test Model3 Test Part Number'.",
        )

    def test_get_absolute_urls(self):
        """
        Get the absolute urls of all three items.
        """
        expected_url1 = reverse("inventory:item_detail", kwargs={"pk": self.item1.pk})
        self.assertEqual(
            self.item1.get_absolute_url(),
            expected_url1,
            "The absolute URL of the first item should be " + expected_url1,
        )
        expected_url2 = reverse("inventory:item_detail", kwargs={"pk": self.item2.pk})
        self.assertEqual(
            self.item2.get_absolute_url(),
            expected_url2,
            "The absolute URL of the second item should be " + expected_url2,
        )
        expected_url3 = reverse("inventory:item_detail", kwargs={"pk": self.item3.pk})
        self.assertEqual(
            self.item3.get_absolute_url(),
            expected_url3,
            "The absolute URL of the third item should be " + expected_url3,
        )

    def test_last_modified_by_none(self):
        """
        The `last_modified_by` field is set to None since no user has been signed in.
        """
        self.assertEqual(
            self.item1.last_modified_by,
            None,
            "The last_modofied_by field of the first item should be None.",
        )
        self.assertEqual(
            self.item2.last_modified_by,
            None,
            "The last_modofied_by field of the second item should be None.",
        )
        self.assertEqual(
            self.item3.last_modified_by,
            None,
            "The last_modofied_by field of the third item should be None.",
        )

    def test___str__(self):
        """
        String representation is printed in the expected format.
        """
        self.assertEqual(
            str(self.item1),
            "Test MFG1, Test Model1",
            "The string representation does not match.",
        )
        self.assertEqual(
            str(self.item2),
            "Test MFG2, Test Model2 ",
            "The string representation does not match.",
        )
        self.assertEqual(
            str(self.item3),
            "Test MFG3, Test Model3 Test Part Number",
            "The string representation does not match.",
        )


class ItemHistoryModelTests(TestCase):
    """
    Tests for ItemHistory model
    """
    # NOTE: Date and time is set to January 1, 2025 at 12:00 for testing purposes
    aware_datetime = timezone.make_aware(datetime.datetime(2025, 1, 1, 12, 0, 0))

    @classmethod
    @freeze_time(aware_datetime)
    def setUpTestData(cls):
        """
        Set up for ItemHistoryModelTests
        """
        Item.objects.create(
            manufacturer="Test MFG1",
            model="Test Model1",
            part_or_unit=Item.UNIT,
            quantity=1,
            unit_price=100.00,
        )
        Item.objects.create(
            manufacturer="Test MFG2",
            model="Test Model2",
            part_or_unit=Item.PART,
            quantity=5,
            min_quantity=10,
            unit_price=0.50,
        )
        Item.objects.create(
            manufacturer="Test MFG3",
            model="Test Model3",
            part_or_unit=Item.PART,
            part_number="Test Part Number",
        )

        cls.item1 = Item.objects.get(id=1)
        cls.item2 = Item.objects.get(id=2)
        cls.item3 = Item.objects.get(id=3)

        cls.item_history1 = ItemHistory.objects.filter(item=cls.item1)
        cls.item_history2 = ItemHistory.objects.filter(item=cls.item2)
        cls.item_history3 = ItemHistory.objects.filter(item=cls.item3)

        cls.item1_use_url = reverse("inventory:item_use_form")

        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.user.groups.add(Group.objects.get(name="Superuser"))

        cls.client = Client()

    def test_history_action_create(self):
        """
        Make sure each created item has a history record of being created.
        """
        self.assertEqual(
            len(self.item_history1),
            1,
            "The history of the first item should only have 1 record.",
        )
        self.assertEqual(
            str(self.item_history1[0]),
            "Test MFG1, Test Model1 - create - 2025-01-01 12:00:00 PM",
        )
        self.assertEqual(
            len(self.item_history2),
            1,
            "The history of the second item should only have 1 record.",
        )
        self.assertEqual(
            str(self.item_history2[0]),
            "Test MFG2, Test Model2  - create - 2025-01-01 12:00:00 PM",
        )
        self.assertEqual(
            len(self.item_history3),
            1,
            "The history of the third item should only have 1 record.",
        )
        self.assertEqual(
            str(self.item_history3[0]),
            "Test MFG3, Test Model3 Test Part Number - create - 2025-01-01 12:00:00 PM",
        )

    def test_history_action_update(self):
        """
        Update an item and check their history records for the update
        """
        self.item1.manufacturer = "Fluke"
        self.item1.save(user=self.user)

        self.assertIsNotNone(self.item_history1, "The item's history doesn't exist.")
        self.assertEqual(
            self.item_history1[1].action,
            "update",
            f"The action for this record should be 'update'. It is actually {self.item_history1[1].action}.",
        )
        self.assertEqual(
            self.item_history1[1].user,
            self.user,
            f"The user responsible for the creation should be {self.user}. It is actually {self.item_history1[1].user}.",
        )
        self.assertEqual(
            self.item_history1[1].changes,
            "manufacturer: 'Test MFG1' has been changed to 'Fluke'",
            "The changes field does not match the expected value.",
        )

    def test_history_action_use(self):
        """
        Use an item and check their history records for the use
        """
        self.client.login(username="testuser", password="password")
        response = self.client.post(
            self.item1_use_url + f"?item_id={self.item1.id}",
            data={"item": self.item1.id, "work_order": "1234567"},
        )

        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        self.assertEqual(response.status_code, 302, "Failed to use the item.")

        self.item1.refresh_from_db()
        self.assertEqual(
            self.item1.quantity,
            0,
            "The quantity of the item should have decremented to 0 after use.",
        )

        item_history = (
            ItemHistory.objects.filter(item=self.item1).order_by("-timestamp").first()
        )
        used_item = UsedItem.objects.filter(item=self.item1).first()
        used_item_url = reverse(
            "inventory:used_item_detail", kwargs={"pk": used_item.pk}
        )

        self.assertIsNotNone(item_history, "The item's history doesn't exist.")
        self.assertEqual(
            item_history.action,
            "use",
            f"The action for this record should be 'use'. It is actually {item_history.action}.",
        )
        self.assertEqual(
            item_history.user,
            self.user,
            f"The user responsible for the creation should be {self.user}. It is actually {item_history.user}.",
        )
        self.assertEqual(
            item_history.changes,
            f"quantity: '1' has been changed to '0', <a href=\"{used_item_url}\">Item used in work order {used_item.work_order}</a>",
            "The changes field does not match the expected value.",
        )


class ItemRequestModelTests(TestCase):
    """
    Tests for ItemRequest model
    """
    # NOTE: Date and time is set to January 1, 2025 at 12:00 for testing purposes
    aware_datetime = timezone.make_aware(datetime.datetime(2025, 1, 1, 12, 0, 0))

    @classmethod
    @freeze_time(aware_datetime)
    def setUpTestData(cls):
        """
        Setup
        """
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.user.groups.add(Group.objects.get(name="Superuser"))

        ItemRequest.objects.create(
            manufacturer="Test MFG",
            model_part_num="Test Model and Part Num",
            quantity_requested=1,
            # description will be blank
            unit_price=0.01,
            requested_by=cls.user,
            # timestamp is set automatically
            # status set to "Pending" as default
            # status_changed_by is None
        )

        cls.item_request = ItemRequest.objects.filter(pk=1).first()

    def test_get_absolute_url(self):
        """
        Test that the get_absolute_url method returns the correct URL.
        """
        expected_url = "/inventory_database/item_requests/1"
        actual_url = self.item_request.get_absolute_url()

        self.assertEqual(
            actual_url,
            expected_url,
            "URL for the ItemRequest object doesn't match the expected URL.",
        )

    def test___str__(self):
        """
        Test that the string representation of the ItemRequest object is correct.
        """
        expected_string = "Request by testuser for Test MFG, Test Model and Part Num"
        actual_string = str(self.item_request)

        self.assertEqual(
            actual_string,
            expected_string,
            "The string for the ItemRequest object doesn't match the expected string.",
        )


class UsedItemModelTests(TestCase):
    """
    Tests for UsedItem model
    """
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.user.groups.add(Group.objects.get(name="Superuser"))

        cls.item = Item.objects.create(
            manufacturer="Test MFG",
            model="Test Model",
            part_or_unit=Item.UNIT,
            # Item is a unit, no part number required.
            # description will be blank
            # location will be blank
            quantity=2,
            # min_quantity will be set to 0
            # unit_price will be set to 0.01
            # last_modified_by will be set to None
        )

        cls.used_item = UsedItem.objects.create(
            item=cls.item,
            work_order=1234567,
            # datetime_used is set automatically
            used_by=cls.user,
        )

    def test_get_absolute_url(self):
        """
        Test that the get_absolute_url method returns the correct URL.
        """
        expected_url = "/inventory_database/used_items/1/"
        actual_url = self.used_item.get_absolute_url()

        self.assertEqual(
            actual_url,
            expected_url,
            "URL for the UsedItem object doesn't match the expected URL.",
        )

    def test___str__(self):
        """
        Test that the string representation of the PurchaseOrderItem object is correct.
        """
        expected_string = "Work Order: 1234567 | Item: Test MFG, Test Model"
        actual_string = str(self.used_item)

        self.assertEqual(
            actual_string,
            expected_string,
            "The string for the UsedItem object doesn't match the expected string.",
        )


class PurchaseOrderItemModelTests(TestCase):
    """
    Tests for PurchaseOrderItem model
    """
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        PurchaseOrderItem.objects.create(
            manufacturer="Test MFG",
            model_part_num="Test Model and Part Num",
            quantity_ordered=1,
            # description will be blank
            # serial_num will be blank
            # property_num will be blank
            unit_price=0.01,
        )

        cls.po_item = PurchaseOrderItem.objects.filter(pk=1).first()

    def test___str__(self):
        """
        Test that the string representation of the PurchaseOrderItem object is correct.
        """
        expected_string = "Purchase Order for Test Model and Part Num by Test MFG - Quantity: 1"
        actual_string = str(self.po_item)

        self.assertEqual(
            actual_string,
            expected_string,
            "The string for the PurchaseOrderItem object doesn't match the expected string.",
        )
