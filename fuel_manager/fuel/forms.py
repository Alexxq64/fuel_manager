from django import forms

class FuelArrivalForm(forms.Form):
    RESERVOIR_CHOICES = [
        ('tank1', 'Резервуар 1'),
        ('tank2', 'Резервуар 2'),
        ('tank3', 'Резервуар 3'),
    ]

    reservoir = forms.ChoiceField(choices=RESERVOIR_CHOICES, label='Резервуар')
    liters = forms.DecimalField(min_value=0, max_digits=10, decimal_places=2, label='Литры')
    price_per_liter = forms.DecimalField(min_value=0, max_digits=10, decimal_places=2, label='Цена за литр')
