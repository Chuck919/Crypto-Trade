from django import forms

class MartingaleForm(forms.Form):
    coin_pair = forms.CharField(max_length=100)
    price_scale = forms.DecimalField(min_value=0.01, max_value=1000, decimal_places=2)
    rebound = forms.DecimalField(min_value=0.01, max_value=1000, decimal_places=2)
    take_profit = forms.DecimalField(min_value=0.01, max_value=1000, decimal_places=2)
    trailing = forms.DecimalField(min_value=0.01, max_value=1000, decimal_places=2)
    stable_coin_amount = forms.DecimalField(min_value=0.01, max_value=1000, decimal_places=2)
    volume_scale = forms.DecimalField(min_value=0.01, max_value=1000, decimal_places=2)
    orders = forms.IntegerField(min_value=1, max_value=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize widgets for DecimalFields to use number input with step=0.01 (2 decimal places)
        decimal_widget = forms.NumberInput(attrs={'step': '0.01'})
        self.fields['price_scale'].widget = decimal_widget
        self.fields['rebound'].widget = decimal_widget
        self.fields['take_profit'].widget = decimal_widget
        self.fields['trailing'].widget = decimal_widget
        self.fields['stable_coin_amount'].widget = decimal_widget
        self.fields['volume_scale'].widget = decimal_widget