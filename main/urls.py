from django.contrib import admin
from django.urls import path

from main import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [path("", views.ProductView.as_view(), name="shop"),
               path("item/<int:pk>/", views.ProductDetailView.as_view(), name="item"),
               path("cancel/", views.CancelView.as_view(), name="cancel"),
               path("success/", views.SuccessView.as_view(), name="success"),
               path("admin/", admin.site.urls),
               path("buy/<int:pk>/", views.CreateCheckoutSessionView.as_view(), name="create-checkout-session"),
               path('cart_view/', views.cart_view, name='cart_view'),
               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
