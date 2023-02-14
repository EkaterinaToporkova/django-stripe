import stripe
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.conf import settings
from shop.models import Item, Order
from django.http import JsonResponse

stripe.api_key = settings.STRIPE_SECRET_KEY


class ProductsListView(ListView):
    model = Item
    template_name = 'shop.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductsListView, self).get_context_data(**kwargs)
        context.update({
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
        })
        return context


class ProductsDetailView(DetailView):
    model = Item
    template_name = 'shop-details.html'

class SuccessView(TemplateView):
    template_name = 'success.html'


class CancelView(TemplateView):
    template_name = 'cancel.html'


class CreateCheckoutSession(View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs['pk']
        product = Item.objects.get(id=product_id)
        print(product)
        YOUR_DOMAIN = 'http://127.0.0.1:8000'
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'unit_amount': product.price,
                        'product_data': {
                            'images': [product.image_url],
                            'name': product.name,
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

        return JsonResponse({
            'id': checkout_session.id
        })
