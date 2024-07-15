import requests
from prettytable import PrettyTable


API_KEY = '7gxIXsUQGzNUBiQU2zcruvNjexlg2jum'
BASE_URL = 'https://www.alphavantage.co/query'

portfolio = []

def get_stock_price(symbol):
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': '1min',
        'apikey': API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    try:
        price = float(list(data['Time Series (1min)'].values())[0]['1. open'])
        return price
    except KeyError:
        return None

def search_stock_symbol(keyword):
    params = {
        'function': 'SYMBOL_SEARCH',
        'keywords': keyword,
        'apikey': API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    if 'bestMatches' in data:
        matches = data['bestMatches']
        return matches
    else:
        return None

def add_stock():
    while True:
        keyword = input("Enter stock symbol or keyword to search: ").upper()
        matches = search_stock_symbol(keyword)
        if not matches:
            print(f"Error: No matches found for '{keyword}'. Please enter a valid stock symbol or keyword.")
            continue

        print("Matching symbols found:")
        for match in matches:
            print(f"Symbol: {match['1. symbol']}, Name: {match['2. name']}")
        
        symbol = input("Enter the exact stock symbol from the list above: ").upper()
        if not any(match['1. symbol'] == symbol for match in matches):
            print(f"Error: Invalid stock symbol '{symbol}'. Please enter a valid stock symbol from the list above.")
            continue

        while True:
            try:
                quantity = int(input("Enter quantity: "))
                if quantity <= 0:
                    print(f"Error: Cannot add a non-positive quantity ({quantity}) of {symbol}.")
                else:
                    break
            except ValueError:
                print("Error: Quantity must be a positive integer. Please try again.")

        price = get_stock_price(symbol)
        if price is None:
            print(f"Error: Invalid stock symbol '{symbol}' or API limit reached.")
            continue

        for stock in portfolio:
            if stock['symbol'] == symbol:
                stock['quantity'] += quantity
                stock['initial_price'] = ((stock['initial_price'] * stock['quantity']) + (price * quantity)) / (stock['quantity'] + quantity)
                stock['initial_total_value'] = stock['quantity'] * stock['initial_price']
                stock['price'] = price
                stock['total_value'] = stock['quantity'] * price
                print(f"Added {quantity} more shares of {symbol} at ${price:.2f} each.")
                return
        
        stock = {
            'symbol': symbol,
            'quantity': quantity,
            'initial_price': price,
            'initial_total_value': quantity * price,
            'price': price,
            'total_value': quantity * price
        }
        portfolio.append(stock)
        print(f"Added {quantity} shares of {symbol} at ${price:.2f} each.")
        return

def remove_stock(symbol, quantity):
    if quantity <= 0:
        print(f"Error: Cannot remove a non-positive quantity ({quantity}) of {symbol}.")
        return

    global portfolio
    for stock in portfolio:
        if stock['symbol'] == symbol:
            if quantity > stock['quantity']:
                print(f"Error: Cannot remove more shares ({quantity}) than you own ({stock['quantity']}) of {symbol}.")
                return
            elif quantity == stock['quantity']:
                portfolio.remove(stock)
                print(f"Removed all shares of {symbol}.")
            else:
                stock['quantity'] -= quantity
                stock['total_value'] = stock['quantity'] * stock['price']
                stock['initial_total_value'] = stock['quantity'] * stock['initial_price']
                print(f"Removed {quantity} shares of {symbol}.")
            return
    print(f"No shares of {symbol} found in portfolio.")

def change_stock_price(symbol, new_price):
    if new_price <= 0:
        print(f"Error: Cannot set a non-positive price ({new_price}) for {symbol}.")
        return
    
    for stock in portfolio:
        if stock['symbol'] == symbol:
            stock['price'] = new_price
            stock['total_value'] = stock['quantity'] * stock['price']
            print(f"Changed price of {symbol} to ${new_price:.2f}.")
            return
    print(f"No shares of {symbol} found in portfolio.")

def view_portfolio():
    if not portfolio:
        print("Your portfolio is empty.")
        return
    
    table = PrettyTable()
    table.field_names = ["Stock", "Quantity", "Initial Price", "Current Price", "Initial Value", "Current Value", "Performance"]

    for stock in portfolio:
        performance = stock['total_value'] - stock['initial_total_value']
        performance_str = f"${performance:.2f} ({(performance / stock['initial_total_value']) * 100:.2f}%)"
        table.add_row([stock['symbol'], stock['quantity'], stock['initial_price'], stock['price'], stock['initial_total_value'], stock['total_value'], performance_str])
    
    print(table)

def main():
    while True:
        print("\nStock Portfolio Tracker")
        print("1. Add Stock")
        print("2. Remove Stock")
        print("3. Change Stock Price")
        print("4. View Portfolio")
        print("5. Exit")
        choice = input("Choose an option: ")
        
        if choice == '1':
            add_stock()
        elif choice == '2':
            symbol = input("Enter stock symbol to remove: ").upper()
            quantity = int(input("Enter quantity to remove: "))
            remove_stock(symbol, quantity)
        elif choice == '3':
            symbol = input("Enter stock symbol to change price: ").upper()
            new_price = float(input("Enter new price: "))
            change_stock_price(symbol, new_price)
        elif choice == '4':
            view_portfolio()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
