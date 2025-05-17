from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import FuelArrivalForm

@login_required
def home(request):
    return render(request, 'fuel/home.html')

@login_required
def fuel_arrival(request):
    if request.method == 'POST':
        form = FuelArrivalForm(request.POST)
        if form.is_valid():
            # Здесь можно обработать данные и сохранить их в БД
            # Например:
            # reservoir = form.cleaned_data['reservoir']
            # liters = form.cleaned_data['liters']
            # price_per_liter = form.cleaned_data['price_per_liter']
            # ... логика сохранения ...

            return redirect('home')  # редирект на главную после успешного сохранения
    else:
        form = FuelArrivalForm()
    return render(request, 'fuel/fuel_arrival.html', {'form': form})