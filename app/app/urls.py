from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

schema = get_schema_view(
    title="ProductsAPI",
    description="API for managing products"
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.obtain_auth_token),
    path('', include('products.urls')),
    path('schema/', schema),
    path('docs/', include_docs_urls(title="ProductsAPI")),
]
