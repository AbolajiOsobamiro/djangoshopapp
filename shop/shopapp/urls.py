from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<slug:slug>/', views.page_view, name='page_view'),
    path('categories/', views.category_view, name = 'category_view'),
    path('products/<slug:slug>/', views.product_page, name="product_page"),
    path('product_upload', views.product_upload, name='product_upload'),
    path('trader/<str:username>/', views.traders_page, name='traders_page'),
    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('confirm_payment/<int:pk>/', views.confirm_payment, name='confirm_payment'),
    path('product/<int:product_id>/submit_review/', views.submit_review, name='submit_review'),
    path('cart/', views.my_cart, name='user_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('search', views.search, name='search'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name= 'logout'),
    path('login', views.login, name='login')
]
