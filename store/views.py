from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Product, Category, Order, OrderItem, Review, Customer, ShippingAddress
from .forms import ReviewForm
import json
import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect

def get_cart_item_count(user):
    if not user.is_authenticated:
        return 0
    try:
        customer = Customer.objects.get(user=user)
        order = Order.objects.filter(customer=customer, complete=False).first()
    except Customer.DoesNotExist:
        return 0
    if order:
        return sum(item.quantity for item in order.orderitem_set.all())
    return 0


def store(request):
    categories = Category.objects.all()
    selected_category = request.GET.getlist('category')
    search_query = request.GET.get('search', '')
    products = Product.objects.all()

    if selected_category:
        products = products.filter(category__slug__in=selected_category).distinct()
    if search_query:
        products = products.filter(name__icontains=search_query)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'cartItems': get_cart_item_count(request.user),
    }
    return render(request, 'store/store.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    review_form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'cartItems': get_cart_item_count(request.user),
    }
    return render(request, 'store/product_detail.html', context)


@login_required
def cart(request):
    try:
        customer = Customer.objects.get(user=request.user)
        order = Order.objects.filter(customer=customer, complete=False).first()
    except Customer.DoesNotExist:
        order = None

    items = []
    total_price = 0
    if order:
        items = order.orderitem_set.all()
        for item in items:
            item.total_price = item.quantity * item.product.price
            total_price += item.total_price

    context = {
        'order': order,
        'items': items,
        'total_price': total_price,
        'cartItems': get_cart_item_count(request.user),
    }
    return render(request, 'store/cart.html', context)


@login_required
@require_POST
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('productId')
        quantity = int(data.get('quantity', 1))
        if quantity < 1:
            quantity = 1

        product = Product.objects.get(id=product_id)
        customer = Customer.objects.get(user=request.user)
        order, _ = Order.objects.get_or_create(customer=customer, complete=False)
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

        if not created:
            order_item.quantity += quantity
        else:
            order_item.quantity = quantity
        order_item.save()

        cart_item_count = sum(item.quantity for item in order.orderitem_set.all())
        total_price = sum(item.quantity * item.product.price for item in order.orderitem_set.all())

        return JsonResponse({
            'success': True,
            'cartItemCount': cart_item_count,
            'totalPrice': str(total_price),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def update_cart_item(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('itemId')
        action = data.get('action')  # expected: 'add', 'remove', or 'set'
        quantity = int(data.get('quantity', 1))

        customer = Customer.objects.get(user=request.user)
        order = Order.objects.get(customer=customer, complete=False)
        order_item = order.orderitem_set.get(id=item_id)

        if action == 'add':
            order_item.quantity += 1
        elif action == 'remove':
            order_item.quantity -= 1
        elif action == 'set':
            order_item.quantity = max(quantity, 1)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)

        if order_item.quantity <= 0:
            order_item.delete()
            message = 'Item removed'
            new_quantity = 0
            deleted = True
        else:
            order_item.save()
            message = 'Quantity updated'
            new_quantity = order_item.quantity
            deleted = False

        cart_item_count = sum(item.quantity for item in order.orderitem_set.all())
        total_price = sum(item.quantity * item.product.price for item in order.orderitem_set.all())

        return JsonResponse({
            'success': True,
            'message': message,
            'new_quantity': new_quantity,
            'cartItemCount': cart_item_count,
            'totalPrice': str(total_price),
            'deleted': deleted
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def remove_cart_item(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('itemId')

        customer = Customer.objects.get(user=request.user)
        order = Order.objects.get(customer=customer, complete=False)
        order_item = order.orderitem_set.get(id=item_id)
        order_item.delete()

        cart_item_count = sum(item.quantity for item in order.orderitem_set.all())
        total_price = sum(item.quantity * item.product.price for item in order.orderitem_set.all())

        return JsonResponse({
            'success': True,
            'cartItemCount': cart_item_count,
            'totalPrice': str(total_price),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return JsonResponse({'success': True, 'message': 'Review submitted successfully.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('store:store')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('store:store')  


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('store:store') 
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})


def checkout(request):
    context = {}  
    return render(request, 'store/checkout.html', context)


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'store/category.html', context)


@csrf_exempt
def process_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        transaction_id = datetime.datetime.now().timestamp()

        if request.user.is_authenticated:
            try:
                customer = Customer.objects.get(user=request.user)
            except Customer.DoesNotExist:
                return JsonResponse({'error': 'Customer not found for user.'}, status=400)
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
        else:
            name = data['form']['name']
            email = data['form']['email']
            customer, created = Customer.objects.get_or_create(email=email)
            customer.name = name
            customer.save()
            order = Order.objects.create(customer=customer, complete=False)

        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == float(order.get_cart_total):
            order.complete = True
        order.save()

        if order.shipping:
            ShippingAddress.objects.create(
                customer=order.customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
                country=data['shipping']['country'],
            )

        return JsonResponse('Payment completed!', safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('store:store')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})
