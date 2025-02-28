from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Product
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
import re


# ✅ User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "email", "password", "is_staff"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        """Custom password validation"""
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not any(char.islower() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one numeric digit."
            )
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )
        return value

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user


# ✅ Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "category_name", "description", "is_deleted"]


# ✅ Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.category_name")

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "category_name",
            "product_name",
            "product_description",
            "product_price",
            "currency",
            "stock_quantity",
            "sku",
            "image_url",
            "is_deleted",
        ]


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = get_user_model().objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError("No account found with this email.")
        return value

    def send_reset_email(self):
        email = self.validated_data["email"]
        user = get_user_model().objects.get(email=email)
        token = default_token_generator.make_token(user)
        reset_link = f"http://localhost:8000/reset-password/{user.pk}/{token}/"

        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_link}",
            from_email="your-email@gmail.com",
            recipient_list=[email],
            fail_silently=False,
        )


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        """Custom password validation"""
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not any(char.islower() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one numeric digit."
            )
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )
        return value

    def validate(self, data):
        """Check if passwords match"""
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return data

    def save(self, uid, token):
        """Reset the password"""
        try:
            user = get_user_model().objects.get(pk=uid)
            if not default_token_generator.check_token(user, token):
                raise serializers.ValidationError("Invalid or expired token")

            user.set_password(self.validated_data["password"])
            user.save()
        except Exception as e:
            raise serializers.ValidationError("Invalid reset link")


class BulkUploadSerializer(serializers.Serializer):
    categories = serializers.ListField(child=serializers.DictField(), required=False)
    products = serializers.ListField(child=serializers.DictField(), required=False)
