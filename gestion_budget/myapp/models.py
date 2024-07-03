from decimal import Decimal  # Add this import at the beginning of your models.py file
from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=[('income', 'Income'), ('expense', 'Expense')])
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.transaction_type})"

    @classmethod
    def calculate_balance(cls, user):
        total_income = cls.objects.filter(user=user, transaction_type='income').aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0.00')
        total_expenses = cls.objects.filter(user=user, transaction_type='expense').aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0.00')
        balance = total_income - abs(total_expenses)
        return balance, total_income, total_expenses
