import stripe
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView, ListView
from main import settings
from shop.models import Item

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
        context = super(ProductView, self).get_context_data(**kwargs,)
        context.update({
            "items": products,
        })
        return context


class ProductDetailView(TemplateView):
    template_name = 'product-details.html'

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get("pk")
        product = Item.objects.get(pk=pk)
        context = super(ProductDetailView, self).get_context_data(**kwargs,)
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
                            #"images": [product.image_url],
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


def cart_view(request):
    pass
    # cart = Order.get_cart(request.user)
    # items = cart.orderitem_set.all()
    # context = {
    #     'cart': cart,
    #     'items': items
    # }
    # return render(request, 'shop/cart.html', context)