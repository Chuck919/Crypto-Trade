from django.db import models
import json
from decimal import Decimal

class MartBotState(models.Model):
    bot_name = models.CharField(primary_key=True, max_length=100)
    api_key = models.CharField(max_length=100, blank=True)
    api_secret = models.CharField(max_length=100, blank=True)
    total_profit = models.FloatField(default=0.00)
    transactions = models.IntegerField(default=0)
    sell_price = models.FloatField(null=True, blank=True)
    symbol = models.CharField(max_length=100)
    profit = models.FloatField(null=True, blank=True)
    trailing = models.FloatField(null=True, blank=True)
    scale = models.JSONField(null=True, blank=True)  # For Django 3.1+ (or use TextField for earlier versions)
    rebounce = models.JSONField(null=True, blank=True)  # For Django 3.1+ (or use TextField for earlier versions)
    volume_list = models.JSONField(null=True, blank=True)  # For Django 3.1+ (or use TextField for earlier versions)
    volume = models.FloatField(null=True, blank=True)
    orders = models.IntegerField(null=True, blank=True)
    use = models.FloatField(null=True, blank=True)
    bought = models.IntegerField(default=0)
    buying = models.BooleanField(default=False)
    selling = models.BooleanField(default=False)
    trailing_buy_price = models.FloatField(null=True, blank=True)
    recent_trailing_buy_price = models.FloatField(null=True, blank=True)
    trailing_sell_price = models.FloatField(null=True, blank=True)
    recent_trailing_sell_price = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.bot_name} Bot State"
    
    def save(self, *args, **kwargs):
        # Convert lists to JSON before saving
        self.scale = json.dumps(self.scale)
        self.rebounce = json.dumps(self.rebounce)
        self.volume_list = json.dumps(self.volume_list)
        if self.total_profit is None:
            self.total_profit = 0.00
        super().save(*args, **kwargs)

    def load(self):
        # Convert JSON to lists after loading
        if self.scale:
            self.scale = json.loads(self.scale)
        if self.rebounce:
            self.rebounce = json.loads(self.rebounce)
        if self.volume_list:
            self.volume_list = json.loads(self.volume_list)

class CryptoBots(models.Model):
    
    bot_name = models.CharField(max_length=100, unique=True)
    bot_instance = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return self.bot_name
    
    def get_bot_instance(self):
        return self.bot_instance