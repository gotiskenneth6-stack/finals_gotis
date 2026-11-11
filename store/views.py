from django.db import transaction as db_transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import BaseUser, Product, Cart, CartProduct, Transaction, ProductTransaction
from .serializers import (BaseUserSerializer, ProductSerializer, CartSerializer,
                          CartProductSerializer, TransactionSerializer,
                          ProductTransactionSerializer)


def get_latest_cart(user):
    return Cart.objects.filter(owner=user).order_by("-created_at", "-id").first()


class BaseUserViewSet(viewsets.ModelViewSet):
    queryset = BaseUser.objects.all()
    serializer_class = BaseUserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return super().get_permissions()


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["get"])
    def mine(self, request):
        cart = get_latest_cart(request.user) or Cart.objects.create(owner=request.user)
        return Response(self.get_serializer(cart).data)

    @action(detail=False, methods=["post"])
    def add(self, request):
        try:
            product = Product.objects.get(pk=request.data.get("product"), is_active=True)
            qty = int(request.data.get("quantity", 1))
        except (Product.DoesNotExist, ValueError, TypeError):
            return Response({"detail": "Invalid product or quantity."},
                            status=status.HTTP_400_BAD_REQUEST)
        if qty < 1:
            return Response({"detail": "Quantity must be at least 1."},
                            status=status.HTTP_400_BAD_REQUEST)

        cart = get_latest_cart(request.user) or Cart.objects.create(owner=request.user)
        existing = CartProduct.objects.filter(cart=cart, product=product).first()
        new_qty = (existing.quantity if existing else 0) + qty
        if new_qty > product.stock:
            return Response({"detail": f"Only {product.stock} in stock for {product.name}."},
                            status=status.HTTP_400_BAD_REQUEST)

        CartProduct.objects.update_or_create(
            cart=cart, product=product, defaults={"quantity": new_qty}
        )
        return Response(self.get_serializer(cart).data)


class CartProductViewSet(viewsets.ModelViewSet):
    queryset = CartProduct.objects.all()
    serializer_class = CartProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartProduct.objects.filter(cart__owner=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Transaction.objects.none()
        if user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(buyer=user)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def checkout(self, request):
        cart = get_latest_cart(request.user)
        items = list(cart.cart_products.select_related("product")) if cart else []

        if not items:
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        for item in items:
            if not item.product.is_active:
                return Response({"detail": f"{item.product.name} is not available."},
                                status=status.HTTP_400_BAD_REQUEST)
            if item.quantity > item.product.stock:
                return Response({"detail": f"Not enough stock for {item.product.name}."},
                                status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            txn = Transaction.objects.create(buyer=request.user)
            for item in items:
                ProductTransaction.objects.create(
                    transaction=txn, item=item.product, quantity=item.quantity
                )
                item.product.stock -= item.quantity
                item.product.save()
            cart.cart_products.all().delete()

        return Response(TransactionSerializer(txn).data, status=status.HTTP_201_CREATED)


class ProductTransactionViewSet(viewsets.ModelViewSet):
    queryset = ProductTransaction.objects.all()
    serializer_class = ProductTransactionSerializer