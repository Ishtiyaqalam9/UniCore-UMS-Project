from .utils import get_user_profile, get_user_role


def role_context(request):
    return {
        "ums_role": get_user_role(request.user),
        "ums_profile": get_user_profile(request.user),
    }
