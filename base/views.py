from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from .models import PropertyListing, Task, Sale, Employee, PerformanceMetrics, ProductivityTracker, Revenue, PredefinedTask
from .forms import PropertyListingForm
from uuid import UUID
from django.db import models  # Add this import
from django.db.models import Sum  # Add this import
from django.contrib import messages
from django.core.paginator import Paginator
import csv
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from datetime import datetime
from django.urls import reverse



from django.shortcuts import render
from django.db.models import Avg, Sum, Count
from .models import Employee, SalesRecord, ProductivityTracker, Revenue, PerformanceMetrics

import matplotlib.pyplot as plt
import io
import urllib, base64

def generate_chart(x, y, title, xlabel, ylabel):
    plt.figure(figsize=(10, 5))
    plt.plot(x, y, marker='o')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    buf.close()
    plt.close()
    return 'data:image/png;base64,' + urllib.parse.quote(string)

def home(request):
    # Agent Performance Metrics
    agent_performance = Employee.objects.annotate(avg_score=Avg('performancemetrics__customer_satisfaction'))

    # Trade Volume Trends
    sales_by_month = SalesRecord.objects.values('sale_date__month').annotate(total_sales=Sum('sale_price')).order_by('sale_date__month')
    months = [record['sale_date__month'] for record in sales_by_month]
    sales = [record['total_sales'] for record in sales_by_month]
    
    sales_chart = generate_chart(months, sales, "Monthly Sales Volume", "Month", "Sales Volume")

    # Productivity Trends
    productivity_data = ProductivityTracker.objects.values('date').annotate(total_hours=Sum('hours_worked')).order_by('date')
    dates = [record['date'] for record in productivity_data]
    hours = [record['total_hours'] for record in productivity_data]
    
    productivity_chart = generate_chart(dates, hours, "Productivity Over Time", "Date", "Hours Worked")

    # Revenue Trends
    revenue_data = Revenue.objects.values('year', 'month').annotate(total_revenue=Sum('total_revenue')).order_by('year', 'month')
    revenue_months = [f"{record['year']}-{record['month']:02d}" for record in revenue_data]
    revenues = [record['total_revenue'] for record in revenue_data]
    
    revenue_chart = generate_chart(revenue_months, revenues, "Revenue Trends", "Time", "Revenue")

    context = {
        'sales_chart': sales_chart,
        'productivity_chart': productivity_chart,
        'revenue_chart': revenue_chart,
        'agent_performance': agent_performance,
    }

    return render(request, 'base/home.html', context)





# Home View


# Login View
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect based on user role
            try:
                employee = Employee.objects.get(user=user)
                if employee.role == 'Admin':
                    return redirect('admin_panel')
                elif employee.role == 'Agent':
                    return redirect('agent_workpage')
                else:
                    return redirect('homie')  # Default redirect for other roles
            except Employee.DoesNotExist:
                return redirect('homie')  # Default redirect if no employee profile exists
        else:
            messages.error(request, "Username or password does not exist.")
    return render(request, 'base/login.html')


@login_required
def user_profile_view(request):
    # Get the logged-in user's Employee record
    employee = get_object_or_404(Employee, user=request.user)
    performance_metrics = PerformanceMetrics.objects.filter(employee=employee).first()
    sales = SalesRecord.objects.filter(agent=employee).order_by('-sale_date')[:10]

    # Data for charts
    task_status_counts = {
        'Pending': Task.objects.filter(assigned_to=employee, status='Pending').count(),
        'Completed': Task.objects.filter(assigned_to=employee, status='Completed').count(),
        'Overdue': Task.objects.filter(assigned_to=employee, status='Overdue').count(),
    }
    revenue_data = {
        'labels': list(Revenue.objects.values_list('month', flat=True).distinct()),
        'net_profits': list(Revenue.objects.values_list('net_profit', flat=True).distinct()),
    }

    context = {
        'user': employee.user,
        'employee': employee,
        'performance_metrics': performance_metrics,
        'sales': sales,
        'task_status_counts': list(task_status_counts.values()),
        'revenue_data': revenue_data,
    }
    return render(request, 'base/user_profile.html', context)


# Assign Task View
@login_required
def assign_task(request):
    # Fetch predefined tasks, agents, and assigned tasks
    predefined_tasks = PredefinedTask.objects.all()
    agents = Employee.objects.filter(role='Agent')
    assigned_tasks = Task.objects.filter(assigned_to__isnull=False)

    if request.method == 'POST':
        predefined_task_id = request.POST.get('predefined_task_id')
        employee_id = request.POST.get('employee_id')
        due_date_str = request.POST.get('due_date')

        try:
            # Validate predefined task and employee
            predefined_task = PredefinedTask.objects.get(id=predefined_task_id)
            employee = Employee.objects.get(id=employee_id)

            # Check if the employee is an agent
            if employee.role != 'Agent':
                messages.error(request, 'Selected user is not an agent.')
                return redirect(reverse('assign_task'))  # Use URL name

            # Validate due date
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            if due_date < datetime.now().date():
                messages.error(request, 'Due date cannot be in the past.')
                return redirect(reverse('assign_task'))  # Use URL name

            # Create a new Task instance
            Task.objects.create(
                predefined_task=predefined_task,
                assigned_to=employee,
                title=predefined_task.title,
                description=predefined_task.description,
                priority=predefined_task.priority,
                due_date=due_date,
                status='Pending'
            )
            messages.success(request, f'Task "{predefined_task.title}" assigned to {employee.user.get_full_name()}.')
            return redirect(reverse('assign_task'))  # Use URL name

        except PredefinedTask.DoesNotExist:
            messages.error(request, 'Invalid task selected.')
        except Employee.DoesNotExist:
            messages.error(request, 'Invalid employee selected.')
        except ValueError:
            messages.error(request, 'Invalid due date format.')

    # Render the template with context data
    return render(request, 'base/assign_task.html', {
        'predefined_tasks': predefined_tasks,
        'agents': agents,
        'assigned_tasks': assigned_tasks,
    })
    
@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    predefined_tasks = PredefinedTask.objects.all()
    agents = Employee.objects.filter(role='Agent')

    if request.method == 'POST':
        # Update task details
        task.predefined_task_id = request.POST.get('predefined_task_id')
        task.assigned_to_id = request.POST.get('employee_id')
        task.due_date = request.POST.get('due_date')
        task.status = request.POST.get('status', 'Pending')
        task.save()

        messages.success(request, 'Task updated successfully.')
        return redirect(reverse('assign_task'))

    return render(request, 'base/edit_task.html', {
        'task': task,
        'predefined_tasks': predefined_tasks,
        'agents': agents,
    })

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
    return redirect(reverse('assign_task'))


#employee management
@login_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'base/employee.html', {'employees': employees})

@login_required
def add_employee(request):
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        join_date = request.POST.get('join_date')

        # Create User
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        # Create Employee
        Employee.objects.create(
            user=user,
            role=role,
            join_date=join_date
        )

        messages.success(request, 'Employee added successfully.')
        return redirect('employee_list')

    return render(request, 'base/add_employee.html')

@login_required
def edit_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        # Update Employee details
        employee.user.first_name = request.POST.get('first_name')
        employee.user.last_name = request.POST.get('last_name')
        employee.user.email = request.POST.get('email')
        employee.role = request.POST.get('role')
        employee.join_date = request.POST.get('join_date')
        employee.user.save()
        employee.save()

        messages.success(request, 'Employee updated successfully.')
        return redirect('employee_list')

    return render(request, 'base/edit_employee.html', {'employee': employee})

@login_required
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        employee.user.delete()  # Delete the associated User
        employee.delete()  # Delete the Employee
        messages.success(request, 'Employee deleted successfully.')
    return redirect('employee_list')
    
    
    
# Property Views
def property_list(request):
    query = request.GET.get('q')  # Search query
    properties = PropertyListing.objects.all()

    if query:
        properties = properties.filter(
            Q(location__icontains=query) |
            Q(propertyType__icontains=query) |
            Q(address__icontains=query)
        )

    # Pagination
    paginator = Paginator(properties, 10)  # Show 10 properties per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'base/property.html', {'view_mode': 'list', 'page_obj': page_obj})

def property_detail(request, pk):
    property_item = get_object_or_404(PropertyListing, pk=pk)
    return render(request, 'base/property.html', {'view_mode': 'detail', 'property': property_item})

def property_add(request):
    if request.method == 'POST':
        form = PropertyListingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Property added successfully.')
            return redirect('property_list')
    else:
        form = PropertyListingForm()
    return render(request, 'base/property.html', {'view_mode': 'add', 'form': form})

def property_edit(request, pk):
    property_item = get_object_or_404(PropertyListing, pk=pk)
    if request.method == 'POST':
        form = PropertyListingForm(request.POST, request.FILES, instance=property_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Property updated successfully.')
            return redirect('property_list')
    else:
        form = PropertyListingForm(instance=property_item)
    return render(request, 'base/property.html', {'view_mode': 'edit', 'form': form})

def property_delete(request, pk):
    property_item = get_object_or_404(PropertyListing, pk=pk)
    if request.method == 'POST':
        property_item.delete()
        messages.success(request, 'Property deleted successfully.')
        return redirect('property_list')
    return render(request, 'base/property.html', {'view_mode': 'delete', 'property': property_item})

def update_property_status(request, pk):
    property_item = get_object_or_404(PropertyListing, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        property_item.status = new_status
        property_item.save()
        messages.success(request, 'Property status updated successfully.')
    return redirect('property_detail', pk=pk)

def export_properties(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="properties.csv"'

    writer = csv.writer(response)
    writer.writerow(['Address', 'Type', 'Location', 'Price', 'Status'])

    properties = PropertyListing.objects.all()
    for property in properties:
        writer.writerow([property.address, property.propertyType, property.location, property.price, property.status])

    return response
# Task Performance View
@login_required
def task_performance(request):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'No employee profile found for the user.'}, status=404)

    tasks = Task.objects.filter(assigned_to=employee)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='Completed').count()
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    context = {
        'agent': employee,
        'tasks': tasks,
        'performance': {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': round(completion_rate, 2),
        }
    }
    return render(request, 'base/task_performance.html', context)

# Update Task Status View
@login_required
def update_task_status(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
        new_status = request.POST.get('status')
        if new_status:
            task.status = new_status
            task.save()
        return redirect('task_performance')
    return JsonResponse({'error': 'Invalid request method'}, status=400)

# Make Sale View
@login_required
def make_sale(request, property_id):
    # Fetch the property
    property = get_object_or_404(PropertyListing, id=property_id)

    if request.method == 'POST':
        # Get the sale price from the form
        sale_price = request.POST.get('sale_price')

        # Validate the sale price
        if not sale_price:
            return render(request, 'base/make_sale.html', {
                'property': property,
                'error': 'Sale price is required.'
            })

        # Calculate profit (example: profit = sale_price - property price)
        profit = float(sale_price) - float(property.price)

        # Create the Sale record
        Sale.objects.create(
            agent=request.user,  # Logged-in user (agent)
            property=property,
            sale_price=sale_price,
            profit=profit,
            transaction_status='Successful'  # Default status
        )

        # Mark the property as sold
        property.status = 'Sold'
        property.save()

        # Redirect to the success page
        return redirect('sale_success')

    return render(request, 'base/make_sale.html', {'property': property})



@login_required
def sale_success(request):
    # Fetch all sales made by the logged-in agent
    sales = Sale.objects.filter(agent=request.user).order_by('-sale_date')

    context = {
        'message': 'Sale completed successfully!',
        'sales': sales
    }

    return render(request, 'base/sale_success.html', context)

# Role-Based Redirect View
@login_required
def role_based_redirect(request):
    try:
        employee = Employee.objects.get(user=request.user)
        if employee.role == 'Admin':
            return redirect('admin_panel')
        elif employee.role == 'Agent':
            return redirect('agent_workpage')
        else:
            return render(request, 'base/main.html', {'message': 'No valid role assigned.'})
    except Employee.DoesNotExist:
        return render(request, 'base/main.html', {'message': 'Employee profile not found.'})



@login_required
def agent_workpage(request):
    try:
        # Get the logged-in agent
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return render(request, 'base/error.html', {'message': 'Employee profile not found.'})

    # Fetch tasks assigned to the agent
    tasks = Task.objects.filter(assigned_to=employee)

    # Fetch available properties
    properties = PropertyListing.objects.filter(status='Available')

    # Fetch performance metrics for the agent
    performance_metrics = PerformanceMetrics.objects.filter(employee=employee).first()

    # Fetch productivity data for the agent
    productivity_data = ProductivityTracker.objects.filter(employee=employee)

    # Fetch sales made by the agent
    sales = Sale.objects.filter(agent=request.user)

    context = {
        'tasks': tasks,
        'properties': properties,
        'performance_metrics': performance_metrics,
        'productivity_data': productivity_data,
        'sales': sales,
    }

    return render(request, 'base/agent_workpage.html', context)


@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user.employee)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [choice[0] for choice in Task.STATUS_CHOICES]:  # Validate status
            task.status = new_status
            task.save()
            return redirect('agent_workpage')
    
    return render(request, 'base/update_task_status.html', {'task': task})

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user.employee)
    return render(request, 'base/task_detail.html', {'task': task})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_panel(request):
    # Employee Performance Metrics
    employee_performance = PerformanceMetrics.objects.select_related('employee__user').all()

    # Property Status
    total_properties = PropertyListing.objects.count()
    available_properties = PropertyListing.objects.filter(status='Available').count()
    sold_properties = PropertyListing.objects.filter(status='Sold').count()
    property_status = {
        'total_properties': total_properties,
        'available_properties': available_properties,
        'sold_properties': sold_properties,
    }

    # Financial Overview
    total_revenue = Revenue.objects.aggregate(total_revenue=Sum('total_revenue'))['total_revenue'] or 0
    total_expenses = Revenue.objects.aggregate(total_expenses=Sum('total_expenses'))['total_expenses'] or 0
    net_profit = total_revenue - total_expenses
    financial_overview = {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
    }

    # Recent Activities
    recent_sales = Sale.objects.select_related('property').order_by('-sale_date')[:5]
    recent_tasks = Task.objects.select_related('assigned_to__user').order_by('-due_date')[:5]

    context = {
        'employee_performance': employee_performance,
        'property_status': property_status,
        'financial_overview': financial_overview,
        'recent_sales': recent_sales,
        'recent_tasks': recent_tasks,
    }

    return render(request, 'base/admin_panel.html', context)



