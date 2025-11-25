from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from procurement.views import UserViewSet, PurchaseRequestViewSet, ApprovalViewSet

# Health check view
def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'procure-to-pay-backend'})

# API Router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'requests', PurchaseRequestViewSet, basename='purchaserequest')
router.register(r'approvals', ApprovalViewSet, basename='approval')

# Swagger documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Procure-to-Pay API",
        default_version='v1',
        description="API for Purchase Request and Approval System",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@procure2pay.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Health check endpoint
    path('health/', health_check, name='health_check'),

    # API URLs
    path('api/', include(router.urls)),

    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
