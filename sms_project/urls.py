from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from django.views.static import serve as static_serve

from accounts.forms import RoleAuthenticationForm

urlpatterns = [
    path("", include("accounts.urls")),
    path("", include("home.urls")),
    path("student/", include("student.urls")),
    path("teacher/", include("teacher.urls")),
    path("library/", include("library.urls")),
    path("academic/", include("academic.urls")),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=RoleAuthenticationForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
]

# Local static-file fallback. This keeps the UMS interface styled even when
# DJANGO_DEBUG is disabled or the project is started without collectstatic.
urlpatterns += [
    re_path(
        r"^static/(?P<path>.*)$",
        static_serve,
        {"document_root": settings.BASE_DIR / "static"},
    ),
]
