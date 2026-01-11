from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('money-received/', views.money_received, name='money_received'),
    path('item-sold/', views.item_sold, name='item_sold'),
    path('delete-money/<int:pk>/', views.delete_money, name='delete_money'),
    path('delete-item/<int:pk>/', views.delete_item, name='delete_item'),
    path('pdf-report/', views.pdf_report, name='pdf_report'),
]
