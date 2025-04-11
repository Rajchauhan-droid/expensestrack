from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Expense, Category
from datetime import datetime
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from .forms import CategoryForm, ExpenseForm 


def index(request):
    return render(request, 'index.html')

from django.db.models import Sum

from django.db.models import Sum


@login_required
def dashboard_view(request):
    expenses = Expense.objects.filter(user=request.user)
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Expense sum per category
    category_expenses = expenses.values('category__name').annotate(total=Sum('amount'))

    # Prepare data for Chart.js
    chart_labels = [item['category__name'] for item in category_expenses]
    chart_data = [float(item['total']) for item in category_expenses]

    context = {
        'total_expense': total_expense,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
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
