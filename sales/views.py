from django.shortcuts import render, redirect, get_object_or_404
from .models import MoneyReceived, ItemSold
from .forms import MoneyReceivedForm, ItemSoldForm
from django.db.models import Sum
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
import datetime

import json
from django.core.serializers.json import DjangoJSONEncoder

def index(request):
    # Summary Cards
    total_received = MoneyReceived.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_sold = ItemSold.objects.aggregate(Sum('total'))['total__sum'] or 0
    balance = total_sold - total_received
    
    # Chart Data - Aggregate by Date
    daily_received = MoneyReceived.objects.values('date').annotate(total=Sum('amount')).order_by('date')
    daily_sold = ItemSold.objects.values('date').annotate(total=Sum('total')).order_by('date')
    
    # Process into a dictionary {date: {received: 0, sold: 0}} to align dates
    data_map = {}
    
    for entry in daily_received:
        d = entry['date'].strftime('%Y-%m-%d')
        if d not in data_map: data_map[d] = {'received': 0, 'sold': 0}
        data_map[d]['received'] = float(entry['total'])

    for entry in daily_sold:
        d = entry['date'].strftime('%Y-%m-%d')
        if d not in data_map: data_map[d] = {'received': 0, 'sold': 0}
        data_map[d]['sold'] = float(entry['total'])
    
    # Sort by date
    sorted_dates = sorted(data_map.keys())
    
    chart_labels = sorted_dates
    chart_received = [data_map[d]['received'] for d in sorted_dates]
    chart_sold = [data_map[d]['sold'] for d in sorted_dates]

    context = {
        'total_received': total_received,
        'total_sold': total_sold,
        'balance': balance,
        'chart_labels': json.dumps(chart_labels, cls=DjangoJSONEncoder),
        'chart_received': json.dumps(chart_received, cls=DjangoJSONEncoder),
        'chart_sold': json.dumps(chart_sold, cls=DjangoJSONEncoder),
    }
    return render(request, 'sales/index.html', context)

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
    balance = total_sales - total_money
    
    html_string = render_to_string('sales/pdf_report.html', {
        'money_entries': money_entries,
        'item_entries': item_entries,
        'total_money': total_money,
        'total_sales': total_sales,
        'balance': balance,
        'date': datetime.date.today()
    })
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="sales_report.pdf"'
    
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html_string + '</pre>')
    return response
