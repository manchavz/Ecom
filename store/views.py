from django.shortcuts import render
from .models import Product, OrderItem, FullOrder, Purchased_item
from .models import ProductCategories
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from dotenv import load_dotenv
import datetime
import requests
import pprint
import os
from . import services


def store(request):
    total_item_cart = 0

    if request.user.is_authenticated:
        items = OrderItem.objects.filter(user=request.user)
        for item in items:
            total_item_cart += item.quantity

    product_categories = ProductCategories.objects.all()

    context = {
        'product_categories': product_categories,
        'total_item_cart': total_item_cart,
    }
    return render(request, 'store/store.html', context)


def checkout(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_login'))

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
        return Http404

    product_categories = ProductCategories.objects.all()

    context = {
        'product_categories': product_categories,
        'items': items,
        'total_item_cart': total_item_cart,
        'total_cost_cart': total_cost_cart,
    }
    return render(request, 'store/checkout.html', context)


@csrf_exempt
def insert_into_cart(request):
    total_item_cart = 0
    about = 'item_not_added'
    if request.user.is_authenticated:
        about = 'Item Added'
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)
        if OrderItem.objects.filter(product=product, user=request.user).exists():
            item = OrderItem.objects.get(product=product, user=request.user)
            item.quantity += 1
            item.save()
        else:
            item = OrderItem.objects.create(product=product, user=request.user, quantity=1)
            item.save()

        items = OrderItem.objects.filter(user=request.user)
        for item in items:
            total_item_cart += item.quantity

    dic = {
        'data': about,
        'total_item_cart': total_item_cart,
    }
    return JsonResponse(dic, safe=False)


@csrf_exempt
def update_item_quantity(request):
    about = 'Some Error Occurred'
    if request.user.is_authenticated:
        about = 'Item Updated'
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        product = Product.objects.get(id=product_id)
        item = OrderItem.objects.get(product=product, user=request.user)

        if action == 'add':
            item.quantity += 1
        else:
            item.quantity -= 1
        item.save()
        if item.quantity <= 0:
            item.delete()

    dic = {
        'data': about,
    }
    return JsonResponse(dic, safe=False)


def cart(request):
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
        check = False
    else:
        check = True

    product_categories = ProductCategories.objects.all()

    context = {
        'items': items,
        'total_item_cart': total_item_cart,
        'total_cost_cart': total_cost_cart,
        'check': check,
        'product_categories': product_categories,
    }
    return render(request, 'store/cart.html', context)


def item_detail(request, id):

    total_item_cart = 0

    if request.user.is_authenticated:
        items = OrderItem.objects.filter(user=request.user)
        for item in items:
            total_item_cart += item.quantity

    product = Product.objects.get(id=id)

    product_categories = ProductCategories.objects.all()

    context = {
        'product_categories': product_categories,
        'product': product,
        'total_item_cart': total_item_cart,
    }

    return render(request, 'store/item_detail.html', context)


def order_details(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_login'))

    total_item_cart = 0
    if request.user.is_authenticated:
        items = OrderItem.objects.filter(user=request.user)
        for item in items:
            total_item_cart += item.quantity

    orders = FullOrder.objects.filter(user=request.user).order_by('-date_ordered')

    ordered = []
    for order in orders:
        tt = []
        items = Purchased_item.objects.filter(order=order)
        for item in items:
            tt.append(item)
        ordered.append({'order': order, 'items': tt})

    product_categories = ProductCategories.objects.all()

    context = {
        'product_categories': product_categories,
        'ordered': ordered,
        'total_item_cart': total_item_cart,
    }
    return render(request, 'store/order_details.html', context)


def show_items(request, id):
    total_item_cart = 0

    if request.user.is_authenticated:
        items = OrderItem.objects.filter(user=request.user)
        for item in items:
            total_item_cart += item.quantity

    product_category = ProductCategories.objects.get(id=id)
    products = Product.objects.filter(category=product_category)

    product_categories = ProductCategories.objects.all()

    context = {
        'product_categories': product_categories,
        'product_category': product_category,
        'products': products,
        'total_item_cart': total_item_cart,
    }
    return render(request, 'store/show_items.html', context)


# Realizar Pago via AdamsPay
def payment_api(request):
    # Usar 'environ variables' por motivos de seguridad
    load_dotenv()
    apikey = os.environ.get("apikey")
    url = "https://staging.adamspay.com/api/v1/debts"
    headers = {
      'apikey': apikey,
      'Content-Type': 'application/json'
    }
    # Hora en UTC!
    inicio_validez = datetime.datetime.utcnow().replace()
    fin_validez = inicio_validez + datetime.timedelta(days=2)
    # Extraer Dinamicamente: Costo Total & Nombre del Item en el Carrito de Compras
    total_cost_cart = 0
    total_item_cart = 0
    if request.user.is_authenticated:
        items = OrderItem.objects.filter(user=request.user)
        for item in items:
            total_item_cart += item.quantity

        for item in items:
            total_cost_cart += item.get_total
            # Extraer el nombre del item dinamicamente
            # todo considerar casos de multiples items, pendiente
            item_name = item.product.name

        payload = {
                    "debt": {
                        # "docId": "", (OPCIONAL)
                        "amount": {
                            "currency": "PYG",
                            "value": str(total_cost_cart)
                        },
                        "label": item_name,
                        "slug": "Ecom850",
                        "validPeriod": {
                            "start": inicio_validez.strftime("%Y-%m-%dT%H:%M:%S"),
                            "end": fin_validez.strftime("%Y-%m-%dT%H:%M:%S")
                        }
                    }
                  }
    # Respuesta del pedido POST
    response = requests.post(url, headers=headers, json=payload)
    # Serializar la respuesta a un formato JSON
    response_json = response.json()
    # Configurar Pretty Printer
    pp = pprint.PrettyPrinter(indent=2)
    if response.ok:
        debt = response_json["debt"]
        print("Deuda creada exitosamente")
        print("URL=" + debt["payUrl"])
        context = {'status_de_transaccion': 'Tu pago a sido procesado. Gracias, esperamos volver a verlo pronto'}
        return render(request, "store/thankyou.html", context)
    else:
        print("# Error")
        print("====================Status Code====================")
        print(response.status_code)
        print("====================Body====================")
        print(response.text)
        print("====================Payload:Raw====================")
        print(payload)
        print("====================JSON====================")
        if "meta" in response_json:
            pp.pprint(response_json["meta"])
        context = {'status_de_transaccion': 'Tu pago no pudo ser procesado. Intentelo nuevamente.'}
        return render(request, "store/thankyou.html", context)

