from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from decimal import Decimal
from .models import Transaction
from .forms import TransactionForm
from django.http import HttpResponse
import xlwt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
def index(request):
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})



@login_required
def dashboard(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user).order_by('-timestamp')

    
    # Calculate total income and total expense
    balance, total_income, total_expenses = Transaction.calculate_balance(user)

    
    context = {
        'user': user,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'transactions': transactions,

    }
    return render(request, 'dashboard.html', context)
@login_required
def add_transaction(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        transaction_type = request.POST.get('transaction_type')
        description = request.POST.get('description')
        
        if transaction_type in ['income', 'expense']:
            amount = float(amount)
            if transaction_type == 'expense':
                amount = -amount  # Convert expense to negative value
            
            # Save transaction
            Transaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type=transaction_type,
                description=description
            )
            
            return redirect('dashboard')
    
    return render(request, 'add_transaction.html')



@login_required
def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            updated_transaction = form.save(commit=False)
            # Adjust amount based on transaction type
            if updated_transaction.transaction_type == 'income':
                updated_transaction.amount = abs(updated_transaction.amount)
            elif updated_transaction.transaction_type == 'expense':
                updated_transaction.amount = -abs(updated_transaction.amount)
            
            updated_transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm(instance=transaction)
    
    return render(request, 'edit_transaction.html', {'form': form, 'transaction': transaction})
@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        transaction.delete()
        return redirect('dashboard')
    
    context = {
        'transaction': transaction,
    }
    return render(request, 'delete_transaction.html', context)
@login_required
def reset_transactions(request):
    user = request.user
    
    # Delete all transactions for the logged-in user
    Transaction.objects.filter(user=user).delete()
    
    # Redirect back to the dashboard or any other page as needed
    return redirect('dashboard')


@login_required
def download_excel_report(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="report.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Transactions')

    # Write headers
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Timestamp', 'Description', 'Amount', 'Type']
    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)

    # Write data
    user = request.user  # Get the logged-in user
    transactions = Transaction.objects.filter(user=user)  # Query transactions related to the user

    font_style = xlwt.XFStyle()

    for transaction in transactions:
        row_num += 1
        ws.write(row_num, 0, transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S'), font_style)
        ws.write(row_num, 1, transaction.description, font_style)
        ws.write(row_num, 2, str(transaction.amount), font_style)
        ws.write(row_num, 3, transaction.get_transaction_type_display(), font_style)

    wb.save(response)
    return response

def download_pdf_report(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    # Create a PDF canvas
    p = canvas.Canvas(response, pagesize=letter)
    p.setTitle("Financial Report")

    # Add title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Financial Report")
    p.setFont("Helvetica", 12)
    p.drawString(100, 780, f"Generated on: {datetime.now()}")

    # Add transactions table
    transactions = Transaction.objects.filter(user=request.user)
    table_y_position = 750
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, table_y_position, "Transactions:")
    table_y_position -= 20
    p.setFont("Helvetica", 10)
    p.drawString(100, table_y_position, "Date")
    p.drawString(200, table_y_position, "Description")
    p.drawString(350, table_y_position, "Amount")
    p.drawString(450, table_y_position, "Type")
    table_y_position -= 20

    for transaction in transactions:
        formatted_date = transaction.timestamp.strftime("%d %b")  # Format to day and abbreviated month (e.g., 01 Jan)
        p.drawString(100, table_y_position, formatted_date)
        p.drawString(200, table_y_position, transaction.description)
        p.drawString(350, table_y_position, "${:.2f}".format(transaction.amount))
        p.drawString(450, table_y_position, transaction.get_transaction_type_display())
        table_y_position -= 15

    # Save the PDF
    p.showPage()
    p.save()

    return response