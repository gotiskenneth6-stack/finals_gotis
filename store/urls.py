from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register("users", views.BaseUserViewSet)
router.register("products", views.ProductViewSet)
router.register("carts", views.CartViewSet)
router.register("cart-products", views.CartProductViewSet)
router.register("transactions", views.TransactionViewSet)
router.register("product-transactions", views.ProductTransactionViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("login/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
]