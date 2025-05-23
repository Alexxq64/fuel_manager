from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import FuelArrivalForm

@login_required
def home(request):
    return render(request, 'fuel/home.html')

from .forms import FuelArrivalForm
from .models import Transaction

@login_required
def fuel_arrival(request):
    if request.method == 'POST':
        form = FuelArrivalForm(request.POST)
        if form.is_valid():
            tank = form.cleaned_data['tank']
            liters = form.cleaned_data['liters']
            price_per_liter = form.cleaned_data['price_per_liter']
            amount = liters * price_per_liter

            transaction = Transaction(
                operation_type='IN',
                tank=tank,
                nozzle=None,  # приход — без пистолета
                operator=request.user,
                liters=liters,
                amount=amount
            )

            try:
                transaction.clean()
                transaction.save()

                # Обновим объём топлива в резервуаре
                tank.current_volume += liters
                tank.save()

                return redirect('home')
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = FuelArrivalForm()

    return render(request, 'fuel/fuel_arrival.html', {'form': form})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RefuelForm
from .models import Nozzle, Transaction
from collections import defaultdict

@login_required
def refuel(request):
    # Загружаем пистолеты с привязкой к колонкам и типам топлива
    nozzles = Nozzle.objects.select_related('pump', 'tank__fuel_type')

    # Группируем пистолеты по колонке
    grouped_nozzles = defaultdict(list)
    for nozzle in nozzles:
        grouped_nozzles[nozzle.pump].append(nozzle)

    if request.method == 'POST':
        form = RefuelForm(request.POST)
        # Обновляем queryset, чтобы шаблон корректно отрисовал radio-кнопки
        form.fields['nozzle'].queryset = nozzles
        if form.is_valid():
            nozzle = form.cleaned_data['nozzle']
            liters = form.cleaned_data['liters']
            amount = form.cleaned_data['amount']
            client = form.cleaned_data.get('client')
            tank = nozzle.tank

            transaction = Transaction(
                operation_type='OUT',
                tank=tank,
                nozzle=nozzle,
                operator=request.user,
                liters=liters or 0,
                amount=amount or 0,
                client=client
            )

            try:
                transaction.clean()
                transaction.save()
                return redirect('home')
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = RefuelForm()
        form.fields['nozzle'].queryset = nozzles

    return render(request, 'fuel/refuel.html', {
        'form': form,
        'grouped_nozzles': grouped_nozzles.items()  # передаём как (pump, [nozzles])
    })

from .forms import StatisticsFilterForm

@login_required
def statistics_view(request):
    form = StatisticsFilterForm(request.GET or None)
    transactions = Transaction.objects.all()

    if form.is_valid():
        start = form.cleaned_data.get('start_date')
        end = form.cleaned_data.get('end_date')

        if start:
            transactions = transactions.filter(datetime__date__gte=start)
        if end:
            transactions = transactions.filter(datetime__date__lte=end)

    # Подготовка данных для графика
    chart_data = {}
    for t in transactions:
        day = t.datetime.date().isoformat()
        chart_data.setdefault(day, 0)
        chart_data[day] += float(t.liters)

    labels = list(chart_data.keys())
    data = list(chart_data.values())

    context = {
        'form': form,
        'transactions': transactions.order_by('-datetime'),
        'labels': labels,
        'data': data,
    }
    return render(request, 'fuel/statistics.html', context)
