"""
URL configuration for wordnest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path, re_path
from django.views.defaults import page_not_found
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(
        r"^accounts/email/$",
        page_not_found,
        {"exception": Exception("Not Found")},
        name="account_email",
    ),
    path("accounts/", include("allauth.urls")),
    path(
        "terms-conditions/",
        TemplateView.as_view(template_name="terms_conditions.html"),
        name="terms_conditions",
    ),
    path(
        "privacy-policy/",
        TemplateView.as_view(template_name="privacy_policy.html"),
        name="privacy-policy",
    ),
    path("", include("dictionary.urls")),
]
