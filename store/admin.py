from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import BaseUser, Product, Cart, CartProduct, Transaction, ProductTransaction


class BaseUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Extra", {"fields": ("middle_name", "gender", "avatar")}),
    )


admin.site.register(BaseUser, BaseUserAdmin)
for m in (Product, Cart, CartProduct, Transaction, ProductTransaction):
    admin.site.register(m)