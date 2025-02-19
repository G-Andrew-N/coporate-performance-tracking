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
from django.core.paginator import Paginator
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F
from django.utils.timezone import now
from decimal import Decimal, InvalidOperation
from datetime import datetime
from .models import PropertyListing, Sale, Employee, AgentProfit


from django.shortcuts import render
from django.db.models import Avg, Sum, Count
from .models import Employee, ProductivityTracker, Revenue, PerformanceMetrics

import matplotlib.pyplot as plt
import io
import urllib, base64

import matplotlib.pyplot as plt
from io import BytesIO
import base64

from django.shortcuts import render
from django.db.models import Sum
from .models import Sale, PropertyListing, PerformanceMetrics

import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from django.db.models import Sum  # ✅ Import Sum for aggregation
from decimal import Decimal


def landing(request):
    return render(request, "base/landing_page.html")

def generate_chart(data, title):
    """Helper function to create base64-encoded chart images."""
    plt.figure(figsize=(5, 3))
    plt.plot(data, marker='o', linestyle='-')
    plt.title(title)
    plt.grid(True)
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    
    return f"data:image/png;base64,{image_base64}"


from django.shortcuts import render
from django.db.models import Sum
from .models import Sale, PropertyListing, PerformanceMetrics

def home(request):
    # Financial Summary
    total_revenue = Sale.objects.aggregate(total=Sum("sale_price"))["total"] or 0
    net_profit = total_revenue * Decimal("0.85")  # Example: Assuming 15% expenses

    # Property Metrics
    properties_sold = PropertyListing.objects.filter(status="Sold").count()
    
    # Pending verifications removed since PropertyListing has no `ownership_verified` field

    # Agent Performance
    agent_performance = PerformanceMetrics.objects.order_by("-aggregate_points")[:5]

    # Sales Volume Trends (last 6 months)
    sales_data = [Sale.objects.filter(sale_date__month=i).count() for i in range(7, 13)]
    sales_chart = generate_chart(sales_data, "Sales Volume Trends")

    # Productivity Trends
    productivity_data = [agent.tasks_completed for agent in agent_performance]
    productivity_chart = generate_chart(productivity_data, "Productivity Trends")

    # Revenue Trends
    revenue_data = [Sale.objects.filter(sale_date__month=i).aggregate(total=Sum("sale_price"))["total"] or 0 for i in range(7, 13)]
    revenue_chart = generate_chart(revenue_data, "Revenue Trends")

    context = {
        "total_revenue": total_revenue,
        "net_profit": net_profit,
        "properties_sold": properties_sold,
        "agent_performance": agent_performance,
        "sales_chart": sales_chart,
        "productivity_chart": productivity_chart,
        "revenue_chart": revenue_chart,
    }

    return render(request, "base/home.html", context)




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


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Employee, PerformanceMetrics, Task, Revenue, Sale  # Fixed Sale model reference

@login_required
def user_profile_view(request):
    employee = get_object_or_404(Employee, user=request.user)

    # Get performance metrics
    performance_metrics = PerformanceMetrics.objects.filter(employee=employee).first()

    # Fetch recent sales handled by the employee
    sales = Sale.objects.filter(agent=employee).order_by('-sale_date')[:10]

    # Task status counts for chart display
    task_status_counts = [
        Task.objects.filter(assigned_to=employee, status=status).count()
        for status in ['Pending', 'Completed', 'Overdue']
    ]

    # Revenue data (existing)
    revenue_entries = Revenue.objects.all().order_by("year", "month")
    revenue_data = {
        'labels': [f"{entry.year}-{entry.month:02d}" for entry in revenue_entries],
        'net_profits': [entry.net_profit for entry in revenue_entries],
    }

    # 🚀 Agent profit trends (new)
    agent_profits = AgentProfit.objects.filter(agent=employee).order_by("recorded_at")
    profit_data = {
        'labels': [profit.recorded_at.strftime('%Y-%m-%d') for profit in agent_profits],
        'profit_values': [float(profit.profit_amount) for profit in agent_profits],
    }

    context = {
        'user': request.user,
        'employee': employee,
        'performance_metrics': performance_metrics or {},
        'sales': sales,
        'task_status_counts': task_status_counts,
        'revenue_data': revenue_data,
        'profit_data': profit_data,  # Add this
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
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        task_document = request.FILES.get('task_document')

        if new_status == "Done" and not task_document:
            return JsonResponse({'error': 'Document submission is required to mark the task as done'}, status=400)

        if new_status:
            task.status = new_status
            if new_status == "Done" and task_document:
                task.document = task_document  # Assuming Task model has a `document` field
                task.save()

                # Increment tasks_completed in PerformanceMetrics
                performance_metrics, created = PerformanceMetrics.objects.get_or_create(employee=request.user)
                performance_metrics.tasks_completed += 1
                performance_metrics.save()
            else:
                task.save()

        return redirect('task_performance')

    return JsonResponse({'error': 'Invalid request method'}, status=400)


# Make Sale View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime
 # Ensure correct imports



from django.db.models import F
from django.utils.timezone import now
from .models import Sale, AgentProfit  # Import new model

@login_required
def make_sale(request, property_id):
    property_listing = get_object_or_404(PropertyListing, pk=property_id)
    
    # Get the Employee instance linked to the logged-in user
    try:
        agent = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, "You are not registered as an employee.")
        return redirect("some_error_page")
    
    if request.method == 'POST':
        try:
            # Extract form data with defaults
            form_data = {
                'buyer_name': request.POST.get('buyer_name', 'Unknown Buyer'),
                'buyer_id': request.POST.get('buyer_id', 'Unknown ID'),
                'buyer_email': request.POST.get('buyer_email', 'notprovided@example.com'),
                'buyer_tel': request.POST.get('buyer_tel', 'Not Provided'),
                'buyer_address': request.POST.get('buyer_address', 'Not Provided'),
                'payment_method': request.POST.get('payment_method', 'Cash'),
                'seller_name': request.POST.get('seller_name', 'Unknown Seller'),
                'seller_tel': request.POST.get('seller_tel', 'Not Provided'),
                'seller_email': request.POST.get('seller_email', 'notprovided@example.com'),
                'seller_address': request.POST.get('seller_address', 'Not Provided'),
                'ownership_verification': request.POST.get('ownership_verification', 'Pending Verification'),
            }
            
            # Convert date fields
            try:
                sale_date = request.POST.get('sale_date')
                closing_date = request.POST.get('closing_date')
                form_data['sale_date'] = datetime.strptime(sale_date, "%Y-%m-%d").date() if sale_date else now().date()
                form_data['closing_date'] = datetime.strptime(closing_date, "%Y-%m-%d").date() if closing_date else None
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return render(request, 'base/make_sale.html', {'property': property_listing})

            # Convert numeric fields
            try:
                form_data.update({
                    'sale_price': Decimal(request.POST.get('sale_price', '0.00')),
                    'title_insurance': Decimal(request.POST.get('title_insurance', '0.00')),
                    'legal_fees': Decimal(request.POST.get('legal_fees', '0.00')),
                    'deposit': Decimal(request.POST.get('deposit', '0.00')),
                })
            except (ValueError, InvalidOperation):
                messages.error(request, "Invalid number format. Ensure all amounts are valid numbers.")
                return render(request, 'base/make_sale.html', {'property': property_listing})

            # Create the Sale record
            sale = Sale.objects.create(
                property_listing=property_listing,
                agent=agent,
                **form_data
            )
            
            # Calculate profit
            profit_amount = form_data['sale_price'] - (form_data['legal_fees'] + form_data['title_insurance'])

            # Store the profit in the AgentProfit model
            AgentProfit.objects.create(
                agent=agent,
                sale=sale,
                profit_amount=profit_amount
            )
            
            # Update the property's status
            property_listing.status = "Sold"
            property_listing.save()

            messages.success(request, f"Sale successful! Profit: {profit_amount:.2f} USD.")
            return render(request, 'base/sale_confirmation.html', {'message': f"Sale successful! Profit: {profit_amount:.2f} USD."})
        
        except PropertyListing.DoesNotExist:
            messages.error(request, "Property not found.")
        except Employee.DoesNotExist:
            messages.error(request, "Agent not found.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            
    return render(request, 'base/make_sale.html', {'property': property_listing})


@login_required
def sale_success(request):
    # Fetch all sales made by the logged-in agent
    sales = Sale.objects.filter(agent=request.user).order_by('-sale_date')

    context = {
        'message': 'Sale completed successfully!',
        'sales': sales
    }

    return render(request, 'base/sale_confirmation.html', context)

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

    # Fetch available properties and apply pagination (e.g., 10 per page)
    property_list = PropertyListing.objects.filter(status='Available')
    paginator = Paginator(property_list, 10)  # Show 10 properties per page
    page_number = request.GET.get('page')
    properties = paginator.get_page(page_number)

    # Fetch performance metrics for the agent
    performance_metrics = PerformanceMetrics.objects.filter(employee=employee).first()

    # Fetch productivity data for the agent
    productivity_data = ProductivityTracker.objects.filter(employee=employee)

    # Fetch sales made by the agent (✅ FIXED THIS LINE)
    sales = Sale.objects.filter(agent=employee)

    context = {
        'tasks': tasks,
        'properties': properties,  # Now paginated
        'performance_metrics': performance_metrics,
        'productivity_data': productivity_data,
        'sales': sales,
    }

    return render(request, 'base/agent_workpage.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Task, PerformanceMetrics

@login_required
def update_task_status(request, task_id):
    # Fetch the task
    task = get_object_or_404(Task, id=task_id)

    # Ensure request.user is the actual person assigned
    if task.assigned_to and hasattr(task.assigned_to, 'user') and task.assigned_to.user != request.user:
        return JsonResponse({'error': 'You are not assigned to this task'}, status=403)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        task_document = request.FILES.get('task_document')

        if new_status == "Done" and not task_document:
            return JsonResponse({'error': 'Document submission is required to mark the task as done'}, status=400)

        # Update task status and document
        if new_status:
            task.status = new_status
            if new_status == "Done" and task_document:
                task.document = task_document
                task.save()

                # Ensure PerformanceMetrics updates properly
                performance_metrics, created = PerformanceMetrics.objects.get_or_create(employee=task.assigned_to)
                performance_metrics.tasks_completed += 1
                performance_metrics.save()
            else:
                task.save()

        return redirect('task_performance')

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
    recent_sales = Sale.objects.select_related('property_listing').order_by('-sale_date')[:5]
    recent_tasks = Task.objects.select_related('assigned_to__user').order_by('-due_date')[:5]

    context = {
        'employee_performance': employee_performance,
        'property_status': property_status,
        'financial_overview': financial_overview,
        'recent_sales': recent_sales,
        'recent_tasks': recent_tasks,
    }

    return render(request, 'base/admin_panel.html', context)




