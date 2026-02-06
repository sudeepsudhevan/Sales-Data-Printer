from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.index, name='index'),
    path('money-received/', views.money_received, name='money_received'),
    path('item-sold/', views.item_sold, name='item_sold'),
    path('delete-money/<int:pk>/', views.delete_money, name='delete_money'),
    path('delete-item/<int:pk>/', views.delete_item, name='delete_item'),
    path('pdf-report/', views.pdf_report, name='pdf_report'),
    path('backup/', views.backup_database, name='backup_database'),
    path('backups/', views.backup_list, name='backup_list'),
    path('restore/<str:filename>/', views.restore_backup, name='restore_backup'),
]
