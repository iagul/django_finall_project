from .models import Category, Order, Customer

def categories_processor(request):
    return {
        'categories': Category.objects.all()
    }

def cart_items_processor(request):
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            order = Order.objects.filter(customer=customer, complete=False).first()
            if order:
                cart_items_count = sum(item.quantity for item in order.orderitem_set.all())
                return {'cartItems': cart_items_count}
        except Customer.DoesNotExist:
            pass
    return {'cartItems': 0}
