import json
from .models import Product, Customer, Order, OrderItem

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES.get('cart', '{}'))
    except json.JSONDecodeError:
        cart = {}

    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = 0

    for product_id, item_data in cart.items():
        try:
            quantity = item_data.get('quantity', 0)
            if quantity <= 0:
                continue

            product = Product.objects.get(id=product_id)
            total = product.price * quantity

            order['get_cart_total'] += total
            order['get_cart_items'] += quantity
            cartItems += quantity

            items.append({
                'id': product.id,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL,
                },
                'quantity': quantity,
                'digital': product.digital,
                'get_total': total,
            })

            if not product.digital:
                order['shipping'] = True
        except Product.DoesNotExist:
            continue

    return {
        'cartItems': cartItems,
        'order': order,
        'items': items,
    }

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, _ = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookie_data = cookieCart(request)
        cartItems = cookie_data['cartItems']
        order = cookie_data['order']
        items = cookie_data['items']

    return {
        'cartItems': cartItems,
        'order': order,
        'items': items,
    }

def guestOrder(request, data):
    name = data['form'].get('name')
    email = data['form'].get('email')

    cookie_data = cookieCart(request)
    items = cookie_data['items']

    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()

    order = Order.objects.create(customer=customer, complete=False)

    for item in items:
        product = Product.objects.get(id=item['id'])
        OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity'],
        )

    return customer, order
