from django.db import models
from django.contrib.auth.models import User

class FuelType(models.Model):
    name = models.CharField(max_length=50)
    selling_price_per_liter = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Новое поле

    def __str__(self):
        return self.name

class Tank(models.Model):
    name = models.CharField(max_length=100)
    fuel_type = models.ForeignKey(FuelType, on_delete=models.CASCADE)
    capacity = models.DecimalField(max_digits=10, decimal_places=2)
    current_volume = models.DecimalField(max_digits=10, decimal_places=2)
    average_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # NEW

    def __str__(self):
        return f"{self.name} ({self.fuel_type.name})"

class Pump(models.Model):
    name = models.CharField(max_length=50)  # Просто название/номер

    def __str__(self):
        return self.name

class Nozzle(models.Model):
    number = models.PositiveIntegerField()  # 1, 2, 3
    pump = models.ForeignKey(Pump, on_delete=models.CASCADE)
    tank = models.ForeignKey(Tank, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.pump.name} — Пистолет {self.number}"

from django.core.exceptions import ValidationError

class Transaction(models.Model):
    OPERATION_CHOICES = [
        ('IN', 'Приход'),
        ('OUT', 'Расход'),
    ]

    operation_type = models.CharField(max_length=3, choices=OPERATION_CHOICES)
    datetime = models.DateTimeField(auto_now_add=True)

    tank = models.ForeignKey('Tank', on_delete=models.CASCADE)
    nozzle = models.ForeignKey('Nozzle', on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True, blank=True)

    operator = models.ForeignKey(User, on_delete=models.CASCADE)
    liters = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    selling_price_per_liter = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # новая цена продажи за литр
    selling_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Новое

    # Себестоимость
    cost_price_per_liter = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def clean(self):
        if self.operation_type == 'IN':
            if self.nozzle is not None:
                raise ValidationError("Приход топлива должен быть напрямую в резервуар (без пистолета).")
        elif self.operation_type == 'OUT':
            if self.nozzle is None:
                raise ValidationError("Для расхода топлива необходимо указать пистолет.")
            if self.nozzle.tank != self.tank:
                raise ValidationError("Пистолет должен быть привязан к выбранному резервуару.")

    def save(self, *args, **kwargs):
        if self.operation_type == 'OUT' and self.tank:
            self.cost_price_per_liter = self.tank.average_price
            self.cost_total = self.liters * self.cost_price_per_liter
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_operation_type_display()} {self.liters} л ({self.tank})"


class Client(models.Model):
    name = models.CharField(max_length=100)
    is_corporate = models.BooleanField(default=False)

    def __str__(self):
        return self.name
