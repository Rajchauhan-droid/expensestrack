from django import forms
from .models import Category
from .models import Expense


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']  # Add more fields if necessary

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter category name'})


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'description']
        date = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker form-control'}))


    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError('Amount must be positive.')
        return amount