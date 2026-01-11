from django.shortcuts import render, redirect, get_object_or_404
from .models import MoneyReceived, ItemSold
from .forms import MoneyReceivedForm, ItemSoldForm
from django.db.models import Sum
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
import datetime

def index(request):
    return render(request, 'sales/index.html')

def money_received(request):
    if request.method == 'POST':
        form = MoneyReceivedForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('money_received')
    else:
        form = MoneyReceivedForm(initial={'date': datetime.date.today()})
    
    entries = MoneyReceived.objects.all().order_by('-date')
    total_received = entries.aggregate(Sum('amount'))['amount__sum'] or 0
    
    return render(request, 'sales/money_received.html', {
        'form': form,
        'entries': entries,
        'total_received': total_received
    })

def item_sold(request):
    if request.method == 'POST':
        form = ItemSoldForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_sold')
    else:
        form = ItemSoldForm(initial={'date': datetime.date.today()})
    
    items = ItemSold.objects.all().order_by('-date')
    total_sold = items.aggregate(Sum('total'))['total__sum'] or 0
    
    return render(request, 'sales/item_sold.html', {
        'form': form,
        'items': items,
        'total_sold': total_sold
    })

def delete_money(request, pk):
    entry = get_object_or_404(MoneyReceived, pk=pk)
    entry.delete()
    return redirect('money_received')

def delete_item(request, pk):
    item = get_object_or_404(ItemSold, pk=pk)
    item.delete()
    return redirect('item_sold')

def pdf_report(request):
    money_entries = MoneyReceived.objects.all().order_by('date')
    item_entries = ItemSold.objects.all().order_by('date')
    
    total_money = money_entries.aggregate(Sum('amount'))['amount__sum'] or 0
    total_sales = item_entries.aggregate(Sum('total'))['total__sum'] or 0
    
    html_string = render_to_string('sales/pdf_report.html', {
        'money_entries': money_entries,
        'item_entries': item_entries,
        'total_money': total_money,
        'total_sales': total_sales,
        'date': datetime.date.today()
    })
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="sales_report.pdf"'
    
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html_string + '</pre>')
    return response
