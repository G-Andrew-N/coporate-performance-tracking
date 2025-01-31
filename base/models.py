from django.db import models
from django.contrib.auth.models import User
import uuid
from uuid import uuid4




    
from django.db import models
import uuid

class PropertyListing(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Sold', 'Sold'),
        ('Under Contract', 'Under Contract'),
    ]

    # Explicit UUIDField as the primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    propertyType = models.CharField(max_length=30)
    location = models.CharField(max_length=30)
    address = models.CharField(max_length=100)
    floors = models.PositiveIntegerField()
    coveredArea = models.CharField(max_length=30)
    electricityStatus = models.CharField(max_length=30)
    bathroomCount = models.PositiveIntegerField()
    bedroomCount = models.PositiveIntegerField()
    bookingAmount = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    image = models.ImageField(upload_to='property_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.propertyType} - {self.location}"
    
class Employee(models.Model):
 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)  # e.g., Agent, Manager, Admin
    join_date = models.DateField()
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"
    
    
    
class SalesRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(PropertyListing, on_delete=models.CASCADE)
    agent = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    sale_date = models.DateField()
    sale_price = models.DecimalField(max_digits=15, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Sale of {self.property} by {self.agent}"

class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Overdue', 'Overdue')])

    def __str__(self):
        return f"{self.title} ({self.status})"

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
    property = models.ForeignKey(PropertyListing, on_delete=models.CASCADE, null=True, blank=True)
    tasks_completed = models.PositiveIntegerField(default=0)
    sales_closed = models.PositiveIntegerField(default=0)
    customer_satisfaction = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Percentage

    def __str__(self):
        return f"Performance Metrics (Employee: {self.employee}, Property: {self.property})"

class ProductivityTracker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    tasks_completed = models.PositiveIntegerField()

    def __str__(self):
        return f"Productivity for {self.employee} on {self.date}"
    
class Sale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey('PropertyListing', on_delete=models.CASCADE)
    sale_price = models.DecimalField(max_digits=15, decimal_places=2)
    profit = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)  # Add default value
    transaction_status = models.CharField(
        max_length=20,
        choices=[('Successful', 'Successful'), ('Unsuccessful', 'Unsuccessful')],
        default='Successful'
    )
    sale_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale of {self.property} by {self.agent} (Status: {self.transaction_status})"
    
    
class PredefinedTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])

    def __str__(self):
        return self.title
    
class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    predefined_task = models.ForeignKey(PredefinedTask, on_delete=models.CASCADE, null=True, blank=True)
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Overdue', 'Overdue')])

    def __str__(self):
        return f"{self.title} ({self.status})"