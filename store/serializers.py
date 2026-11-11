
from rest_framework import serializers
from .models import (
    BaseUser,
    Product,
    Cart,
    CartProduct,
    Transaction,
    ProductTransaction
)


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseUser
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "middle_name",
            "last_name",
            "gender",
            "avatar",
            "is_active"
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        return BaseUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class CartProductSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(
        source="product",
        read_only=True
    )

    class Meta:
        model = CartProduct
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    cart_products = CartProductSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Cart
        fields = [
            "id",
            "owner",
            "created_at",
            "updated_at",
            "cart_products"
        ]


class ProductTransactionSerializer(serializers.ModelSerializer):
    item_detail = ProductSerializer(
        source="item",
        read_only=True
    )

    class Meta:
        model = ProductTransaction
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    product_transactions = ProductTransactionSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "buyer",
            "created_at",
            "product_transactions"
        ]
