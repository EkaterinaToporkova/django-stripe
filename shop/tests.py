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
        users_number = users.count()
        user = users.first()
        self.assertEqual(users_number, 1)
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


    def test_functional_get_cart(self):
        """ Проверяем количество корзин пользователя:
        1. Нет корзины
        2. Корзина только что создана
        3. Проверить, что получена та корзина, которая создана, а не создалась новая
        =============================================================================
        Добавим @staticmethod Order.get_cart(user)
        """

        # Нет корзины
        self.assertEqual(self.find_cart_number(), 0)
        # 2. Корзина только что создана
        Order.get_cart(self.user)
        self.assertEqual(self.find_cart_number(), 1)
        # 3. Проверить, что получена та корзина, которая создана, а не создалась новая
        Order.get_cart(self.user)
        self.assertEqual(self.find_cart_number(), 1)

    def test_cart_older_7_day(self):
        """Если корзина старше 7 дней, она должна быть удалена
        1. Получаем корзину и искусственно состариваем ее
        """
        cart = Order.get_cart(self.user)
        cart.creation_time = timezone.datetime(2000, 1, 1, tzinfo=zoneinfo.ZoneInfo(
            'UTC'))  # корзина удаляется, т.к. она старше 7 лет
        cart.save()
        cart = Order.get_cart(self.user)  # получаем новую корзину(пустую)
        self.assertEqual((timezone.now() - cart.creation_time).days, 0)

    def test_recalculate_order_amount_after_changing_ordertime(self):
        """Перерасчет суммы заказа после каждого изменения
        1. Получаем сумму до какого-либо изменения
        2. -------''-------- после добавления элемента
        3. -------''-------- после удаления элемента
        """

        # 1. Получаем сумму до всех изменения
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(0))

        # 2. -------''-------- после добавления элемента
        i = OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=2)
        i = OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=3)
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(10))

        # 3. -------''-------- после удаления элемента
        i.delete()
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(4))

    def test_cart_status_changing_after_applying_make_order(self):
        """Изменение статуса корзины, после применения метода Order.make_order()
        После завершения набора/изменения Корзины и перехода к оплате, Корзина должна менять статус(если
        она не пустая) и становится Заказом, ожидающим оплаты(waiting_for_payment)
        """

        # 1. Изменение статуса для пустой корзины - статус не должен поменяться
        cart = Order.get_cart(self.user)
        cart.make_order()
        self.assertEqual(cart.status, Order.STATUS_CART)

        # 2. Изменения статуса для непустой корзины
        OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=2)
        cart.make_order()
        self.assertEqual(cart.status, Order.STATUS_WAITING_FOR_PAYMENT)

    def test_method_get_amount_of_unpaid_orders(self):
        """Получаем сумму неоплаченных заказов
        Необходим метод get_unpaid_orders(user), который позволит получить общую сумму
        неоплаченных заказов(status = waiting_for_payment) по указанному пользователю.
        1. Перед созданием корзины
        2. После создания корзины
        3. После того, как к корзине применили cart.make_order()
        4. После оплаты заказа
        5. После удаления всех заказов
        ==============================
        Метод Order.get_amount_of_unpaid_orders()
        """

        # 1. Перед созданием корзины
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(100))

        # 2. После создания корзины
        cart = Order.get_cart(self.user)
        OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=2)
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(100))

        # 3. После того, как к корзине применили cart.make_order()
        cart.make_order()
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(104))

        # 4. После оплаты заказа
        cart.status = Order.STATUS_PAID
        cart.save()
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(100))

        # 5. После удаления всех заказов
        Order.objects.all().delete()
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(0))

    # def test_method_get_balance(self):
    #     """Метод получения баланса
    #     1. До оплаты
    #     2. После оплаты
    #     3. После добавления какого-либо платежа
    #     4. Нет платежей
    #     ========================================
    #     Метод Payment.get_balance()
    #     """
    #
    #     # 1. До оплаты
    #     amount = Payment.get_balance(self.user)
    #     self.assertEqual(amount, Decimal(100))
    #
    #     # 2. После оплаты
    #     Payment.objects.create(user=self.user, amount=100)
    #     amount = Payment.get_balance(self.user)
    #     self.assertEqual(amount, Decimal(200))
    #
    #     # 3. После добавления нескольких платежей
    #     Payment.objects.create(user=self.user, amount=-4)
    #     amount = Payment.get_balance(self.user)
    #     self.assertEqual(amount, Decimal(196))
    #
    #     # 4. Нет платежей
    #     Payment.objects.all().delete()
    #     amount = Payment.get_balance(self.user)
    #     self.assertEqual(amount, Decimal(0))
    #
    # def test_auto_payment_after_add_required_payment(self):
    #     """Изменение при добавлении платежей
    #     После применения оплаты:
    #     1. заказа должен поменять статус
    #     2. И баланс должен быть равен нулю
    #     """
    #     Payment.objects.create(user=self.user, amount=0)
    #     self.assertEqual(Payment.get_balance(self.user), Decimal(100))
    #     amount = Order.get_amount_of_unpaid_orders(self.user)
    #     self.assertEqual(amount, Decimal(100))
    #
    # def test_auto_payment_after_add_earlier_payment(self):
    #     """Баланс и заказ уже существуют, но создается новый заказ.
    #     1. Более ранний заказ должен изменить статус
    #     2. Баланс должен уменьшится
    #     """
    #     cart = Order.get_cart(self.user)
    #     OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=100)
    #     Payment.objects.create(user=self.user, amount=200)
    #     self.assertEqual(Payment.get_balance(self.user), Decimal(300))
    #     amount = Order.get_amount_of_unpaid_orders(self.user)
    #     self.assertEqual(amount, Decimal(100))
    #
    #
    # def test__auto_payment_for_all_orders(self):
    #     """Есть неоплаченные заказы
    #     """
    #     cart = Order.get_cart(self.user)
    #     OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=100)
    #     Payment.objects.create(user=self.user, amount=300)
    #     self.assertEqual(Payment.get_balance(self.user), Decimal(400))
    #     amount = Order.get_amount_of_unpaid_orders(self.user)
    #     self.assertEqual(amount, Decimal(100))
