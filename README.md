# Stock Exchange #
## Stock Exchange Web Application ##

This is a full-stack implementation of a stock exchange application, using stock data from the IEX API. The application has four major functions: Quote, Buy, Sell, and History to allow the user to look up stock prices, buy stocks, sell stocks, and track their transaction history. This application uses HTML, CSS, and JavaScript for the front-end development of the web app, Flask and Python to communicate across servors, and SQLite to maintain a database of stocks and user data.

## Components ##
### application.py ###
This is the main file of the program that uses the Flask framework written in Python. This Python program makes all the function calls for the various functions of the application, checks for the validity of form inputs, and updates the database with new user data and transactions. This 
### finance.db ###
This database file contanins three tables for this application. The "users" table contains user log in information, including their user id, username, and hashed password. The "transactions" table records the user's buying and selling actions with their corresponding timestamps, organized by the user id. And the "holdings" table keeps track of the user's current stock holdings, also organized by user id. The tables in this database are updated through SQLite queries which are made by the Flask-Python program. 
### layout.html ###
This HTML file includes a template for all the webpages of the application. It contains all the general web information, references to the CSS files, and JavaScript functions as well.
### templates ###
This directory contains all of the HTML files used by the program. Each function of the program has an HTML file dedicated to it which extends layout.html, specifies the title of the page, and implements the main functionality of the page.
### styles.css ###
This file contains all of the CSS information for the application.

## Program Walk Through ##

### Register and Log In ###
A new user is required to register in the application, providing a username and password. Both are checked for authenticity and uniqueness, and the password is hashed before being stored in the database. The user's information is then stored in the database in the "users" table. Once the user is registered, they may log in to the application using their username and password. Both of these functions are implemented through an HTML form to collect the data from the user. The user is also able to log out of the application as well.

### Home Page ###
Then, the user is taken to the home page of the applicaiton, where their current stock holdings are displayed in an HTML table. New users will only have a default CASH value of $10,000.00, but returning users will have their shares (if any) displayed here as well. This page is implemented in HTML as well and contains a couple JavaScript applications as well. First, this page as well as the others display the time and date information at the bottom of the screen using JavaScript's Date Reference, and updating this value every milisecond. This home page also contains a "Stock Exchange Tip" generator which generates a random stock exchange tip from a list of tips, using the Math.random() function. 

### Quote ###
This is the first function for the user to view stock data. Through an HTML form, the user is asked for a stock symbol. Once the code is entered, the program checks for its validity and quotes the stock symbol, company name, and price at the moment using the IEX API. If the symbol is invalid, the program displays an apology message.

### Buy ###
The buy function asks the user for the stock symbol and the number of shares they would like to buy through an HTML form. The program checks for a valid symbol and number of shares, displaying an apology message if necessary. The program updates the user's CASH value in the "users" table in the database, as well as updating the "transactions" and "holdings" tables in the database. The user is then redirected to the home page of the application, where their newly-bought shares are displayed.

### Sell ###
The sell function asks the user for a stock symbol, in a drop-down menu containing the user's current stock holdings, and the number of shares to be sold. After checking the validity of the symbol and number of shares and displaying an apology message if necessary, the program updates the user's CASH value in the "users" table, by adding the stock's current price. The "transactions" and "holdings" tables in the database are also updated to incorporate this new selling request. Finally, the user is redirected to the home page, and this new transaction is displayed.

### History ###
This function displays the history of all the user's transactions in the form of an HTML table. The transactions are ordered chronologically based on the timestamp of the transaction and display all of the stock information as well as the price of the stock at the time of the transaction.

## Conclusion ##
All in all, this stock exchange implementation is a full-stack web application constructed using HTML, CSS, JavaScript, Flask-Python, and SQLite. The program allows users to perform various stock exchange functions including Quote, Buy, Sell, and History. At the end of the day, this program is a fun and easy way for people to play around with stocks, without losing any real money :)
