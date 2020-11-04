from django.urls import path
from . import views


urlpatterns = [
    path('api/', views.Store.as_view(), name='api_store'),
    path('api/cart', views.Cart.as_view(), name='api_cart'),
    path('api/checkout/', views.Checkout.as_view(), name='api_checkout'),
    path('api/show_items/<int:id>/', views.ShowItems.as_view(), name='api_show_items'),
    path('api/item_detail/<int:id>', views.ItemDetail.as_view(), name='api_item_detail'),
    path('api/insert_cart/', views.InsertIntoCart.as_view(), name='api_insert_cart'),
    path('api/make_payment/<int:id>', views.MakePayment.as_view(), name='api_make_payment'),
    path('api/order_details/', views.OrderDetails.as_view(), name='api_order_details'),
]
