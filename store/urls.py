from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('', views.store, name='store'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('product/<int:product_id>/', views.product_detail, name='product-detail'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update_item/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove_item/', views.remove_cart_item, name='remove_cart_item'),
    path('process_order/', views.process_order, name='process_order'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
]
