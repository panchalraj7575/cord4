from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Product


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("id", "email", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )
    search_fields = ("email",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category_name", "is_deleted")
    search_fields = ("category_name",)
    list_filter = ("is_deleted",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "product_name", "category", "product_price", "is_deleted")
    search_fields = ("product_name", "category__category_name")
    list_filter = ("category", "is_deleted")
