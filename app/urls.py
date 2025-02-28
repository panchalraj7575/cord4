from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ForgotPasswordView,
    CategoryListCreateView,
    CategoryDetailView,
    ProductListCreateView,
    ProductDetailView,
    BulkUploadAPIView,
    ResetPasswordView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("forgot-password/", ForgotPasswordView.as_view()),
    path(
        "reset-password/<str:uid>/<str:token>/",
        ResetPasswordView.as_view(),
        name="reset-password",
    ),
    path("category/", CategoryListCreateView.as_view()),
    path("category/<int:pk>/", CategoryDetailView.as_view()),
    path("product/", ProductListCreateView.as_view()),
    path("product/<int:pk>/", ProductDetailView.as_view()),
    path("bulk-upload/", BulkUploadAPIView.as_view(), name="bulk-upload"),
]
