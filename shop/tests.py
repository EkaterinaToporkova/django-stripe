import zoneinfo
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from shop.models import Item, Payment, OrderItem, Order


class TestDataBase(TestCase):
    fixtures = [
        'shop/fixtures/data.json'
    ]

    # извлекаем супер пользователя
    def setUp(self):
        self.user = User.objects.get(username='root')
        self.p = Item.objects.all().first()

    # проверяем, существует ли пользователь
    def test_user_exists(self):
        users = User.objects.all()
        user = users.first()
        self.assertEqual(user.username, 'root')
        self.assertTrue(user.is_superuser)

    # проверяем пароль суперпользователя
    def test_user_password(self):
        self.assertTrue(self.user.check_password('root'))

    # проверяем, что во всех таблицах находится больше 1 значения
    def test_all_date(self):
        self.assertGreater(Item.objects.all().count(), 0)
        self.assertGreater(Order.objects.all().count(), 0)
        self.assertGreater(OrderItem.objects.all().count(), 0)
        self.assertGreater(Payment.objects.all().count(), 0)

    # подчитываем корзины конкретного пользователя (больше 1 корзины у 1 пользователя быть не может)
    def find_cart_number(self):
        cart_number = Order.objects.filter(user=self.user,
                                           status=Order.STATUS_CART
                                           ).count()
        return cart_number
