import helpers

class Customer(object):
    def __init__(self, user_id, cash=10000):
        self.id = user_id
        self.symbols = []
        self.cash = cash

    def get_id(self):
        #returns the ID of this particular Customer

        return self.id

    def find_symbol(self, symbol):
        '''
        String -> Boolean
        returns boolean if symbol is already held by the customer
        '''
        if symbol in self.symbols:
            return True
        else:
            return False

    def add_symbol(self, symbol):
        ''' String -> None
        checks if symbol is already held by customer, 
        if symbol is not held, then it will be added to customer's list of stocks
        '''
        if not symbol in self.symbols:
            self.symbols.append(symbol)

        
    def deposit_money(self, cash):
        ''' float -> None
        allows a user to deposit cash. 
        
        '''
        self.cash = self.cash + cash
        return None

    def withdraw_cash(self, cash):
        '''float -> float
        allows user to use or withdraw cash
        cash balance is not allowed to be negative
        '''
        if self.cash - cash < 0:
            return None
        
        self.cash = self.cash - cash

        return None

    def get_balance(self):
        ''' None - > Float
        returns the balance of a given customer
        '''
        return self.cash

class Stock(object):
    def __init__(self, stock_symbol, cost, qty, timestamp=None):
        self.symbol = stock_symbol
        self.value = cost
        self.qty = qty
        self.time = timestamp
        
    
    

    def set_cost(self, cost):
        self.value = cost
        return self.value

    def get_cost(self):
        '''int -> int
        returns value of a given symbol's value
        '''
        stock_value = self.value
        return stock_value
    
    
    def get_qty(self):
        ''' int -> int
        returns quantity
        '''
        return self.qty

    def get_total_cost(self):
        ''' None -> Float
        returns the extended price of a stock
        '''
        
        return self.total_price

#probably not needed algorithm

'''
rows = [{'id': 1, 'symbol':"SPY", 'qty': 3 ,'cost': 40.00, 'Timestamp': '2020-01-01 13:01:55' },
            {'id': 3, 'symbol':"VONG", 'qty': 12 ,'cost': 250.00, 'Timestamp': '2020-02-04 13:01:55' }, 
            {'id': 1, 'symbol':"SPY", 'qty': 1 ,'cost': 50.00, 'Timestamp': '2020-02-05 13:01:55' },
            {'id': 2, 'symbol':"VOO", 'qty': 13 ,'cost': 200.00, 'Timestamp': '2020-03-05 13:01:55' }]
user_data = {}


for row in rows:
    if key_checker(row,row["symbol"]) == True:
        user_data[row['symbol']] = {
            'qty': user_data[row['symbol']]['qty'] + row['qty'],
            'cost': user_data[row['symbol']]['cost'] + row['cost']
        }
    else:
        user_data[row['symbol']] = {
            'qty': row['qty'],
            'cost': row['cost']
            }


    

    '''

'''user_data = {}
    
    for row in rows:
        try:
            if user_data[rows[0]["Symbol"]] in user_data:
                user_data[row[0]["Symbol"]["qty"]] += row[0]["Quantity"]
                user_data[row[0]["Symbol"]["costbasis"]] += row[0]["Price Ea"]
        except KeyError:
            {rows[0]["Symbol"]: {rows["Symbol"]["qty"] : rows[0]["Quantity"]}

            {user_data["Symbol"]["costbasis"] = row[0]["Price Ea"]}
            
    
    
    rows = [{'ID': 1, 'Symbol':"SPY", 'Quantity': 3 ,'Price ea': 40.00, 'Timestamp': '2020-01-01 13:01:55' }],
            [{'ID': 3, 'Symbol':"VONG", 'Quantity': 12 ,'Price ea': 250.00, 'Timestamp': '2020-02-04 13:01:55' }], 
            [{'ID': 1, 'Symbol':"SPY", 'Quantity': 1 ,'Price ea': 50.00, 'Timestamp': '2020-02-05 13:01:55' }],
            [{'ID': 2, 'Symbol':"VOO", 'Quantity': 13 ,'Price ea': 200.00, 'Timestamp': '2020-03-05 13:01:55' }]
    '''