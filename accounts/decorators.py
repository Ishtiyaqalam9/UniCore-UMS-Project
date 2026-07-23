from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

from .models import UserProfile
from .utils import get_user_role


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            role = get_user_role(request.user)
            if role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You do not have permission to open that page.")
            if role == UserProfile.STUDENT:
                return redirect("student_portal")
            if role == UserProfile.TEACHER:
                return redirect("teacher_portal")
            if role == UserProfile.ADMIN:
                return redirect("home")
            return redirect("login")

        return wrapped

    return decorator


admin_required = role_required(UserProfile.ADMIN)
student_required = role_required(UserProfile.STUDENT)
teacher_required = role_required(UserProfile.TEACHER)
