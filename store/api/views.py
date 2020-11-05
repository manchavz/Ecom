from store.models import Product, OrderItem, FullOrder, Purchased_item
from store.models import ProductCategories
from .serializers import (
    ProductCategorySerializer,
    OrderItemSerializer,
    ProductSerializer,
    OrderDetailsSerializer,
)
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers


class Store(APIView):
    def get(self, request):
        total_item_cart = 0

        if request.user.is_authenticated:
            items = OrderItem.objects.filter(user=request.user)
            for item in items:
                total_item_cart += item.quantity

        product_categories = ProductCategories.objects.all()
        serializer_pct = ProductCategorySerializer(product_categories,many=True)
        context = {
            'product_categories' : serializer_pct.data,
            'total_item_cart' : total_item_cart,
        }

        return Response(context)


class Cart(APIView):
    def get(self, request):

        items = []
        total_cost_cart = 0
        total_item_cart = 0

        if request.user.is_authenticated:
            items = OrderItem.objects.filter(user=request.user)
            for item in items:
                total_item_cart += item.quantity

            for item in items:
                total_cost_cart += item.get_total

        product_categories = ProductCategories.objects.all()
        serializer_pct = ProductCategorySerializer(product_categories, many=True)
        serializer_oi = OrderItemSerializer(items, many=True)
        context = {
            'items': serializer_oi.data,
            'total_item_cart': total_item_cart,
            'total_cost_cart': total_cost_cart,
            'product_categories': serializer_pct.data,
        }
        return Response(context)


class Checkout(APIView):
    def get(self, request):

        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        items = []
        total_cost_cart = 0
        total_item_cart = 0

        if request.user.is_authenticated:
            items = OrderItem.objects.filter(user=request.user)
            for item in items:
                total_item_cart += item.quantity

            for item in items:
                total_cost_cart += item.get_total

        if total_item_cart == 0:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer_oi = OrderItemSerializer(items, many=True)

        product_categories = ProductCategories.objects.all()
        serializer_pct = ProductCategorySerializer(product_categories, many=True)

        context = {
            'product_categories': serializer_pct.data,
            'items': serializer_oi.data,
            'total_item_cart': total_item_cart,
            'total_cost_cart': total_cost_cart,
        }
        return Response(context)


class ShowItems(APIView):

    def get(self, request, id):

        total_item_cart = 0

        if request.user.is_authenticated:
            items = OrderItem.objects.filter(user=request.user)
            for item in items:
                total_item_cart += item.quantity
        try:
            product_category = ProductCategories.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer_pct_1 = ProductCategorySerializer(product_category)

        products = Product.objects.filter(category=product_category)
        serializer_p = ProductSerializer(products, many=True)

        product_categories = ProductCategories.objects.all()
        serializer_pct = ProductCategorySerializer(product_categories,many=True)

        context = {
            'product_categories': serializer_pct.data,
            'product_category': serializer_pct_1.data,
            'products': serializer_p.data,
            'total_item_cart': total_item_cart,
        }
        return Response(context)


class ItemDetail(APIView):
    def get(self, request, id):

        total_item_cart = 0

        if request.user.is_authenticated:
            items = OrderItem.objects.filter(user=request.user)
            for item in items:
                total_item_cart += item.quantity
        try:
            product = Product.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer_p = ProductSerializer(product)

        product_categories = ProductCategories.objects.all()
        serializer_pct = ProductCategorySerializer(product_categories, many=True)

        context = {
            'product_categories': serializer_pct.data,
            'product': serializer_p.data,
            'total_item_cart': total_item_cart,
        }

        return Response(context)


class OrderDetails(APIView):
    def get(self, request):

        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        total_item_cart = 0
        if request.user.is_authenticated:
            items = OrderItem.objects.filter(user=request.user)
            for item in items:
                total_item_cart += item.quantity

        orders = FullOrder.objects.filter(user=request.user).order_by('-date_ordered')

        ordered = []
        for order in orders:
            items = Purchased_item.objects.filter(order=order)
            tt = serializers.serialize('json', items)
            serializer_order = OrderDetailsSerializer(order)
            ordered.append({'order': serializer_order.data, 'items': tt})

        product_categories = ProductCategories.objects.all()
        serializer_pct = ProductCategorySerializer(product_categories, many=True)

        context = {
            'product_categories': serializer_pct.data,
            'ordered': ordered,
            'total_item_cart': total_item_cart,
        }
        return Response(context)


@method_decorator(csrf_exempt, name='dispatch')
class InsertIntoCart(APIView):

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        total_item_cart = 0

        product_id = request.data['product_id']
        action = request.data['action']
        product = Product.objects.get(id=product_id)

        item , created = OrderItem.objects.get_or_create(product=product, user=request.user)
        item.save()
        if action == 'add':
            item.quantity += 1
            item.save()
        else:
            item.quantity -= 1
            item.save()
            if item.quantity <= 0:
                item.delete()

        items = OrderItem.objects.filter(user=request.user)
        for item in items:
            total_item_cart += item.quantity

        dic = {
            'total_item_cart': total_item_cart,
        }

        return Response(dic)


class MakePayment(APIView):
    def get(self, request):

        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        dt = datetime.datetime.now()
        seq = int(dt.strftime("%Y%m%d%H%M%S"))

        obj = FullOrder.objects.create(user=request.user)

        obj.transaction_id = seq
        obj.save()

        total_amount = 0

        items = OrderItem.objects.all()
        for item in items:
            item_purchased = Purchased_item.objects.create(order=obj)
            item_purchased.user = request.user
            item_purchased.quantity = item.quantity
            item_purchased.name = item.product.name
            item_purchased.price = item.product.price
            item_purchased.image = item.product.image
            item_purchased.description = item.product.description
            item_purchased.save()
            total_amount += item.product.price * item.quantity

            item.delete()

        obj.amount = total_amount
        obj.save()

        return Response(status=status.HTTP_200_OK)
