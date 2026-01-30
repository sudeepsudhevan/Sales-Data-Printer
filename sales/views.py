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

def calculate_status():
    # 1. Reset everything to False first (simplest way to ensure consistency on re-calc)
    # Be careful with performance on large datasets, but for small scale this is fine.
    # Ideally only re-calc from last changes, but for now full re-calc ensures correctness.
    
    # Get all items ordered by date
    all_items = ItemSold.objects.all().order_by('date')
    all_money = MoneyReceived.objects.all().order_by('date')
    
    total_money_received = all_money.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Mark Items as Closed based on Total Money
    cumulative_sales = 0
    closed_items_value = 0
    
    for item in all_items:
        cumulative_sales += item.total
        if cumulative_sales <= total_money_received:
            if not item.is_closed:
                item.is_closed = True
                item.save()
            closed_items_value += item.total
        else:
            if item.is_closed:
                item.is_closed = False
                item.save()
                
    # Mark Money as Settled based on Closed Items Value
    # (Money is "settled" if it has been "used up" by closed items)
    cumulative_money = 0
    for money in all_money:
        cumulative_money += money.amount
        if cumulative_money <= closed_items_value:
             if not money.is_settled:
                money.is_settled = True
                money.save()
        else:
            if money.is_settled:
                money.is_settled = False
                money.save()
    
    return closed_items_value

def index(request):
    # Recalculate status before showing dashboard
    calculate_status()
    
    # Filter Form
    filter_form = FilterForm(request.GET or None)
    
    # Base QuerySets (for charts and summary)
    money_qs = MoneyReceived.objects.all()
    sold_qs = ItemSold.objects.all()
    
    filtered_items = None
    filtered_total = 0
    filtered_balance = 0
    
    show_closed = False
    
    if filter_form.is_valid():
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        min_amount = filter_form.cleaned_data.get('min_amount')
        max_amount = filter_form.cleaned_data.get('max_amount')
        due_days = filter_form.cleaned_data.get('due_days')
        show_closed = filter_form.cleaned_data.get('show_closed')
        
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
            
        # Specific Logic for "Items List" on Dashboard
        # Now we use 'due_days' OR just general list view if we want.
        # But per original logic, filtered_items was specifically for "Due > X Days".
        # Let's keep that but respect 'show_closed'.
        
        if due_days:
            cutoff_date = datetime.date.today() - datetime.timedelta(days=due_days)
            # If checked, we specifically want to SHOW these items in a list
            
            # Start with base likely filtered by date/amount
            filtered_items = sold_qs.filter(date__lte=cutoff_date).order_by('date')
            
            # Application of show_closed toggle
            if not show_closed:
                filtered_items = filtered_items.filter(is_closed=False)
                
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
    calculate_status()
    if request.method == 'POST':
        form = MoneyReceivedForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('money_received')
    else:
        form = MoneyReceivedForm(initial={'date': datetime.date.today()})
    
    entries = MoneyReceived.objects.all().order_by('-date')
    
    # Filter
    filter_form = FilterForm(request.GET or None)
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
    unsettled_money = entries.filter(is_settled=False).aggregate(Sum('amount'))['amount__sum'] or 0
    
    return render(request, 'sales/money_received.html', {
        'form': form,
        'entries': entries,
        'total_received': total_received,
        'unsettled_money': unsettled_money,
        'filter_form': filter_form
    })

def item_sold(request):
    calculate_status()
    if request.method == 'POST':
        form = ItemSoldForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_sold')
    else:
        form = ItemSoldForm(initial={'date': datetime.date.today()})
    
    items = ItemSold.objects.all().order_by('-date')
    
    # Filter
    filter_form = FilterForm(request.GET or None)
    if filter_form.is_valid():
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        min_amount = filter_form.cleaned_data.get('min_amount')
        max_amount = filter_form.cleaned_data.get('max_amount')
        # We also support due_days here if user wants to see it on generic list
        due_days = filter_form.cleaned_data.get('due_days')
        show_closed = filter_form.cleaned_data.get('show_closed') # Add checking show_closed

        if start_date:
            items = items.filter(date__gte=start_date)
        if end_date:
            items = items.filter(date__lte=end_date)
        if min_amount:
            items = items.filter(total__gte=min_amount)
        if max_amount:
            items = items.filter(total__lte=max_amount)
            
        if due_days:
            cutoff_date = datetime.date.today() - datetime.timedelta(days=due_days)
            items = items.filter(date__lte=cutoff_date)
            
        if show_closed is False: # If not explictly True (and if field exists)
             # Actually, simpler: if not filter_form.cleaned_data.get('show_closed'):
             pass
             # We haven't implemented filtering logic based on show_closed in item_sold VIEW yet, 
             # but user just asked for AMOUNT. 
             # Let's add the Amount calculation first.
    
    total_sold = items.aggregate(Sum('total'))['total__sum'] or 0
    open_sales = items.filter(is_closed=False).aggregate(Sum('total'))['total__sum'] or 0
    
    return render(request, 'sales/item_sold.html', {
        'form': form,
        'items': items,
        'total_sold': total_sold,
        'open_sales': open_sales,
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
