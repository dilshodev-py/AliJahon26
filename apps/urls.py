from django.urls import path

from apps.views import HomeListView, ProductDetailView, LoginFormView, CategoryListView, ProfileFormView, \
    get_districts, wishlist_view, MarketListView, WishListView, OrderFormView, ThreadStatisticListView

urlpatterns = [
    path('', HomeListView.as_view() , name = 'home'),
    path('product/<str:slug>', ProductDetailView.as_view() , name = 'product-detail'),
    path('category/<str:slug>', CategoryListView.as_view() , name = 'category-list'),
    path('market/<str:slug>', MarketListView.as_view() , name = 'market-list'),

]

urlpatterns += [
    path('login', LoginFormView.as_view(), name='login'),
    path('profile', ProfileFormView.as_view(), name='profile'),
    path('district-list', get_districts, name='get_districts'),
    path('wishlist', wishlist_view, name='wishlist'),
    path('wishlist/list', WishListView.as_view(), name='wishlist-list'),
    path('order', OrderFormView.as_view(), name='order'),
    path('thread-statistic', ThreadStatisticListView.as_view(), name='thread-statistic'),
]
