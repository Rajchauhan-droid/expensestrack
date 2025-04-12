from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    is_recurring = models.BooleanField(default=False)
    tags = models.CharField(max_length=255, blank=True)  # Add a tags field


    def __str__(self):
        return f"{self.title} - {self.amount}"
    # Add a method to return tags as a list (if tags are comma-separated)
    def get_tags(self):
        return self.tags.split(',') if self.tags else []

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username}'s Budget - {self.month.strftime('%B %Y')}"



class FinanceGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # Name of the goal (e.g., "Save for vacation")
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)  # Target amount for the goal
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Amount saved so far
    start_date = models.DateField()  # When the user started saving for this goal
    end_date = models.DateField()  # Deadline to reach the goal
    description = models.TextField(blank=True, null=True)  # Optional description for the goal

    def progress_percentage(self):
        """Calculate the percentage of goal completed."""
        if self.target_amount > 0:
            return (self.current_amount / self.target_amount) * 100
        return 0

    def __str__(self):
        return f"{self.name} - {self.progress_percentage():.2f}%"


