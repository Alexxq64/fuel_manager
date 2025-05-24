from django import forms

from .models import FuelType, Tank
class FuelArrivalForm(forms.Form):
    fuel_type = forms.ModelChoiceField(
        queryset=FuelType.objects.all(),
        label='Тип топлива',
        empty_label="Выберите тип топлива"
    )

    tank = forms.ModelChoiceField(
        queryset=Tank.objects.none(),
        label='Резервуар',
        empty_label="Сначала выберите тип топлива"
    )

    liters = forms.DecimalField(
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        label='Литры'
    )

    price_per_liter = forms.DecimalField(
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        label='Цена за литр'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tank'].queryset = Tank.objects.all()


from .models import Nozzle, Client
from django import forms
from .models import Nozzle, Client

class RefuelForm(forms.Form):
    nozzle = forms.ModelChoiceField(
        queryset=Nozzle.objects.select_related('pump', 'tank'),
        label='Пистолет',
        empty_label=None,
        widget=forms.RadioSelect
    )
    liters = forms.DecimalField(
        required=False,
        min_value=0.01,
        decimal_places=2,
        max_digits=10,
        label='Литры'
    )
    amount = forms.DecimalField(
        required=False,
        min_value=0.01,
        decimal_places=2,
        max_digits=12,
        label='Сумма'
    )
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=False,
        empty_label="Покупатель (анонимно)",
        label='Клиент'
    )

    def clean(self):
        cleaned_data = super().clean()
        liters = cleaned_data.get('liters')
        amount = cleaned_data.get('amount')

        if not liters and not amount:
            raise forms.ValidationError("Укажите либо объем в литрах, либо сумму.")
        if liters and amount:
            raise forms.ValidationError("Укажите только объем в литрах ИЛИ только сумму, не оба значения.")

        return cleaned_data


class StatisticsFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='С даты'
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='По дату'
    )
