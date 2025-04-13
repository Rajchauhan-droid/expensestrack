from django.urls import path
from . import views
# from django.contrib.auth import views as auth_views

app_name = 'expenses'

urlpatterns = [
    # Home / Dashboard
    path('', views.dashboard_view, name='dashboard'),  # Set dashboard as homepage
    # path('home/', views.index, name='index'),  # Optional: if you want index.html, use a separate route

    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Category Views
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),

    # Expense Views
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_create, name='add_expense'),
    path('expenses/edit/<int:pk>/', views.expense_update, name='edit_expense'),
    path('expenses/delete/<int:pk>/', views.expense_delete, name='delete_expense'),

    path('currency_converter/', views.currency_converter, name='currency_converter'),


    # Budget (optional/future)
    # path('budget/', views.budget_view, name='budget'),
    
    # Legacy or placeholder route (optional)
    # path('category_list/', views.category_view, name='category_list'),

    #finance
    path('goal/delete/<int:goal_id>/', views.delete_goal, name='delete_goal'),
    path('goals/', views.view_goals, name='view_goals'),  # View all goals
    path('goal/add/', views.add_or_edit_goal, name='add_goal'),  # Add a goal
    path('goal/edit/<int:goal_id>/', views.add_or_edit_goal, name='edit_goal'),  # Make sure this is here



    path('expenses/export/csv/', views.export_expenses_csv, name='export_expenses_csv'),
    path('expenses/export/pdf/', views.export_expenses_pdf, name='export_expenses_pdf'),


]
