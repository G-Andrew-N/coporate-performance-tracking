from django.urls import path, include
from . import views

urlpatterns = [
    # Home and Authentication
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_view, name='logout_view'),  
    path("signup/", views.signup, name="signup"),
    
    path('admin-panel/', views.admin_panel, name='admin_panel'),

    # Role-Based Redirect and Panels
    path('redirect/', views.role_based_redirect, name='role_based_redirect'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('agent-workpage/', views.agent_workpage, name='agent_workpage'),

    # Task Management
    path('assign-task/', views.assign_task, name='assign_task'),
    path('edit-task/<uuid:task_id>/', views.edit_task, name='edit_task'),
    path('delete-task/<uuid:task_id>/', views.delete_task, name='delete_task'),
    path('tasks/', views.task_performance, name='task_performance'),
    path('tasks/<uuid:task_id>/update/', views.update_task_status, name='update_task_status'),

    # Property Management
    path('property_list/', views.property_list, name='property_list'),
    path('property/<uuid:pk>/', views.property_detail, name='property_detail'),
    path('property/add/', views.property_add, name='property_add'),
    path('property/<uuid:pk>/edit/', views.property_edit, name='property_edit'),
    path('property/<uuid:pk>/delete/', views.property_delete, name='property_delete'),
    path('property/<uuid:property_id>/make_sale/', views.make_sale, name='make_sale'),
    path('property/<uuid:pk>/update_status/', views.update_property_status, name='update_property_status'),
    path('export_properties/', views.export_properties, name='export_properties'),
    path('sale_success/', views.sale_success, name='sale_success'),

    # Sales Management
    path('property/<uuid:property_id>/make_sale/', views.make_sale, name='make_sale'),
    
    
    path('tasks/<uuid:task_id>/update/', views.update_task_status, name='update_task_status'),
    path('tasks/<uuid:task_id>/', views.task_detail, name='task_detail'),
    
    
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.add_employee, name='add_employee'),
    path('employees/edit/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('employees/delete/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    
    path('profile/', views.user_profile_view, name='user_profile'),



    path('predict/revenue/', views.predict_revenue, name='predict_revenue'),
    path('predict/property-price/', views.predict_property_price, name='predict_property_price'),
]