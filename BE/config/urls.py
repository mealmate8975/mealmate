from django.contrib import admin
from django.urls import path,include
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include("accounts.urls", namespace="accounts")),
    path('accounts/',include('accounts.urls')),
    path('friendships/',include('friendships.urls')),
]
