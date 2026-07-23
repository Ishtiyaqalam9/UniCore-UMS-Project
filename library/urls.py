from django.urls import path

from accounts.decorators import admin_required

from . import views

urlpatterns = [
    path("", admin_required(views.library_list), name="library_list"),
    path("add/", admin_required(views.add_book), name="add_book"),
    path("<str:id>/edit/", admin_required(views.edit_book), name="edit_book"),
    path("<str:id>/delete/", admin_required(views.delete_book), name="delete_book"),
    path("<str:id>/issue/", admin_required(views.issue_book), name="issue_book"),
    path("issues/", admin_required(views.issue_list), name="issue_list"),
    path("issues/<str:id>/return/", admin_required(views.return_book), name="return_book"),
    path("portal/catalog/", views.member_library_catalog, name="member_library_catalog"),
    path("portal/catalog/<str:id>/issue/", views.self_issue_book, name="self_issue_book"),
    path("portal/my-books/", views.my_library, name="my_library"),
    path("portal/my-books/<str:id>/return/", views.member_return_book, name="member_return_book"),
]
