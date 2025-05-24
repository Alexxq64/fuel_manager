from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from django.http import JsonResponse

from .models import Nozzle, Transaction
from .forms import FuelArrivalForm, RefuelForm, StatisticsFilterForm


@login_required
def home(request):
    return render(request, 'fuel/home.html')


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
                nozzle=None,
                operator=request.user,
                liters=liters,
                amount=amount
            )

            try:
                transaction.clean()
                transaction.save()

                # Обновляем объем и среднюю цену в резервуаре
                old_volume = tank.current_volume
                old_price = tank.average_price
                total_volume = old_volume + liters

                if total_volume > 0:
                    new_average_price = ((old_volume * old_price) + (liters * price_per_liter)) / total_volume
                else:
                    new_average_price = 0

                tank.current_volume = total_volume
                tank.average_price = new_average_price
                tank.save()

                return redirect('home')

            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = FuelArrivalForm()

    return render(request, 'fuel/fuel_arrival.html', {'form': form})

@login_required
def refuel(request):
    # Получаем все пистолеты с данными о колонках и топливе
    nozzles = Nozzle.objects.select_related('pump', 'tank__fuel_type')

    # Группируем пистолеты по колонкам
    grouped_nozzles = defaultdict(list)
    for nozzle in nozzles:
        grouped_nozzles[nozzle.pump].append(nozzle)

    # Обработка POST-запроса
    if request.method == 'POST':
        form = RefuelForm(request.POST)
        form.fields['nozzle'].queryset = nozzles  # важно: обновляем queryset

        if form.is_valid():
            nozzle = form.cleaned_data['nozzle']
            liters = form.cleaned_data.get('liters')
            amount = form.cleaned_data.get('amount')
            client = form.cleaned_data.get('client')

            tank = nozzle.tank
            selling_price_per_liter = tank.fuel_type.selling_price_per_liter
            average_cost = tank.average_price

            # Определяем, сколько литров и на какую сумму
            if liters:
                calculated_liters = liters
                calculated_amount = liters * selling_price_per_liter
            else:
                calculated_amount = amount
                calculated_liters = amount / selling_price_per_liter

            # Проверка остатка топлива
            if tank.current_volume < calculated_liters:
                form.add_error('liters', 'Недостаточно топлива в резервуаре.')
            else:
                transaction = Transaction(
                    operation_type='OUT',
                    tank=tank,
                    nozzle=nozzle,
                    operator=request.user,
                    liters=calculated_liters,
                    amount=calculated_amount,
                    client=client,
                    selling_price_per_liter=selling_price_per_liter,
                    cost_price_per_liter=average_cost,
                    cost_total=calculated_liters * average_cost
                )
                try:
                    transaction.clean()
                    transaction.save()

                    # Обновляем объем топлива в резервуаре
                    tank.current_volume -= calculated_liters
                    tank.save()

                    return redirect('home')
                except Exception as e:
                    form.add_error(None, str(e))

    else:
        form = RefuelForm()
        form.fields['nozzle'].queryset = nozzles

    # Рендерим шаблон с формой и сгруппированными пистолетами
    return render(request, 'fuel/refuel.html', {
        'form': form,
        'grouped_nozzles': grouped_nozzles.items()
    })


# Дополнительный view для AJAX-запроса цены по выбранному пистолету
def get_price_for_nozzle(request):
    nozzle_id = request.GET.get('nozzle_id')
    if not nozzle_id:
        return JsonResponse({'error': 'No nozzle_id provided'}, status=400)

    try:
        nozzle = Nozzle.objects.select_related('tank__fuel_type').get(id=nozzle_id)
        price = nozzle.tank.fuel_type.selling_price_per_liter
        return JsonResponse({'price': float(price)})
    except Nozzle.DoesNotExist:
        return JsonResponse({'error': 'Nozzle not found'}, status=404)


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
