from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(PropertyListing)
admin.site.register(Employee)
admin.site.register(Task)
admin.site.register(Revenue)
admin.site.register(PerformanceMetrics)
admin.site.register(ProductivityTracker)
admin.site.register(PredefinedTask)
admin.site.register(Sale)


