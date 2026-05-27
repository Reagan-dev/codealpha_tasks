from django.urls import path

from .views import (
    CategoryListView,
    MenuItemCreateView,
    MenuItemDetailView,
    MenuItemListView,
    MenuItemUpdateView,
)


app_name = "menu"


def menu_item_collection_view(request, *args, **kwargs):
    """Route menu item collection requests to the correct class-based view."""
    if request.method == "POST":
        return MenuItemCreateView.as_view()(request, *args, **kwargs)

    return MenuItemListView.as_view()(request, *args, **kwargs)


urlpatterns = [
    path(
        "categories/",
        CategoryListView.as_view(),
        name="category-list",
    ),
    path(
        "items/",
        menu_item_collection_view,
        name="menu-item-list-create",
    ),
    path(
        "items/<int:pk>/",
        MenuItemDetailView.as_view(),
        name="menu-item-detail",
    ),
    path(
        "items/<int:pk>/manage/",
        MenuItemUpdateView.as_view(),
        name="menu-item-manage",
    ),
]



