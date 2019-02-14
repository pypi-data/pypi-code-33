import uuid
from abc import ABC, abstractmethod

import crayons as cy
import pandas as pd
from loguru import logger
from funhandler.blocks.general.performance import (create_drawdowns,
                                                   create_sharpe_ratio)
from funhandler.blocks import BaseBlock

# TODO: Add a state "converter" to get a vectorize version of the current state
# TODO: Also add a reward vector to let the environment determine what's considered "good"
class Portfolio(BaseBlock):
    def __init__(self, name, **kwargs):
        super().__init__(name, "portfolio")
        self.required = ["store"]
        self.task_parts = {}
        self.dsk = None
        
        """Use portfolio to add/remove holdings"""
        logger.opt(ansi=True).info("Initializing <i>Portfolio</i>")
        store = kwargs.get("store", None)
        if store is not None:
            self.task_parts["store"] = store
        

    def check_required(self):
        kwkeys = self.task_parts.keys()

        for i in self.required:
            if i not in kwkeys:
                msg = "{} not found in {}".format(i, self.__repr__())
                raise AttributeError(msg)

    def add_task_parts(self, parts):
        if isinstance(parts, dict):
            # print(parts_dict)
            total = {**self.task_parts, **parts}
            self.task_parts = total

    def reset(self):
        self.cash = 100000
        self.trades = []
        self.holdings = {}
        self.share_balance = 0
        self.total_balance = 0
        self.shares = {} # Should hold the balance of the shares for stocks
        self.timed_holdings = [] # Stores everything about the portfolio over a given time. To read make sure to resample
        self.exchanges = []
        # self.store = Storage()
        self.general_pct = {
            'shares': 0,
            'cash': 0
        }
        self.pct_cash = 0.4 # Meaning I want at least 40% cash
        self.latest_price = 0
        self.check_required()
        logger.opt(ansi=True).info("<m>Portfolio Initiated</m> Cash: <g>{}</g> Minimum pct cash: {}", self.cash, round(self.pct_cash, 3))

    def step(self, action, **kwargs):
        logger.opt(ansi=True).info("This is usually an order")
        logger.opt(ansi=True).info("run an order")
        logger.opt(ansi=True).info("log the general value")
        logger.opt(ansi=True).info("Run stats to determine the strength of the system")

    def set_price(self, latest):
        self.latest_price = latest

    def snapshot(self):
        """Gets the latest balance of the user and stores it inside of a timestamp"""
        pass
    
    def get_exchange_balances(self):
        """Get the balance of the exchanges"""
        exchanges = self.exchanges
        if len(exchanges) > 0:
            for e in exchanges:
                print(e.balance)
    
    
    def order(self, direction, symbol, amount, price, timestamp):
        if direction == "BUY":
            self.buy(symbol, amount, price, timestamp)
        elif direction == "SELL":
            self.sell(symbol, amount, price, timestamp)    
    
    
    def buy(self, symbol, amount, price, timestamp):
        total_amount = price*amount
        if self.cash < total_amount:
            print("We don't have enough money")
        else:            
            # The stocks variable has the trade information
            self.trades.append({
                'symbol': symbol,
                'amount': amount,
                'price': price,
                'total': total_amount,
                'timestamp': timestamp,
                'type': "BUY"
            })

            self.cash -= total_amount
            self.update(timestamp)
            # if self.level_portfolio(total_amount, sy):
                # Also check to see if our purchase will fuck with the max pct for the symbol
                
    
    
    def level_portfolio(self, total_amount, symbol, direction):
        """Here we check to see if the current purchase will go above the decided upon portfolio"""
        lvl = dict()
        lvl['shares'] = 0.4
        lvl['cash'] = 0.6

        # Get the valuation now
        if self.general_pct is None:
            return False, 0
        
        if 'shares' not in self.general_pct:
            print("Shares don't exist rn. Abort son!!!!")
            return False, 0
        

        if direction == "BUY":
            hypothetical_cash = self.cash - total_amount
            
            hypothetical_share_balance = self.share_balance + total_amount
            hypothetical_total_balance = hypothetical_cash+hypothetical_share_balance
            
            

            hcpct = round((hypothetical_cash / hypothetical_total_balance), 4)
            hspct = round((hypothetical_share_balance / hypothetical_total_balance), 4)
            

            print("Hypothetical Remaining Cash: ", hypothetical_cash)
            print("Hypothetical Share Balance: ", hypothetical_share_balance)
            print("Hypothetical Total Balance: ", hypothetical_total_balance)


            print("---\n\n---")

            print("Hypothetical Cash Percentages: ", hcpct)
            print("Hypothetical Cash Percentages: ", hspct)

            # If we're selling, check to see if
            if hcpct < lvl['cash']:
                # We're saying that we can buy the given percentage
                # Otherwise look for the max that can be done
                print(cy.yellow("\nHypothetical Cash Percentage Above\n"))
                return False, 0

            print(cy.yellow("\nHypothetical Share Percentage Above\n"))
            return True, 0


        elif direction == "SELL":
            if symbol not in self.shares.keys():
                print("Shares don't currently exist. We're adding them and setting it {} to zero".format(symbol))
                self.shares[symbol] = 0.0
                return False, 0
            
            elif self.holdings == {}:
                return False, 0
            

            amt = self.shares[symbol]
            
            is_little = ((amt - total_amount) < 0)
            if amt == 0 or is_little:
                # Check to see if we can get a difference
                if is_little:
                    # print(cy.yellow(amt, bold=True))
                    return True, amt
                logger.opt(ansi=True).debug("Not enough to currently trade")
                return False, 0
            # Check to see if we can actually buy the amount avaiable
            # If the shares is negative after cant do it
            # current_price = get the current price of this symbol BUT FUCKIT!!!!!
            return True, 0
        
    
    def sell(self, symbol, amount, price, timestamp):
        # Should look through current holdings and determine if there's enough to sell of that volume
        holdings = self.holdings # Safety Bitch
        if symbol in holdings:
            # Perfect, now check to see if we have enough
            act = holdings[symbol]
            amt = act['amount']
            if amount <= amt:
                # Calculate the total sell
                # TODO: Reference the trades and calculate profits
                
                total = amount*price
                self.trades.append({
                    'symbol': symbol,
                    'amount': amount,
                    'price': price,
                    'total': total,
                    'timestamp': timestamp,
                    'type': "SELL"
                })
                self.cash += total
        self.update(timestamp)
    
    def fill_order(self, event):
        """Get the variables for the order then use the order method"""
        symbol = "{}/{}".format(event.base, event.trade)
        direction = event.direction
        price = event.price
        quantity = event.quantity
        amount = (quantity/price)
        timestamp = event.timeindex
        
        self.order(direction, symbol, amount, price, timestamp)

    def preload_order(self, event):
        """Here we load the orders for the user"""
        {
            'type': 'SIGNAL', 
            'base': 'USDT', 
            'trade': 'BTC', 
            'datetime': 1535742000, 
            'signal_type': 'SELL', 
            'source': 'both', 
            'strength': 36.27075347237506
        }
        SYMBOL = "{}/{}".format(event.base, event.trade)
        source = event.source
        direction = event.signal_type

        
        strength = event.strength
        multiplier = 0.0
        if source == "both":
            # OPTIMIZE BRUH
            multiplier = 0.04
        if source == "fib":
            # OPTIMIZE BRUH (SK-Optimize)
            # Experiment - 
                # - Optimize by risk profile, 
                # - profit potential
                # - and shit of the coin
            multiplier = 0.007
        can_order = True
        if direction == "SELL":
            # We favor sells for the time being
            total_order_size = self.cash * multiplier * (strength * 0.03)
        elif direction == "BUY":
            total_order_size = self.cash * multiplier * (strength * 0.025)
        
        
        can_order, amt = self.level_portfolio(total_order_size, SYMBOL, direction)
        if amt != 0:
            total_order_size = amt
        
        return {
            'is_act': can_order,
            'size': total_order_size
        }
    
    def timestamp_holdings(self, timestamp):
        """Gets the timestamped holdings for the user"""
        holdings = {}
        holdings['time'] = timestamp
        holdings['cash'] = self.cash
        holdings['total'] = self.cash
        for k, v in self.shares.items():
            holdings[k] = v
            holdings['total'] += v
        self.timed_holdings.append(holdings)
    
    
    def update(self, timestamp):
        self.update_holdings()
        self.update_balance()
        self.update_portfolio_percentages()
        if timestamp != 0:
            self.timestamp_holdings(timestamp)
            
    
    def update_holdings(self):
        # Should have holdings for the trades that are available
        # Buys add to the total for a symbol, sells take from the value of a symbol
        # The total for each symbol should be what's left
        current_holdings = {}
        for t in self.trades:
            order_type = t['type'] # Placehold the order type and amount
            sym = t['symbol'] # Placehold the order type and amount
            amt = t['amount'] # Placehold the order type and amount
            # Get the current timestamp
            # Get the price of sym
            # If the price doesn't currently exist, probably should just exit
            if order_type == "BUY":
                # check to see if it's current holdings already
                if sym in current_holdings:
                    # Get the current holdings
                    current_holdings[sym]['amount'] += amt 
                else:
                    current_holdings[sym] = {
                        'amount': 0
                    }
                    current_holdings[sym]['amount'] += amt
            elif order_type == "SELL":
                if sym in current_holdings:
                    if current_holdings[sym]['amount'] < amt:
                        print("That mathematically shouldn't be. We can't subtract from what we don't have.")
                    if current_holdings[sym]['amount'] >= amt:
                        current_holdings[sym]['amount'] -= amt
                else:
                    print("Cant subtract from what we don't have")
        
        
        self.holdings = current_holdings

        
    
    def update_balance(self):
        """Should update the balance of the holding"""
        # Step 1: Run through all of the holdings you have
        # Step 2: Get the price of the symbol (for now get the last instance of what you bought/sold for)
        # Step 3: Say you have the shares balance
        # Step 4: Combine the cash and shares balance to get the balance
        # Don't want to fuck with this variable too much
        holdings = self.holdings
        rev_trades = list(reversed(self.trades)) # Temporary measure
        holdings_balance = 0
        if holdings != {}:
            for symbol, information in holdings.items():
                for r in rev_trades:
                    if r['symbol'] == symbol:
                        p = self.latest_price
                        tots = p*information['amount']
                        self.shares[symbol] = tots
                        holdings_balance+=tots
                        break
        
        self.share_balance = holdings_balance
        self.total_balance = self.cash + self.share_balance
      
    def check_portfolio_strategy(self):
        # Check portfolio strategy for the user. Should get percentages
        
        pass
    
    def update_portfolio_percentages(self):
        self.general_pct = {
            'shares': 0,
            'cash': 0
        }
        self.general_pct['shares'] = round(self.share_balance / self.total_balance, 2)
        self.general_pct['cash'] = round(self.cash / self.total_balance, 2) 
        self.shares_pct = {
            
        }
        try:
            for sym in self.holdings:
                if self.share_balance is not 0:
                    self.shares_pct[sym] = ((self.shares[sym]/self.share_balance) * 100)
        except ZeroDivisionError:
            logger.opt(ansi=True).exception("You just divided by zero <r>[0, ZEEERO, 0z, _, ...,    ]</r> bro. It's all good though. Shit happens: ¯\_(ツ)_/¯")
            
                   
    def performance(self):
        # The data frame for the holdings. Set the index to timestamp
        df = pd.DataFrame(self.timed_holdings)
        tt = df['time']
        ts = pd.to_datetime(tt, unit='s')
        df = df.set_index(ts).resample('D').mean()
        df['returns'] = df['total'].pct_change()
        df['equity_curve'] = (1 + df['returns']).cumprod()
        self.equity = df
        return df
    
    
    def stats(self):
        total_return = self.equity['equity_curve'][-1]
        drawdown, duration = create_drawdowns(self.equity['equity_curve'])
        
        return [
            ('Total return', (total_return - 1) * 100),
            ('Sharpe ratio', create_sharpe_ratio(self.equity['returns'])),
            ('Max drawdown', drawdown * 100),
            ('Drawdown duration', duration)
        ]
    


    # def save(self):
    #     """Save should call explicitly"""
    #     current = self.equity.rename(index=str, columns={"time": "timestamp"}).fillna(0)
    #     port = current.to_dict("records")
    #     self.store.user_portfolio(1, port)
    #     self.shares_pct['timestamp'] = time.time()
    #     stats = self.stats()
        # Make sure to save the stats as well
        # Save the current portfolio with the most recent time. Can get the latest for the dashboard
        # Store all of the most recent trades with the time stamp as well
