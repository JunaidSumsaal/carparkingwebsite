from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('auth_service.urls')),  # 🔹 new microservice (signup/login APIs)
    path('', include('app.urls')),                # 🔹 your existing app
]
