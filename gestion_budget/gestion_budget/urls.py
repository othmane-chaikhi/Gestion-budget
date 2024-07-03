from django.contrib import admin
from django.urls import include, path
from myapp import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('edit_transaction/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    path('delete_transaction/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('reset_transactions/', views.reset_transactions, name='reset_transactions'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('download_excel_report/', views.download_excel_report, name='download_excel_report'),
    path('download_pdf_report/', views.download_pdf_report, name='download_pdf_report'),
]