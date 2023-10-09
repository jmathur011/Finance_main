# Finance
This application is designed to provide users with a simulated stock trading experience. Users can register, log in, view real-time stock prices, buy and sell stocks, and manage their portfolio.

#### Index Page
![Screenshot of a Index page](https://i.imgur.com/1zpDWIo.png)
#### History Page
![Screenshot of a Transactions History page](https://i.imgur.com/5DGyPs4.png)
#### History Page
![Screenshot of a Transactions Selling page](https://i.postimg.cc/FFbnP8ww/C-50-Finance-Buy-Google-Chrome-15-07-2023-19-14-24.png)

## Technologies

- Python
- Flask with session authentication
- SQL
- HTML/CSS
- Bootstrap
- APIs
- JavaScripts

## Summary

Finance is a web app that allows logged-in users to "buy" and "sell" stocks (with pretend money) as well as look up real stock quotes fetched from IEX API. Users can also view their stock portfolio transaction history.

## How to Run

1. Clone this repository, navigate to the project.
2. Activate a virtual environment: 'python3 -m venv .venv' then select the virtual environment as the active workspace.
3. Install dependencies: 'pip install -r requirements.txt'.
4. Run command 'export FLASK_APP=application.py' to set the Flask environment variable.
5. Configure and export your API key.
6. Run command 'flask run' to open on localhost.
7. When the finance site opens in your browser, register for a new account (upper right corner) to create your own stock portfolio
Views.

## Features
### Register

Allow a new user to register for an account, rendering an apology view if the form data is incomplete or if the username already exists in the database.

### Index

The homepage displays a table of the logged-in user's owned stocks, number of shares, current stock price, value of each holding. This view also shows the user's imaginary "cash" balance and the total of their "cash" plus stock value.

### Quote

Allows the user to submit a form to look up a stock's current price, retrieving real-time data from the IEX API. An error message is rendered if the stock symbol is invalid.

### Buy

Allows the user to "buy" stocks by submitting a form with the stock's symbol and number of shares. Checks to ensure the stock symbol is valid and the user can afford the purchase at the stock's current market price with their available balance, and stores the transaction history in the database.

### Sell

Allows the user to "sell" shares of any stock currently owned in their portfolio.

### History

Displays a table summarizing the user's past transactions (all buys and sells). Each row in the table lists whether the stock was bought or sold, the stock's symbol, the buy/sell price, the number of shares, and the transaction's date/time.

### Additional Changes

- Allows users to change their passwords.
- Allows users to add additional cash to their account.
- Allows users to buy more shares or sell shares of stocks.
- Requires users’ passwords to have some number of letters, numbers, and/or symbols.

## Usage
- Register a new account or log in with your existing credentials.
- Once logged in, you will be taken to the home page, where you can view your current portfolio, cash balance, and real-time stock data.
- To buy stocks, enter the symbol and the number of shares you wish to purchase on the Buy page.
- To sell stocks, enter the symbol and the number of shares you wish to sell on the Sell page.
- The Transaction History page displays all your buy and sell activities.
- Logout when you are done using the application.

## Contributing
Contributions are welcome! If you find any bugs or want to add new features, please create an issue or submit a pull request explaining the changes you propose.

## License
[MIT License](https://opensource.org/license/mit/)
