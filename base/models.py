from django.db import models
from django.contrib.auth.models import User
import uuid

from django.db.models.signals import post_save
from django.dispatch import receiver
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver


class PropertyListing(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Sold', 'Sold'),
        ('Under Contract', 'Under Contract'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    propertyType = models.CharField(max_length=30)
    location = models.CharField(max_length=30)
    address = models.CharField(max_length=100)
    floors = models.PositiveIntegerField()
    coveredArea = models.CharField(max_length=30)
    electricityStatus = models.CharField(max_length=30)
    bathroomCount = models.PositiveIntegerField()
    bedroomCount = models.PositiveIntegerField()
    bookingAmount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    image = models.ImageField(upload_to='property_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.propertyType} - {self.location}"


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default='Agent')  # e.g., Agent, Manager, Admin
    join_date = models.DateField()
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"


class Revenue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()  # 1 (January) to 12 (December)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2)
    net_profit = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"Revenue for {self.year}-{self.month:02d}: {self.net_profit}"


class PerformanceMetrics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    tasks_completed = models.PositiveIntegerField(default=0)
    sales_closed = models.PositiveIntegerField(default=0)
    aggregate_points = models.PositiveIntegerField(default=0)  # New field

    def __str__(self):
        return f"Performance Metrics (Employee: {self.employee})"

    def update_aggregate_points(self):
        """Updates the aggregate points based on sales and tasks completed."""
        self.aggregate_points = (self.sales_closed * 10) + (self.tasks_completed * 5)
        self.save()


# ✅ Signal to create PerformanceMetrics when a new Employee is added
@receiver(post_save, sender=Employee)
def create_performance_metrics(sender, instance, created, **kwargs):
    if created:
        PerformanceMetrics.objects.create(employee=instance)


class ProductivityTracker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    tasks_completed = models.PositiveIntegerField()

    def __str__(self):
        return f"Productivity for {self.employee} on {self.date}"


class PredefinedTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])

    def __str__(self):
        return self.title




@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        task_document = request.FILES.get('task_document')

        if new_status == "Completed" and not task_document:
            return JsonResponse({'error': 'Document submission is required to mark the task as completed'}, status=400)

        if new_status:
            task.status = new_status
            if new_status == "Completed" and task_document:
                task.document = task_document
                task.save()
                
                # Update performance metrics
                performance_metrics, _ = PerformanceMetrics.objects.get_or_create(employee=request.user)
                performance_metrics.tasks_completed += 1
                performance_metrics.save()
            else:
                task.save()

        return redirect('task_dashboard')

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def task_dashboard(request):
    pending_tasks = Task.objects.filter(assigned_to=request.user, status='Pending')
    overdue_tasks = Task.objects.filter(assigned_to=request.user, status='Overdue')
    completed_tasks = Task.objects.filter(assigned_to=request.user, status='Completed')
    return render(request, 'tasks/dashboard.html', {
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'completed_tasks': completed_tasks
    })

@login_required
def clear_completed_tasks(request):
    if request.method == 'POST':
        Task.objects.filter(assigned_to=request.user, status='Completed').delete()
        return redirect('task_dashboard')
    return JsonResponse({'error': 'Invalid request method'}, status=400)


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    predefined_task = models.ForeignKey('PredefinedTask', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=20, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], blank=True)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Overdue', 'Overdue')],
    )
    document = models.FileField(upload_to='task_documents/', null=True, blank=True)

    def __str__(self):
        return f"{self.predefined_task.title} ({self.status})"

    def save(self, *args, **kwargs):
        """Ensure priority is updated from predefined task but preserve custom description."""
        if self.predefined_task:
            self.priority = self.predefined_task.priority
            # Only set description from predefined task if no custom description is provided
            if not self.description:
                self.description = self.predefined_task.description
        super(Task, self).save(*args, **kwargs)



# ✅ Signal to update task points
@receiver(post_save, sender=Task)
def update_task_points(sender, instance, **kwargs):
    if instance.status == "Completed" and instance.assigned_to:
        performance_metrics, _ = PerformanceMetrics.objects.get_or_create(employee=instance.assigned_to)
        performance_metrics.tasks_completed += 1
        performance_metrics.update_aggregate_points()
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver

# ✅ Signal to update task points
@receiver(post_save, sender=Task)
def update_task_points(sender, instance, **kwargs):
    if instance.status == "Completed" and instance.assigned_to:
        performance_metrics, _ = PerformanceMetrics.objects.get_or_create(employee=instance.assigned_to)
        performance_metrics.tasks_completed += 1
        performance_metrics.update_aggregate_points()

# ✅ Signal to update productivity tracker
@receiver(post_save, sender=Task)
def update_task_productivity(sender, instance, **kwargs):
    if instance.status == "Completed" and instance.assigned_to:
        today = now().date()
        employee = instance.assigned_to

        # Update the productivity tracker
        tracker, _ = ProductivityTracker.objects.get_or_create(
            employee=employee, date=today,
            defaults={'hours_worked': 0, 'tasks_completed': 0}
        )
        tracker.tasks_completed += 1
        tracker.save()


class Sale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property_listing = models.ForeignKey('PropertyListing', on_delete=models.CASCADE)
    agent = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True)
    buyer_name = models.CharField(max_length=100, default="Unknown Buyer")
    buyer_id = models.CharField(max_length=100, default="Unknown ID")
    buyer_email = models.EmailField(null=True, blank=True, default="notprovided@example.com")
    buyer_tel = models.CharField(max_length=20, default="Not Provided")
    buyer_address = models.TextField(default="Not Provided")
    payment_method = models.CharField(max_length=20, default="Cash")
    seller_name = models.CharField(max_length=100, default="Unknown Seller")
    seller_tel = models.CharField(max_length=20, default="Not Provided")
    seller_email = models.EmailField(null=True, blank=True, default="notprovided@example.com")
    seller_address = models.TextField(default="Not Provided")
    ownership_verification = models.CharField(max_length=100, default="Pending Verification")
    sale_date = models.DateField(null=True, blank=True)
    sale_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    title_insurance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    legal_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    closing_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Sale of {self.property_listing} to {self.buyer_name}"


# ✅ Signal to update sales points
@receiver(post_save, sender=Sale)
def update_sales_points(sender, instance, created, **kwargs):
    if created and instance.agent:
        performance_metrics, _ = PerformanceMetrics.objects.get_or_create(employee=instance.agent)
        performance_metrics.sales_closed += 1
        performance_metrics.update_aggregate_points()





class AgentProfit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey('Employee', on_delete=models.CASCADE)
    sale = models.ForeignKey('Sale', on_delete=models.CASCADE)
    profit_amount = models.DecimalField(max_digits=15, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profit: {self.profit_amount} (Agent: {self.agent})"
