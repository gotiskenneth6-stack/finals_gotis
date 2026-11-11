from django.contrib.auth.models import AbstractUser
from django.db import models
 
 
class BaseUser(AbstractUser):
    # username, email, password, first_name, last_name, is_active come from AbstractUser
    middle_name = models.CharField(max_length=150, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
 
    class Meta:
        db_table = "base_users"
 
 
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=64, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    thumbnail = models.ImageField(upload_to="thumbnails/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = "products"
 
    def __str__(self):
        return self.name
 
 
class Cart(models.Model):
    owner = models.ForeignKey(BaseUser, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = "carts"
 
 
class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_products")
    quantity = models.PositiveIntegerField(default=1)
 
    class Meta:
        db_table = "cart_products"
 
 
class Transaction(models.Model):
    buyer = models.ForeignKey(BaseUser, on_delete=models.CASCADE, related_name="transactions")
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        db_table = "transactions"
 
 
class ProductTransaction(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="product_transactions")
    item = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_transactions")
    quantity = models.PositiveIntegerField(default=1)
 
    class Meta:
        db_table = "product_transactions"
