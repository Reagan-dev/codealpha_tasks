from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from inventory.models import InventoryItem, MenuItemIngredient
from menu.models import Category, MenuItem
from orders.models import Order, OrderItem
from reservations.models import Reservation, RestaurantTable


class Command(BaseCommand):
    """Seed optional demo data for the restaurant API."""

    help = (
        "Seed demo users, menu, inventory, tables, reservations, and orders."
    )

    demo_emails = (
        "manager@restaurant.com",
        "staff1@restaurant.com",
        "staff2@restaurant.com",
        "customer1@email.com",
        "customer2@email.com",
        "customer3@email.com",
    )
    category_names = ("Starters", "Main Course", "Desserts", "Drinks")
    menu_item_names = (
        "Chicken Wings",
        "Garlic Bread",
        "Grilled Chicken",
        "Beef Burger",
        "Chocolate Cake",
        "Fruit Sundae",
        "Fresh Lemonade",
        "Iced Tea",
    )
    inventory_names = (
        "Chicken",
        "Beef",
        "Bread",
        "Potatoes",
        "Lettuce",
        "Lemonade Syrup",
        "Chocolate",
        "Tea Bags",
    )
    table_numbers = tuple(range(1, 9))

    def handle(self, *args, **options):
        """Run the demo seed process."""
        self.created_counts = {
            "Users": 0,
            "Categories": 0,
            "Menu Items": 0,
            "Inventory Items": 0,
            "Menu Item Ingredients": 0,
            "Restaurant Tables": 0,
            "Reservations": 0,
            "Orders": 0,
            "Order Items": 0,
        }

        self.stdout.write("Clearing existing demo data...")
        self.clear_demo_data()

        self.stdout.write("Seeding users...")
        users = self.seed_users()

        self.stdout.write("Seeding categories...")
        categories = self.seed_categories()

        self.stdout.write("Seeding menu items...")
        menu_items = self.seed_menu_items(categories)

        self.stdout.write("Seeding inventory items...")
        inventory_items = self.seed_inventory_items()

        self.stdout.write("Seeding menu item ingredients...")
        self.seed_menu_item_ingredients(menu_items, inventory_items)

        self.stdout.write("Seeding restaurant tables...")
        tables = self.seed_tables()

        self.stdout.write("Seeding reservations...")
        self.seed_reservations(users, tables)

        self.stdout.write("Seeding orders...")
        self.seed_orders(users, menu_items, tables)

        self.print_summary()
        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))

    def clear_demo_data(self):
        """Delete only known demo data and keep any superusers."""
        OrderItem.objects.filter(
            order__customer__email__in=self.demo_emails
        ).delete()
        Order.objects.filter(customer__email__in=self.demo_emails).delete()
        Reservation.objects.filter(
            customer__email__in=self.demo_emails
        ).delete()
        Reservation.objects.filter(
            table__table_number__in=self.table_numbers
        ).delete()
        MenuItemIngredient.objects.filter(
            menu_item__name__in=self.menu_item_names
        ).delete()
        MenuItemIngredient.objects.filter(
            ingredient__name__in=self.inventory_names
        ).delete()
        MenuItem.objects.filter(name__in=self.menu_item_names).delete()
        Category.objects.filter(name__in=self.category_names).delete()
        InventoryItem.objects.filter(name__in=self.inventory_names).delete()
        RestaurantTable.objects.filter(
            table_number__in=self.table_numbers
        ).delete()

        User = get_user_model()
        User.objects.filter(
            email__in=self.demo_emails,
            is_superuser=False,
        ).delete()

    def seed_users(self):
        """Create demo manager, staff, and customer accounts."""
        User = get_user_model()
        user_data = (
            (
                "manager@restaurant.com",
                "manager",
                "Manager@1234",
                User.Role.MANAGER,
            ),
            (
                "staff1@restaurant.com",
                "staff1",
                "Staff@1234",
                User.Role.STAFF,
            ),
            (
                "staff2@restaurant.com",
                "staff2",
                "Staff@1234",
                User.Role.STAFF,
            ),
            (
                "customer1@email.com",
                "customer1",
                "Customer@1234",
                User.Role.CUSTOMER,
            ),
            (
                "customer2@email.com",
                "customer2",
                "Customer@1234",
                User.Role.CUSTOMER,
            ),
            (
                "customer3@email.com",
                "customer3",
                "Customer@1234",
                User.Role.CUSTOMER,
            ),
        )
        users = {}

        for email, username, password, role in user_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": username,
                    "role": role,
                },
            )
            user.username = username
            user.role = role
            user.set_password(password)
            user.save()
            users[email] = user
            self.created_counts["Users"] += int(created)

        return users

    def seed_categories(self):
        """Create menu categories in display order."""
        category_data = (
            ("Starters", "Small plates and appetizers.", 1),
            ("Main Course", "Filling main dishes for lunch and dinner.", 2),
            ("Desserts", "Sweet dishes served after meals.", 3),
            ("Drinks", "Cold and refreshing beverages.", 4),
        )
        categories = {}

        for name, description, display_order in category_data:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "display_order": display_order,
                    "is_active": True,
                },
            )
            category.description = description
            category.display_order = display_order
            category.is_active = True
            category.save()
            categories[name] = category
            self.created_counts["Categories"] += int(created)

        return categories

    def seed_menu_items(self, categories):
        """Create available menu items for each category."""
        item_data = (
            (
                "Chicken Wings",
                "Crispy wings tossed in a mild house sauce.",
                "Starters",
                Decimal("8.50"),
                18,
            ),
            (
                "Garlic Bread",
                "Toasted bread with garlic butter and herbs.",
                "Starters",
                Decimal("4.00"),
                10,
            ),
            (
                "Grilled Chicken",
                "Char-grilled chicken served with seasoned potatoes.",
                "Main Course",
                Decimal("15.00"),
                30,
            ),
            (
                "Beef Burger",
                "Beef patty with lettuce, sauce, and a toasted bun.",
                "Main Course",
                Decimal("13.50"),
                25,
            ),
            (
                "Chocolate Cake",
                "Rich chocolate cake served with cream.",
                "Desserts",
                Decimal("6.50"),
                12,
            ),
            (
                "Fruit Sundae",
                "Mixed fruit, ice cream, and chocolate drizzle.",
                "Desserts",
                Decimal("5.75"),
                8,
            ),
            (
                "Fresh Lemonade",
                "Chilled lemonade made with fresh citrus.",
                "Drinks",
                Decimal("3.50"),
                5,
            ),
            (
                "Iced Tea",
                "Cold brewed tea served over ice.",
                "Drinks",
                Decimal("3.00"),
                5,
            ),
        )
        menu_items = {}

        for name, description, category_name, price, preparation_time in (
            item_data
        ):
            menu_item, created = MenuItem.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "category": categories[category_name],
                    "price": price,
                    "is_available": True,
                    "preparation_time": preparation_time,
                },
            )
            menu_item.description = description
            menu_item.category = categories[category_name]
            menu_item.price = price
            menu_item.is_available = True
            menu_item.preparation_time = preparation_time
            menu_item.save()
            menu_items[name] = menu_item
            self.created_counts["Menu Items"] += int(created)

        return menu_items

    def seed_inventory_items(self):
        """Create stock items, including one low-stock demo item."""
        inventory_data = (
            ("Chicken", "kg", Decimal("18.00"), Decimal("5.00")),
            ("Beef", "kg", Decimal("12.00"), Decimal("4.00")),
            ("Bread", "pieces", Decimal("40.00"), Decimal("10.00")),
            ("Potatoes", "kg", Decimal("3.00"), Decimal("5.00")),
            ("Lettuce", "pieces", Decimal("15.00"), Decimal("5.00")),
            ("Lemonade Syrup", "litres", Decimal("8.00"), Decimal("2.00")),
            ("Chocolate", "kg", Decimal("6.00"), Decimal("2.00")),
            ("Tea Bags", "pieces", Decimal("100.00"), Decimal("20.00")),
        )
        inventory_items = {}

        for name, unit, stock, reorder_level in inventory_data:
            item, created = InventoryItem.objects.get_or_create(
                name=name,
                defaults={
                    "unit": unit,
                    "quantity_in_stock": stock,
                    "reorder_level": reorder_level,
                    "cost_per_unit": Decimal("2.50"),
                },
            )
            item.unit = unit
            item.quantity_in_stock = stock
            item.reorder_level = reorder_level
            item.cost_per_unit = Decimal("2.50")
            item.save()
            inventory_items[name] = item
            self.created_counts["Inventory Items"] += int(created)

        return inventory_items

    def seed_menu_item_ingredients(self, menu_items, inventory_items):
        """Link menu items to the inventory they consume."""
        link_data = (
            ("Chicken Wings", "Chicken", Decimal("0.300")),
            ("Garlic Bread", "Bread", Decimal("2.000")),
            ("Grilled Chicken", "Chicken", Decimal("0.500")),
            ("Grilled Chicken", "Potatoes", Decimal("0.300")),
            ("Beef Burger", "Beef", Decimal("0.250")),
            ("Beef Burger", "Bread", Decimal("1.000")),
            ("Beef Burger", "Lettuce", Decimal("1.000")),
            ("Chocolate Cake", "Chocolate", Decimal("0.120")),
            ("Fresh Lemonade", "Lemonade Syrup", Decimal("0.200")),
            ("Iced Tea", "Tea Bags", Decimal("1.000")),
        )

        for menu_item_name, inventory_name, quantity_required in link_data:
            _, created = MenuItemIngredient.objects.get_or_create(
                menu_item=menu_items[menu_item_name],
                ingredient=inventory_items[inventory_name],
                defaults={"quantity_required": quantity_required},
            )
            MenuItemIngredient.objects.filter(
                menu_item=menu_items[menu_item_name],
                ingredient=inventory_items[inventory_name],
            ).update(quantity_required=quantity_required)
            self.created_counts["Menu Item Ingredients"] += int(created)

    def seed_tables(self):
        """Create active restaurant tables across all locations."""
        table_data = (
            (1, 2, RestaurantTable.Location.INDOOR),
            (2, 4, RestaurantTable.Location.INDOOR),
            (3, 4, RestaurantTable.Location.INDOOR),
            (4, 6, RestaurantTable.Location.INDOOR),
            (5, 4, RestaurantTable.Location.OUTDOOR),
            (6, 6, RestaurantTable.Location.OUTDOOR),
            (7, 8, RestaurantTable.Location.PRIVATE),
            (8, 10, RestaurantTable.Location.PRIVATE),
        )
        tables = {}

        for table_number, capacity, location in table_data:
            table, created = RestaurantTable.objects.get_or_create(
                table_number=table_number,
                defaults={
                    "capacity": capacity,
                    "location": location,
                    "is_active": True,
                },
            )
            table.capacity = capacity
            table.location = location
            table.is_active = True
            table.save()
            tables[table_number] = table
            self.created_counts["Restaurant Tables"] += int(created)

        return tables

    def seed_reservations(self, users, tables):
        """Create demo reservations for today and tomorrow."""
        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)
        reservation_data = (
            (
                users["customer1@email.com"],
                tables[2],
                self.make_datetime(today, time(18, 0)),
                90,
                2,
                Reservation.Status.CONFIRMED,
                "Window seat if available.",
            ),
            (
                users["customer2@email.com"],
                tables[5],
                self.make_datetime(today, time(20, 0)),
                90,
                4,
                Reservation.Status.PENDING,
                "Birthday dinner.",
            ),
            (
                users["customer3@email.com"],
                tables[7],
                self.make_datetime(tomorrow, time(19, 30)),
                120,
                6,
                Reservation.Status.CONFIRMED,
                "Private table requested.",
            ),
        )

        for reservation in reservation_data:
            customer, table, starts_at, duration, party_size, status, notes = (
                reservation
            )
            _, created = Reservation.objects.get_or_create(
                customer=customer,
                table=table,
                reservation_datetime=starts_at,
                defaults={
                    "duration_minutes": duration,
                    "party_size": party_size,
                    "status": status,
                    "notes": notes,
                },
            )
            Reservation.objects.filter(
                customer=customer,
                table=table,
                reservation_datetime=starts_at,
            ).update(
                duration_minutes=duration,
                party_size=party_size,
                status=status,
                notes=notes,
            )
            self.created_counts["Reservations"] += int(created)

    def seed_orders(self, users, menu_items, tables):
        """Create served and active orders after all dependencies exist."""
        order_data = (
            (
                users["customer1@email.com"],
                tables[2],
                Order.Status.SERVED,
                Order.OrderType.DINE_IN,
                (("Grilled Chicken", 2), ("Fresh Lemonade", 2)),
            ),
            (
                users["customer2@email.com"],
                tables[5],
                Order.Status.SERVED,
                Order.OrderType.DINE_IN,
                (("Beef Burger", 1), ("Iced Tea", 1), ("Fruit Sundae", 1)),
            ),
            (
                users["customer3@email.com"],
                None,
                Order.Status.SERVED,
                Order.OrderType.TAKEAWAY,
                (("Chicken Wings", 2), ("Chocolate Cake", 1)),
            ),
            (
                users["customer1@email.com"],
                tables[3],
                Order.Status.PREPARING,
                Order.OrderType.DINE_IN,
                (("Beef Burger", 2), ("Fresh Lemonade", 2)),
            ),
            (
                users["customer2@email.com"],
                None,
                Order.Status.RECEIVED,
                Order.OrderType.TAKEAWAY,
                (("Garlic Bread", 1), ("Iced Tea", 2)),
            ),
        )

        for customer, table, status, order_type, items in order_data:
            order = Order.objects.create(
                customer=customer,
                table=table,
                status=status,
                order_type=order_type,
            )
            self.created_counts["Orders"] += 1

            for item_name, quantity in items:
                menu_item = menu_items[item_name]
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=quantity,
                    unit_price=menu_item.price,
                    subtotal=0,
                )
                self.created_counts["Order Items"] += 1

            order.save()

    def make_datetime(self, date_value, time_value):
        """Return a timezone-aware datetime for the configured timezone."""
        naive_datetime = datetime.combine(date_value, time_value)

        return timezone.make_aware(
            naive_datetime,
            timezone.get_current_timezone(),
        )

    def print_summary(self):
        """Print created record counts in a simple summary table."""
        self.stdout.write("")
        self.stdout.write("Seed summary:")
        self.stdout.write("-" * 40)
        self.stdout.write(f"{'Model':<26}Created")
        self.stdout.write("-" * 40)

        for model_name, count in self.created_counts.items():
            self.stdout.write(f"{model_name:<26}{count}")

        self.stdout.write("-" * 40)


