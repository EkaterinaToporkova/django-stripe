import stripe
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, DeleteView
from main import settings
from main.forms import AddQuantityForm
from shop.models import Item, Order, OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessView(TemplateView):
    template_name = "payment_success.html"


class CancelView(TemplateView):
    template_name = "payment_failed.html"


class ProductView(ListView):
    model = Item
    template_name = 'shop.html'

    def get_context_data(self, **kwargs):
        products = Item.objects.all()
        context = super(ProductView, self).get_context_data(**kwargs, )
        context.update({
            "items": products,
        })
        return context


class ProductDetailView(TemplateView):
    template_name = 'product-details.html'

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get("pk")
        product = Item.objects.get(pk=pk)
        context = super(ProductDetailView, self).get_context_data(**kwargs, )
        context.update({
            "product": product,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
        })
        return context


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs["pk"]
        product = Item.objects.get(id=product_id)
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'rub',
                        'unit_amount_decimal': product.price_unit,
                        'product_data': {
                            'name': product.name,
                            "description": product.note,
                            # "images": [product.image_url],
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "product_id": product.id
            },
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
        return redirect(checkout_session.url, code=303)


# @login_required(login_url=reverse_lazy(
#     'register'))  # работу функции add_item_to_cart() может вызвать только залогиненный пользователь
def add_item_to_cart(request, pk):
    if request.method == 'POST':
        quantity_form = AddQuantityForm(request.POST)
        if quantity_form.is_valid():  # если форма прошла валидацию, то создаётся объект quantity
            quantity = quantity_form.cleaned_data['quantity']
            if quantity:
                cart = Order.get_cart(
                    request.user)  # метод get_cart способен обеспечить нужной корзиной - объектом cart
                product = get_object_or_404(Item, pk=pk)
                if OrderItem.objects.filter(product=product).exists():
                    order_items = cart.orderitem_set.filter(product=product)
                    for it in order_items:
                        it.quantity += quantity
                        it.save()
                        cart.save()
                else:
                    # с помощью cart.orderitem_set.create() создаём
                    # новый объект модели OrderItem
                    cart.orderitem_set.create(product=product,
                                              quantity=quantity,
                                              price=product.price)

                cart.save()  # фиксируем связь этого объекта с корзиной заказа
                return redirect('cart_view')
        else:
            pass
    return redirect(request.META['HTTP_REFERER'])


def cart_view(request):
    cart = Order.get_cart(request.user)
    items = cart.orderitem_set.all()
    context = {
        'cart': cart,
        'items': items
    }
    return render(request, 'cart.html', context)


@method_decorator(login_required,
                  name='dispatch')  # работу класса CartDeleteIem может вызвать только залогиненный пользователь
class CartDeleteItem(DeleteView):
    model = OrderItem
    template_name = 'cart.html'
    success_url = reverse_lazy('cart_view')

    def get_queryset(self):
        qs = super().get_queryset()
        qs.filter(order__user=self.request.user)
        return qs
