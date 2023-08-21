from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django_q.tasks import async_task, async_chain, fetch
import time
import sqlite3
from decimal import Decimal, ROUND_DOWN
from binance.client import Client
from authentication.models import CustomUser
from tradebots.bots import MartBot
from django.contrib import messages
from .models import MartBotState, CryptoBots
from .forms import MartingaleForm
from django.db.models import F, Max
import pickle
import json

global task_running
task_running = False

global client
client = None

global task_id
task_id = None

class PriceUpdater:
    def __init__(self, client):
        self.running = False
        self.client = client

    def start(self):
        self.running = True
        self.update_prices()

    def stop(self):
        self.running = False

    def get_current_price(self):
        tickers = self.client.get_all_tickers()
        return tickers

    def update_prices(self):
        while self.running:
            current_price = self.get_current_price()
            crypto_bots = CryptoBots.objects.all()
            print(crypto_bots)
            for bot in crypto_bots:
                if bot.bot_instance is not None:
                    print(current_price)
                    bot_instance = pickle.loads(bot.bot_instance)
                    try:
                        bot_instance.load_state()
                        bot_instance.price_check(current_price)
                        bot_instance.save_state()
                    except:
                        pass
            time.sleep(1)

@login_required
def bots(request):
    global client
    user = request.user
    api_key = user.api_key
    api_secret = user.api_secret
    print(api_key)
    print(api_secret)
    if not client:
        client = Client(api_key, api_secret, tld='us')
    return render(request, 'tradebots/index.html')

@login_required
def success(request):
    return render(request, 'tradebots/success.html')

@login_required
def smart(request):
    return render(request, 'tradebots/smart.html')

@login_required
def grid(request):
    return render(request, 'tradebots/grid.html')


@login_required
def martingale(request):
    global client
    global task_id
    
    print(client)
    print("Inside martingale function.")
    
    if request.method == 'POST':
        print("POST request received.")
        form = MartingaleForm(request.POST)
        if form.is_valid():
            try:
                coin_pair = form.cleaned_data['coin_pair']
                price_scale = form.cleaned_data['price_scale']
                rebound = form.cleaned_data['rebound']
                take_profit = form.cleaned_data['take_profit']
                trailing = form.cleaned_data['trailing']
                stable_coin_amount = form.cleaned_data['stable_coin_amount']
                volume_scale = form.cleaned_data['volume_scale']
                orders = form.cleaned_data['orders']
                variables = [coin_pair, price_scale, rebound, take_profit, trailing, stable_coin_amount, volume_scale, orders]

                symbol_info = client.get_symbol_info(coin_pair)
                print(symbol_info)
                
            except:
                print('error1')
                messages.error(request, 'Invalid input fields')
                return render(request, 'tradebots/martingale.html', {'form': form})
                

            if task_running == False:
                task_running_check()
                print(task_running)
                price_updater = PriceUpdater(client)
                try:
                    task_id = async_task(price_updater.start)
                except:
                    print('error2')
                    messages.error(request, 'Problem starting task')
                    return render(request, 'tradebots/martingale.html', {'form': form})   
            
            bot_name = ('Martingale Bot')
            number = 1
            key = f'{bot_name} {number}'
            while True:
                if not MartBotState.objects.filter(bot_name=key).exists() and not CryptoBots.objects.filter(bot_name=key).exists():
                    break
                number += 1
                key = f'{bot_name} {number}'  
                
            user = request.user
            api_key = user.api_key
            api_secret = user.api_secret
            
            instance = MartBot(api_key, api_secret, key, variables)
            instance_bytes = pickle.dumps(instance)
            
            crypto_bot = CryptoBots(bot_name=key, bot_instance=instance_bytes)
            crypto_bot.save()
            print(task_id)


            return render(request, 'tradebots/success.html')
        else:
            messages.error(request, 'Invalid form data. Please fill out all required fields.')
    else:
        print("GET request received.")
        form = MartingaleForm()

    context = {
        'form': form
    }
    return render(request, 'tradebots/martingale.html', context)

    
def task_running_check():
    global task_running
    task_running = True
