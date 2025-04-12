from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Expense, Category
from datetime import datetime
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from .forms import CategoryForm, ExpenseForm 

import requests 
from django.conf import settings


def index(request):
    return render(request, 'index.html')

from django.db.models import Sum
from django.db.models.functions import TruncMonth

from django.db.models import Q
from django.shortcuts import render
from .models import Expense
from .forms import ExpenseSearchForm

@login_required
def dashboard_view(request):
    # Search form handling
    search_form = ExpenseSearchForm(request.GET)

    # Get expenses filtered by search query, tags, or date range
    expenses = Expense.objects.filter(user=request.user)

    # If search query exists, filter by description or category name
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query', '')
        if query:
            expenses = expenses.filter(
                Q(description__icontains=query) | Q(category__name__icontains=query)
            )

        # Filter by tags
        tags = search_form.cleaned_data.get('tags', '')
        if tags:
            expenses = expenses.filter(tags__icontains=tags)

        # Filter by date range
        start_date = search_form.cleaned_data.get('start_date', None)
        end_date = search_form.cleaned_data.get('end_date', None)
        if start_date:
            expenses = expenses.filter(date__gte=start_date)
        if end_date:
            expenses = expenses.filter(date__lte=end_date)

    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Expense sum per category
    category_expenses = expenses.values('category__name').annotate(total=Sum('amount'))

    # Prepare data for Chart.js
    chart_labels = [item['category__name'] for item in category_expenses]
    chart_data = [float(item['total']) for item in category_expenses]

    # Expense trend over time (e.g., monthly)
    trend_expenses = expenses.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')

    # Prepare data for Line Chart (Monthly expense trend)
    trend_labels = [expense['month'].strftime('%b %Y') for expense in trend_expenses]  # Format month as 'Jan 2025'
    trend_data = [float(expense['total']) for expense in trend_expenses]

    context = {
        'total_expense': total_expense,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'trend_labels': trend_labels,
        'trend_data': trend_data,
        'search_form': search_form,
    }

    return render(request, 'dashboard.html', context)






def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('expenses:dashboard')
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('expenses:login')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('expenses:login')
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

def category_view(request):
    return render(request,'category_list.html')


@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'category/category_list.html', {'categories': categories})

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)  # Don't save to the database yet
            category.user = request.user  # Set the current user
            category.save()  # Now save the category
            return redirect('expenses:category_list')  # Redirect to category list after saving
    else:
        form = CategoryForm()

    return render(request, 'category/add_category.html', {'form': form})

@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('expenses:category_list')  # Redirect to category list page
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'category/edit_category.html', {'form': form, 'category': category})

@login_required
def delete_category(request, pk):
    category = Category.objects.get(pk=pk, user=request.user)
    category.delete()
    messages.success(request, "Category deleted!")
    return redirect('expenses:category_list')


@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user)
    return render(request, 'expense/expense_list.html', {'expenses': expenses})

@login_required
def expense_create(request):
    categories = Category.objects.filter(user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user  # Associate the current user with the expense
            expense.save()
            messages.success(request, "Expense added successfully!")
            return redirect('expenses:expense_list')
    else:
        form = ExpenseForm()

    return render(request, 'expense/expense_form.html', {'form': form, 'categories': categories})



@login_required
def expense_update(request, pk):
    # Fetch the expense by pk and ensure it's the current user's
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    categories = Category.objects.filter(user=request.user)
    
    if request.method == 'POST':
        # Create the form with POST data and the current expense instance
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()  # Save the updated expense to the database
            messages.success(request, "Expense updated successfully!")
            return redirect('expenses:expense_list')
    else:
        # Initialize the form with the current expense data
        form = ExpenseForm(instance=expense)

    return render(request, 'expense/expense_form.html', {
        'form': form,
        'categories': categories,
        'expense': expense
    })

@login_required
def expense_delete(request, pk):
    expense = Expense.objects.get(pk=pk, user=request.user)
    expense.delete()
    messages.success(request, "Expense deleted!")
    return redirect('expenses:expense_list')



import requests
from django.shortcuts import render
from django.conf import settings

# Add this to your settings.py (for API key storage)
# CURRENCY_API_KEY = 'your_api_key_here'

def currency_converter(request):
    # Default currency values (for example)
    from_currency = 'USD'
    to_currency = 'EUR'
    amount = 1

    # If the form is submitted, use the data
    if request.method == 'POST':
        from_currency = request.POST.get('from_currency')
        to_currency = request.POST.get('to_currency')
        amount = float(request.POST.get('amount'))

    # Construct the API URL
    api_url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"

    # Make the API request
    response = requests.get(api_url)
    data = response.json()

    # Check if request is successful
    if response.status_code == 200:
        # Get the exchange rate for the selected currency
        exchange_rate = data['rates'].get(to_currency)
        if exchange_rate:
            converted_amount = amount * exchange_rate
        else:
            converted_amount = None
    else:
        converted_amount = None

    # Pass data to the template
    context = {
        'from_currency': from_currency,
        'to_currency': to_currency,
        'amount': amount,
        'converted_amount': converted_amount,
        'rates': data['rates']
    }

    return render(request, 'currency_converter.html', context)



from .models import FinanceGoal
from .forms import FinanceGoalForm

# View to add or edit goals
def view_goals(request):
    goals = FinanceGoal.objects.all()
    return render(request, 'finance/view_goals.html', {'goals': goals})

def add_or_edit_goal(request, goal_id=None):
    if goal_id:
        goal = get_object_or_404(FinanceGoal, id=goal_id, user=request.user)
    else:
        goal = None

    if request.method == 'POST':
        form = FinanceGoalForm(request.POST, instance=goal)
        if form.is_valid():
            goal = form.save(commit=False)  # Don't save to DB yet
            goal.user = request.user        # ✅ assign user here!
            goal.save()
            return redirect('expenses:view_goals')
    else:
        form = FinanceGoalForm(instance=goal)

    return render(request, 'finance/add_or_edit_goal.html', {'form': form})



def delete_goal(request, goal_id):
    goal = get_object_or_404(FinanceGoal, id=goal_id)
    goal.delete()
    return redirect('expenses:view_goals')
