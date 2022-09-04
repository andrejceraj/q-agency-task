from django.contrib import admin
from django.urls import include, path
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view

schema = get_schema_view(
    title="ProductsAPI",
    description="API for managing products"
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls')),
    path('schema/', schema),
    path('docs/', include_docs_urls(title="ProductsAPI")),
]
