from django.contrib import admin
from .models import Category, Product

admin.site.register(Category)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    fields = ('category', 'name', 'price', 'image', 'description')
    search_fields = ('name',)
    list_filter = ('category',)

admin.site.register(Product, ProductAdmin)
