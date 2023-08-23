import time
import sqlite3
from decimal import Decimal, ROUND_DOWN
from binance.client import Client
from authentication.models import CustomUser
from django.db.models import F, Max
import json
from .models import MartBotState
import ast

class MartBot:
    def __init__(self, api_key, api_secret, key, variables):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = Client(api_key, api_secret, tld='us')
        self.key = key
        self.total_profit = 0.00
        self.transactions = 0
        self.sell_price = None
        self.symbol = variables[0]
        self.profit = float(variables[3])
        self.trailing = float(variables[4])

        try:
            string_scale = variables[1].split(',')
            self.scale = [float(i) for i in string_scale]
            string_rebounce = variables[2].split(',')
            self.rebounce = [float(i) for i in string_rebounce]
        except:
            self.scale = float(variables[1])
            self.rebounce = float(variables[2])

        self.volume_list = []
        self.volume = float(variables[6])
        self.orders = int(variables[7])
        self.use = float(variables[5])
        try:
            series_sum = (1-self.volume**self.orders)/(1-self.volume)
            x = (self.use + self.total_profit)/ series_sum
        except:
            x = (self.use + self.total_profit)/self.orders
        for i in range(self.orders):
            self.volume_list.append(x*self.volume**i)

        self.price_bought = []
        self.amount_bought = []
        self.bought = 0

        self.buying = False
        self.selling = False

        self.trailing_buy_price = None
        self.recent_trailing_buy_price = None
        self.trailing_sell_price = None
        self.recent_trailing_sell_price = None


    def print_local_variables(self):
        local_vars = self.__dict__
        for var_name, var_value in local_vars.items():
            print(f"{var_name}: {var_value}")

    def main(self, new_price):
        print(f'in bot {self.key} main')
        #self.print_local_variables()
        if self.bought == 0:
            self.buy_order(new_price)

        elif self.buying is True:
            self.trailing_buy(new_price)

        elif self.selling is True:
            self.trailing_sell(new_price)

        elif self.bought >= 1 and self.bought < self.orders and new_price <= self.price_bought[-1]*(1-self.scale/100):
            self.buying = True
            self.recent_trailing_buy_price = new_price
            self.trailing_buy_price = round(new_price*(1+self.rebounce/100), 4)

        elif self.bought >= 1 and new_price >= self.sell_price:
            self.selling = True
            self.recent_trailing_sell_price = new_price
            self.trailing_sell_price = round(new_price*(1-self.trailing/100), 4)

        else:
            pass

    def price_check(self, tickers):
        for ticker in tickers:
            symbol_check = ticker['symbol']
            if symbol_check == self.symbol:
                new_price = float(ticker['price'])
        print(f'in bot {self.key}')
        print(new_price)
        self.main(new_price)


    def trailing_buy(self, new_price):

        if self.recent_trailing_buy_price > new_price:
            print('buying')
            self.trailing_buy_price = self.trailing_buy_price - (self.trailing_buy_price - new_price)
            self.recent_trailing_buy_price = new_price

        #if price goes above trailing buy amount, creates a buy order
        elif self.trailing_buy_price <= new_price:
            self.buy_order(new_price)

        else:
            pass


    def trailing_sell(self, new_price):
        if self.recent_trailing_sell_price < new_price:
            self.trailing_sell_price = self.trailing_sell_price - (self.trailing_sell_price - new_price)
            self.recent_trailing_sell_price = new_price
            
            print('selling')

        #if price goes above trailing buy amount, creates a buy order
        elif self.trailing_sell_price >= new_price:
            print(new_price)
            self.sell_order()

        else:
            pass

    def buy_order(self, new_price):
        #buy_order = self.client.order_market_buy(symbol=self.symbol, quantity=float(Decimal(self.volume_list[self.bought] / new_price).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)))
        '''
        buy_order = client.create_test_order(
            symbol=self.symbol,
            side='BUY',
            type='MARKET',
            quantity=round(self.volume_list[self.bought]/new_price, 4)
        )'''
        self.price_bought.append(new_price)
        self.amount_bought.append(float(Decimal(self.volume_list[self.bought] / new_price).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)))
        print(self.amount_bought)
        print(self.price_bought)

        total_cost = 0
        for i in range(len(self.price_bought)):
            total_cost += self.price_bought[i] * self.amount_bought[i]
        self.sell_price = total_cost * (1 + self.profit/100) / sum(self.amount_bought)

        self.bought += 1
        print(self.bought)
        self.trailing_buy_price = None
        self.recent_trailing_buy_price = None
        self.buying = False
        
        print('bought')

    def sell_order(self):
        selling_amount = float(Decimal(sum(self.amount_bought)).quantize(Decimal('0.0001'), rounding=ROUND_DOWN))
        print(selling_amount)
        #sell_order = self.client.order_market_sell(symbol = self.symbol, quantity = selling_amount)
        '''
            symbol=self.symbol,
            side='SELL',
            type='MARKET',
            quantity=sum(self.amount_bought)
        )'''

        #calculates profit
        total_round_cost = 0
        for i in range(len(self.price_bought)):
            total_round_cost += self.price_bought[i] * self.amount_bought[i]
        round_profit = round(self.recent_trailing_sell_price * sum(self.amount_bought) - total_round_cost, 4)
        self.total_profit += round_profit


        self.volume_list = []
        series_sum = (1-self.volume**self.orders)/(1-self.volume)
        x = (self.use + self.total_profit)/ series_sum
        for i in range(self.orders):
            self.volume_list.append(x*self.volume**i)

        self.price_bought = []
        self.amount_bought = []
        self.sell_price = None
        self.trailing_sell_price = None
        self.recent_trailing_sell_price = None
        self.bought = 0
        self.transactions += 1
        self.selling = False
        print(f'\n\nTotal Transactions of {self.key}: {self.transactions}')
        print(f'Round Profit: {round(round_profit, 4)}')
        print(f'Total Profit: {round(self.total_profit, 4)}')
        
        print('sold')

    def save_state(self):
        print(self.key)
        state, created = MartBotState.objects.get_or_create(api_secret=self.api_secret, bot_name=self.key)

        state.api_key = self.api_key
        state.api_secret = self.api_secret
        state.total_profit = self.total_profit
        state.transactions = self.transactions
        state.sell_price = self.sell_price
        state.symbol = self.symbol
        state.profit = self.profit
        state.trailing = self.trailing
        state.volume = self.volume
        state.orders = self.orders
        state.use = self.use
        state.bought = self.bought
        state.buying = self.buying
        state.selling = self.selling
        state.trailing_buy_price = self.trailing_buy_price
        state.recent_trailing_buy_price = self.recent_trailing_buy_price
        state.trailing_sell_price = self.trailing_sell_price
        state.recent_trailing_sell_price = self.recent_trailing_sell_price

        # Convert lists to JSON before saving
        state.scale = json.dumps(float(self.scale))
        state.rebounce = json.dumps(float(self.rebounce))
        print(type(self.volume_list))
        state.volume_list = json.dumps(self.volume_list)
        print(type(state.volume_list))
        state.price_bought = json.dumps(self.price_bought)
        state.amount_bought = json.dumps(self.amount_bought)
        state.save()


        print('saved')
            
            
    
    def load_state(self):
        try:
            state = MartBotState.objects.get(api_secret=self.api_secret, bot_name=self.key)
            self.total_profit = state.total_profit
            self.transactions = state.transactions
            self.sell_price = state.sell_price
            self.symbol = state.symbol
            self.profit = state.profit
            self.trailing = state.trailing
            self.volume = state.volume
            self.orders = state.orders
            self.use = state.use
            self.bought = state.bought
            self.buying = state.buying
            self.selling = state.selling
            self.trailing_buy_price = state.trailing_buy_price
            self.recent_trailing_buy_price = state.recent_trailing_buy_price
            self.trailing_sell_price = state.trailing_sell_price
            self.recent_trailing_sell_price = state.recent_trailing_sell_price
            
            print(state.scale)
            print(state.rebounce)
            print(state.volume_list)
            
            #if '[' in state.scale:
            self.scale = float(json.loads(state.scale))
            print(self.scale)
            #self.scale = self.scale.strip("[]")
            #self.scale = self.scale.split(",")
            #self.scale = [float(item.strip()) for item in self.scale]
            #print(self.scale)
        #else:
            #self.scale = float(json.loads(state.scale))
            #print(self.scale)
            

            self.rebounce = float(json.loads(state.rebounce))
            print(self.rebounce)
            #if '[' in self.rebounce:
                #self.rebounce = self.rebounce.strip("[]")
                #self.rebounce = self.rebounce.split(",")
                #self.rebounce = [float(item.strip()) for item in self.rebounce]
                #print(self.rebounce)
           # else:
                #self.rebounce = float(json.loads(state.rebounce))
                #print(self.rebounce)
            print(type(state.volume_list))
            self.volume_list = json.loads(state.volume_list)
            print(self.volume_list)
            print(type(state.volume_list))

            if '[' in state.volume_list:
                self.volume_list = self.volume_list.strip("[]")
                self.volume_list = self.volume_list.split(",")
                self.volume_list = [float(item.strip()) for item in self.volume_list]
                print(self.volume_list)
            else:
                self.volume_list = float(json.loads(state.volume_list))
                print(self.volume_list)
            

            self.amount_bought = json.loads(state.amount_bought)
            self.amount_bought = [float(item) for item in self.amount_bought]
            #print(self.amount_bought)
            #self.amount_bought = self.amount_bought.strip("[]")
            #self.amount_bought = self.amount_bought.split(",")
            #self.amount_bought = [float(item.strip()) for item in self.amount_bought]
            #print(self.amount_bought)
            #self.amount_bought = float(json.loads(state.amount_bought))
            #print(self.amount_bought)
        

            self.price_bought = json.loads(state.price_bought)
            self.price_bought = [float(item) for item in self.price_bought]
            #print(self.price_bought)
            #self.price_bought = self.price_bought.strip("[]")
            #self.price_bought = self.price_bought.split(",")
            #self.price_bought = [float(item.strip()) for item in self.price_bought]
           # print(self.price_bought)

        except MartBotState.DoesNotExist:
            # If the state does not exist, use the original values provided to the bot.
            pass
            
