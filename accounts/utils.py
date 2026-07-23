from .models import UserProfile


def get_user_role(user):
    if not getattr(user, "is_authenticated", False):
        return None
    if user.is_superuser or user.is_staff:
        return UserProfile.ADMIN
    try:
        return user.ums_profile.role
    except UserProfile.DoesNotExist:
        return None


def get_user_profile(user):
    if not getattr(user, "is_authenticated", False):
        return None
    try:
        return user.ums_profile
    except UserProfile.DoesNotExist:
        return None


def user_reference(user):
    profile = get_user_profile(user)
    return profile.reference_id if profile else ""
