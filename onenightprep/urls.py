
from django.contrib import admin
from django.urls import path,include
from ai.health import HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('ai/', include('ai.urls')),
    path('session/', include('session.urls')),
    path('video/', include('videosummerization.urls')),
    path('health/', HealthCheckView.as_view(), name='health_check'),
]
