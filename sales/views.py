from django.shortcuts import render, redirect, get_object_or_404
from .models import MoneyReceived, ItemSold
from .forms import MoneyReceivedForm, ItemSoldForm, FilterForm
from django.db.models import Sum
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
import datetime

import json
from django.core.serializers.json import DjangoJSONEncoder

def index(request):
    # Filter Form
    filter_form = FilterForm(request.GET)
    
    # Base QuerySets (for charts and summary)
    money_qs = MoneyReceived.objects.all()
    sold_qs = ItemSold.objects.all()
    
    filtered_items = None
    filtered_total = 0
    filtered_balance = 0
    
    if filter_form.is_valid():
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        min_amount = filter_form.cleaned_data.get('min_amount')
        max_amount = filter_form.cleaned_data.get('max_amount')
        due_15_days = filter_form.cleaned_data.get('due_15_days')
        
        # Apply filters to Base QS
        if start_date:
            money_qs = money_qs.filter(date__gte=start_date)
            sold_qs = sold_qs.filter(date__gte=start_date)
        if end_date:
            money_qs = money_qs.filter(date__lte=end_date)
            sold_qs = sold_qs.filter(date__lte=end_date)
            
        if min_amount:
            # For Money, it's 'amount'. For Sold, it's 'total' (usually what user cares about for range)
            money_qs = money_qs.filter(amount__gte=min_amount)
            sold_qs = sold_qs.filter(total__gte=min_amount)
        if max_amount:
            money_qs = money_qs.filter(amount__lte=max_amount)
            sold_qs = sold_qs.filter(total__lte=max_amount)
            
        # Specific Logic for "Due > 15 Days" -> Filter Items Sold older than 15 days
        if due_15_days:
            cutoff_date = datetime.date.today() - datetime.timedelta(days=15)
            # If checked, we specifically want to SHOW these items in a list
            filtered_items = sold_qs.filter(date__lte=cutoff_date).order_by('date')
            filtered_total = filtered_items.aggregate(Sum('total'))['total__sum'] or 0
            
            # Calculate Total Received (for the subtraction)
            # We use money_qs which might be filtered by other fields if specified, or is all money
            current_total_received = money_qs.aggregate(Sum('amount'))['amount__sum'] or 0
            filtered_balance = filtered_total - current_total_received
            
    # Summary Cards (Filtered)
    total_received = money_qs.aggregate(Sum('amount'))['amount__sum'] or 0
    total_sold = sold_qs.aggregate(Sum('total'))['total__sum'] or 0
    balance = total_sold - total_received
    
    # Chart Data - Aggregate by Date (Filtered)
    daily_received = money_qs.values('date').annotate(total=Sum('amount')).order_by('date')
    daily_sold = sold_qs.values('date').annotate(total=Sum('total')).order_by('date')
    
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
        'filter_form': filter_form,
        'filtered_items': filtered_items, # Pass the list if "Due" was checked
        'filtered_total': filtered_total,
        'filtered_balance': filtered_balance,
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
    
    # Filter
    filter_form = FilterForm(request.GET)
    if filter_form.is_valid():
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        min_amount = filter_form.cleaned_data.get('min_amount')
        max_amount = filter_form.cleaned_data.get('max_amount')
        
        if start_date:
            entries = entries.filter(date__gte=start_date)
        if end_date:
            entries = entries.filter(date__lte=end_date)
        if min_amount:
            entries = entries.filter(amount__gte=min_amount)
        if max_amount:
            entries = entries.filter(amount__lte=max_amount)
    
    total_received = entries.aggregate(Sum('amount'))['amount__sum'] or 0
    
    return render(request, 'sales/money_received.html', {
        'form': form,
        'entries': entries,
        'total_received': total_received,
        'filter_form': filter_form
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
    
    # Filter
    filter_form = FilterForm(request.GET)
    if filter_form.is_valid():
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        min_amount = filter_form.cleaned_data.get('min_amount')
        max_amount = filter_form.cleaned_data.get('max_amount')
        # We also support due_15_days here if user wants to see it on generic list
        due_15_days = filter_form.cleaned_data.get('due_15_days')

        if start_date:
            items = items.filter(date__gte=start_date)
        if end_date:
            items = items.filter(date__lte=end_date)
        if min_amount:
            items = items.filter(total__gte=min_amount)
        if max_amount:
            items = items.filter(total__lte=max_amount)
            
        if due_15_days:
            cutoff_date = datetime.date.today() - datetime.timedelta(days=15)
            items = items.filter(date__lte=cutoff_date)
    
    total_sold = items.aggregate(Sum('total'))['total__sum'] or 0
    
    return render(request, 'sales/item_sold.html', {
        'form': form,
        'items': items,
        'total_sold': total_sold,
        'filter_form': filter_form
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
