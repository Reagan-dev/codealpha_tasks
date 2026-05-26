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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# app_name names this URL module as "menu" so project URLs can include it with
# a namespace.
#
# menu_item_collection_view sends POST requests to MenuItemCreateView and all
# other requests to MenuItemListView. It exists because GET and POST both use
# /api/menu/items/, but they are handled by separate class-based views.
#
# urlpatterns maps each menu URL to a view with a descriptive route name.
#
# Important decisions that were made and why
#
# path() is used for every route because these URLs do not need regular
# expressions.
#
# The create and list menu item endpoints share one path to keep the API REST
# shaped: list with GET and create with POST on the same collection URL.
#
# What you should read and understand before you review the code
#
# Read Django path(), app_name, and include namespaces.
#
# Read how Django resolves URL patterns before DRF checks allowed methods.
#
# ============================================================
# END OF REVIEW
# ============================================================
