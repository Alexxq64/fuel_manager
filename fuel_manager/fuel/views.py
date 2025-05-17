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


from .forms import RefuelForm

@login_required
def refuel(request):
    if request.method == 'POST':
        form = RefuelForm(request.POST)
        if form.is_valid():
            nozzle = form.cleaned_data['nozzle']
            liters = form.cleaned_data['liters']
            amount = form.cleaned_data['amount']
            tank = nozzle.tank

            transaction = Transaction(
                operation_type='OUT',
                tank=tank,
                nozzle=nozzle,
                operator=request.user,
                liters=liters or 0,
                amount=amount or 0,
            )

            try:
                transaction.clean()  # вызов валидации из модели
                transaction.save()
                return redirect('home')
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = RefuelForm()

    return render(request, 'fuel/refuel.html', {'form': form})
