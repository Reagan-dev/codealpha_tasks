from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from inventory.models import InventoryItem, MenuItemIngredient
from inventory.utils import get_daily_sales_report
from menu.models import Category, MenuItem
from reservations.models import Reservation, RestaurantTable
from reservations.serializers import ReservationCreateSerializer

from .models import Order, OrderItem


User = get_user_model()


def create_user(email, role=User.Role.CUSTOMER):
    """Create a user with the role needed by the test."""
    return User.objects.create_user(
        username=email.split("@")[0],
        email=email,
        password="StrongPass123!",
        role=role,
    )


def create_category(name="Mains"):
    """Create a menu category for test menu items."""
    return Category.objects.create(
        name=name,
        description=f"{name} category",
    )


def create_menu_item(
    name="Jollof Rice",
    price=Decimal("10.00"),
    is_available=True,
):
    """Create a menu item with a fresh category."""
    return MenuItem.objects.create(
        name=name,
        description=f"{name} description",
        category=create_category(name=f"{name} Category"),
        price=price,
        is_available=is_available,
        preparation_time=20,
    )


def create_inventory_link(
    menu_item,
    stock=Decimal("10.00"),
    reorder_level=Decimal("2.00"),
    quantity_required=Decimal("1.000"),
):
    """Create an inventory item and recipe link for one menu item."""
    inventory_item = InventoryItem.objects.create(
        name=f"{menu_item.name} Stock",
        unit="kg",
        quantity_in_stock=stock,
        reorder_level=reorder_level,
        cost_per_unit=Decimal("3.00"),
    )
    MenuItemIngredient.objects.create(
        menu_item=menu_item,
        ingredient=inventory_item,
        quantity_required=quantity_required,
    )

    return inventory_item


def create_table(table_number=1, capacity=4):
    """Create an active restaurant table."""
    return RestaurantTable.objects.create(
        table_number=table_number,
        capacity=capacity,
        location=RestaurantTable.Location.INDOOR,
        is_active=True,
    )


def create_order(customer, menu_item, quantity=1, status_value=None):
    """Create an order and one order item."""
    order = Order.objects.create(customer=customer)
    OrderItem.objects.create(
        order=order,
        menu_item=menu_item,
        quantity=quantity,
        unit_price=menu_item.price,
        subtotal=0,
    )

    if status_value is not None:
        order.status = status_value
        order.save(update_fields=("status", "updated_at"))

    order.refresh_from_db()
    return order


class InventoryDeductionTest(TestCase):
    """Test stock movement caused by order creation and cancellation."""

    def setUp(self):
        self.customer = create_user("customer@example.com")
        self.menu_item = create_menu_item(price=Decimal("12.00"))

    def test_placing_order_deducts_inventory_correctly(self):
        """Placing an order deducts recipe quantity times item quantity."""
        inventory_item = create_inventory_link(
            self.menu_item,
            stock=Decimal("10.00"),
            quantity_required=Decimal("2.500"),
        )

        create_order(self.customer, self.menu_item, quantity=3)

        inventory_item.refresh_from_db()
        self.assertEqual(inventory_item.quantity_in_stock, Decimal("2.50"))

    def test_cancelling_order_restores_inventory(self):
        """Cancelling an order restores the stock deducted by its items."""
        inventory_item = create_inventory_link(
            self.menu_item,
            stock=Decimal("10.00"),
            quantity_required=Decimal("2.000"),
        )
        order = create_order(self.customer, self.menu_item, quantity=4)

        order.status = Order.Status.CANCELLED
        order.save(update_fields=("status", "updated_at"))

        inventory_item.refresh_from_db()
        self.assertEqual(inventory_item.quantity_in_stock, Decimal("10.00"))

    def test_low_stock_condition_is_detectable_after_deduction(self):
        """A stock item is low when deduction leaves it at reorder level."""
        inventory_item = create_inventory_link(
            self.menu_item,
            stock=Decimal("5.00"),
            reorder_level=Decimal("2.00"),
            quantity_required=Decimal("1.500"),
        )

        create_order(self.customer, self.menu_item, quantity=2)

        inventory_item.refresh_from_db()
        self.assertTrue(inventory_item.is_low_stock)


class TableAvailabilityTest(TestCase):
    """Test reservation validation for table time windows and capacity."""

    def setUp(self):
        self.customer = create_user("booking@example.com")
        self.table = create_table(capacity=4)
        self.starts_at = timezone.now() + timedelta(days=1)

    def test_reservation_blocks_table_for_its_time_window(self):
        """An overlapping reservation for the same table is rejected."""
        Reservation.objects.create(
            table=self.table,
            customer=self.customer,
            reservation_datetime=self.starts_at,
            duration_minutes=90,
            party_size=2,
        )
        serializer = ReservationCreateSerializer(
            data={
                "table": self.table.pk,
                "reservation_datetime": (
                    self.starts_at + timedelta(minutes=30)
                ),
                "duration_minutes": 60,
                "party_size": 2,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("reservation_datetime", serializer.errors)

    def test_non_overlapping_reservation_on_same_table_is_allowed(self):
        """A later reservation is allowed after the first booking ends."""
        Reservation.objects.create(
            table=self.table,
            customer=self.customer,
            reservation_datetime=self.starts_at,
            duration_minutes=90,
            party_size=2,
        )
        serializer = ReservationCreateSerializer(
            data={
                "table": self.table.pk,
                "reservation_datetime": (
                    self.starts_at + timedelta(minutes=100)
                ),
                "duration_minutes": 60,
                "party_size": 2,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_party_size_exceeding_table_capacity_is_rejected(self):
        """A reservation is invalid when party size exceeds capacity."""
        serializer = ReservationCreateSerializer(
            data={
                "table": self.table.pk,
                "reservation_datetime": self.starts_at,
                "duration_minutes": 60,
                "party_size": 5,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("party_size", serializer.errors)


class OrderStatusTransitionTest(APITestCase):
    """Test staff-only order status workflow updates."""

    def setUp(self):
        self.staff = create_user("staff@example.com", role=User.Role.STAFF)
        self.customer = create_user("status-customer@example.com")
        self.menu_item = create_menu_item(
            name="Chicken",
            price=Decimal("8.00"),
        )
        self.order = create_order(self.customer, self.menu_item)
        self.url = reverse(
            "orders:order-status-update",
            kwargs={"pk": self.order.pk},
        )
        self.client.force_authenticate(user=self.staff)

    def test_status_follows_allowed_progression(self):
        """Order status can move from received to served step by step."""
        for next_status in (
            Order.Status.PREPARING,
            Order.Status.READY,
            Order.Status.SERVED,
        ):
            response = self.client.patch(
                self.url,
                {"status": next_status},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.SERVED)

    def test_invalid_transition_is_rejected_with_400(self):
        """Order status cannot skip directly from received to served."""
        response = self.client.patch(
            self.url,
            {"status": Order.Status.SERVED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.RECEIVED)


class DailySalesReportTest(TestCase):
    """Test daily sales report totals and top item ordering."""

    def setUp(self):
        self.customer = create_user("report@example.com")
        self.today = timezone.localdate()
        self.rice = create_menu_item(name="Rice", price=Decimal("10.00"))
        self.soup = create_menu_item(name="Soup", price=Decimal("5.00"))

    def test_report_returns_correct_total_revenue(self):
        """The report sums total_amount from served orders for the date."""
        create_order(
            self.customer,
            self.rice,
            quantity=2,
            status_value=Order.Status.SERVED,
        )
        create_order(
            self.customer,
            self.soup,
            quantity=3,
            status_value=Order.Status.SERVED,
        )

        report = get_daily_sales_report(self.today)

        self.assertEqual(report["total_orders"], 2)
        self.assertEqual(report["total_revenue"], Decimal("35.00"))

    def test_report_returns_correct_top_items(self):
        """The report returns top items ordered by quantity sold."""
        create_order(
            self.customer,
            self.rice,
            quantity=1,
            status_value=Order.Status.SERVED,
        )
        create_order(
            self.customer,
            self.soup,
            quantity=4,
            status_value=Order.Status.SERVED,
        )

        report = get_daily_sales_report(self.today)

        self.assertEqual(report["top_5_items"][0]["menu_item"], "Soup")
        self.assertEqual(
            report["top_5_items"][0]["total_quantity_sold"],
            4,
        )

    def test_report_with_no_orders_returns_zeros_not_an_error(self):
        """The report returns zero values when no served orders exist."""
        report = get_daily_sales_report(self.today)

        self.assertEqual(report["total_orders"], 0)
        self.assertEqual(report["total_revenue"], Decimal("0.00"))
        self.assertEqual(report["average_order_value"], Decimal("0.00"))
        self.assertEqual(report["top_5_items"], [])


class OrderCreateTest(APITestCase):
    """Test customer order creation through the API."""

    def setUp(self):
        self.customer = create_user("api-customer@example.com")
        self.client.force_authenticate(user=self.customer)
        self.url = reverse("orders:order-list-create")
        self.rice = create_menu_item(name="Fried Rice", price=Decimal("9.50"))
        self.juice = create_menu_item(name="Juice", price=Decimal("3.00"))

    def test_customer_can_place_order_with_multiple_items(self):
        """A customer can create one order containing multiple menu items."""
        response = self.client.post(
            self.url,
            {
                "order_type": Order.OrderType.TAKEAWAY,
                "items": [
                    {"menu_item": self.rice.pk, "quantity": 2},
                    {"menu_item": self.juice.pk, "quantity": 3},
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(customer=self.customer)
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.customer, self.customer)

    def test_unavailable_menu_item_is_rejected(self):
        """An order cannot include a menu item marked unavailable."""
        unavailable_item = create_menu_item(
            name="Sold Out Steak",
            price=Decimal("15.00"),
            is_available=False,
        )

        response = self.client.post(
            self.url,
            {
                "order_type": Order.OrderType.TAKEAWAY,
                "items": [
                    {"menu_item": unavailable_item.pk, "quantity": 1},
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_total_amount_is_calculated_correctly(self):
        """Order total equals each item price multiplied by its quantity."""
        response = self.client.post(
            self.url,
            {
                "order_type": Order.OrderType.TAKEAWAY,
                "items": [
                    {"menu_item": self.rice.pk, "quantity": 2},
                    {"menu_item": self.juice.pk, "quantity": 1},
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(customer=self.customer)
        self.assertEqual(order.total_amount, Decimal("22.00"))


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# create_user creates test users with the role each test needs.
#
# create_category creates a menu category because MenuItem requires one.
#
# create_menu_item creates menu items with prices and availability values used
# by order tests.
#
# create_inventory_link creates inventory stock plus the recipe link that
# tells the signal how much stock to deduct for one menu item.
#
# create_table creates an active table for reservation tests.
#
# create_order creates an order and one order item. It is used by model and
# report tests so each test can focus on the business rule being checked.
#
# InventoryDeductionTest checks the order signals. It verifies stock is
# deducted when an order item is created, restored when the order is cancelled,
# and marked low when the quantity reaches the reorder level.
#
# TableAvailabilityTest checks reservation validation. It verifies overlapping
# reservations are rejected, non-overlapping reservations are accepted, and a
# party that is too large for the table is rejected.
#
# OrderStatusTransitionTest checks the staff status API. It verifies the normal
# received, preparing, ready, served flow works and invalid jumps return 400.
#
# DailySalesReportTest checks get_daily_sales_report. It verifies revenue,
# top item ordering, and the empty-report case.
#
# OrderCreateTest checks the order creation API. It verifies customers can
# create multi-item orders, unavailable items are rejected, and totals are
# calculated from item prices and quantities.
#
# Important decisions that were made and why
#
# Model-level tests are used for signals and reports because those rules live
# below the API layer.
#
# APITestCase is used for status updates and order creation because those
# rules are exposed through real API endpoints.
#
# Decimal values are used for prices and stock quantities because the models
# store money and inventory amounts as DecimalField values.
#
# force_authenticate is used so tests can focus on authorization roles and
# business logic without needing to request JWT tokens first.
#
# What you should read and understand before you review the code
#
# Read Django TestCase and DRF APITestCase.
#
# Read Django signals for OrderItem and Order status changes.
#
# Read ReservationCreateSerializer validation for table conflicts.
#
# Read OrderStatusUpdateSerializer validation for allowed status transitions.
#
# Read get_daily_sales_report to understand the report fields.
#
# ============================================================
# END OF REVIEW
# ============================================================
