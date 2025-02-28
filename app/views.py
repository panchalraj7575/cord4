import json
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import get_object_or_404
from .models import Category, Product
from .serializers import (
    UserSerializer,
    CategorySerializer,
    ProductSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)
from rest_framework_simplejwt.exceptions import TokenError
from django.db import transaction
from .serializers import BulkUploadSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


class RegisterView(generics.CreateAPIView):
    """
    Handles user registration.
    """

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class LoginView(APIView):
    """
    Handles user login.
    """

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response({"refresh": str(refresh), "access": str(refresh.access_token)})


class LogoutView(APIView):
    """
    Handles user logout.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logged out successfully"}, status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CategoryListCreateView(generics.ListCreateAPIView):
    """
    Handles listing categories (public) and creating categories (admin only).
    """

    queryset = Category.objects.filter(is_deleted=False)
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"error": "Only admins can create categories"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving (public), updating (admin only),
    and soft deleting (admin only) a specific category.
    """

    queryset = Category.objects.filter(is_deleted=False)
    serializer_class = CategorySerializer

    def patch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"error": "Only admins can update categories"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"error": "Only admins can delete categories"},
                status=status.HTTP_403_FORBIDDEN,
            )
        category = self.get_object()
        category.is_deleted = True
        category.save()
        return Response(
            {"message": "Category soft deleted"}, status=status.HTTP_204_NO_CONTENT
        )


class ProductListCreateView(generics.ListCreateAPIView):
    """
    Handles listing products (public) and creating products (admin only).
    """

    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"error": "Only admins can create products"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)


class ProductDetailView(APIView):
    """
    Handles retrieving (public), updating (admin only),
    and soft deleting (admin only) a specific product.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, is_deleted=False)
        return Response(ProductSerializer(product).data)

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"error": "Only admins can update products"},
                status=status.HTTP_403_FORBIDDEN,
            )
        product = get_object_or_404(Product, pk=pk, is_deleted=False)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"error": "Only admins can delete products"},
                status=status.HTTP_403_FORBIDDEN,
            )
        product = get_object_or_404(Product, pk=pk, is_deleted=False)
        product.is_deleted = True
        product.save()
        return Response(
            {"message": "Product soft deleted"}, status=status.HTTP_204_NO_CONTENT
        )


class ForgotPasswordView(APIView):
    """
    Handles sending a password reset link to the user's email.
    """

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.send_reset_email()
            return Response(
                {"message": "Password reset link sent."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """
    Handles resetting the user's password using a valid token.
    """

    def post(self, request, uid, token):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(uid, token)
            return Response(
                {"message": "Password reset successful"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BulkUploadAPIView(APIView):
    """
    Handles bulk upload of categories and products.
    - Only admins can perform bulk upload.
    - Skips existing categories and products to avoid duplication.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_staff:
            raise PermissionDenied("Only admins can perform bulk upload.")

        serializer = BulkUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        categories_data = serializer.validated_data.get("categories", [])
        products_data = serializer.validated_data.get("products", [])

        created_categories = []
        created_products = []

        # Categories
        with transaction.atomic():
            for cat_data in categories_data:
                category, created = Category.objects.get_or_create(
                    category_name=cat_data["category_name"],
                    defaults={"description": cat_data.get("description", "")},
                )
                if created:
                    created_categories.append(category.category_name)

        # Products
        with transaction.atomic():
            for prod_data in products_data:
                category_name = prod_data.pop("category_name", None)
                if not category_name:
                    return Response(
                        {"error": "category_name is required for products"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                category = Category.objects.filter(category_name=category_name).first()
                if not category:
                    return Response(
                        {"error": f"Category '{category_name}' not found"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                product, created = Product.objects.get_or_create(
                    product_name=prod_data["product_name"],
                    category=category,
                    defaults={
                        "product_description": prod_data.get("product_description", ""),
                        "product_price": prod_data.get("product_price", 0),
                        "currency": prod_data.get("currency", "INR"),
                        "stock_quantity": prod_data.get("stock_quantity", 0),
                        "sku": prod_data.get("sku", ""),
                        "image_url": prod_data.get("image_url", ""),
                    },
                )
                if created:
                    created_products.append(product.product_name)

        return Response(
            {
                "message": "Bulk upload successful",
                "created_categories": created_categories,
                "created_products": created_products,
            },
            status=status.HTTP_201_CREATED,
        )
