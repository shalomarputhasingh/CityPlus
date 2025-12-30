from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('dj-admin/', admin.site.urls),
    path('', include('core.urls')),
    path('auth/', include('authentication.urls')),
    path('citizen/', include('citizen.urls')),
    path('portal/', include('admin_portal.urls')),
]
