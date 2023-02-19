# CS50 Finance

Hello, world!

This is my CS50 Finance project that I completed by re-implementing https://finance.cs50.net/login.

In this project, I used Python's framework Flask, HTML, CSS, Bootstrap and for db sqlite3. I implemented this project by using Harvard's CS50 X course. 

Working Principle: After succesful registration, symbolic 10.000$ is assigned to the user. 
By interacting with IEX (https://www.iexexchange.io/) API's, user can quote, buy and sell stocks.
Additionally, user have the chance to see their portfollio, past transactions and able to change their password.

Here comes the features of each section:

<h2> Register </h2>

It is asked user to provide a username and password in order to access the functionalities of the web application.
Password is stored in sqlite database with hash.

<h2> Login </h2>

User logins with their username and password.

<h2> Homepage </h2>

User have the ability to see their current share(s), corresponding value and their cash balance.

<h2> Quote </h2>

User can quote a valid stock by interacting real data from IEX.

<h2> Buy </h2>

User can buy share(s) as long as they have the sufficent funds.
After succesfull transaction, user is alerted and data is stored in purchases table. 
User have the ability to keep track of their transaction under history.

<h2> Sell </h2>

User can sell share(s).
After succesfull transaction, user is alerted and data is stored in purchases table as a negative value. 
User have the ability to keep track of their transaction under history.

<h2> History </h2>

History keeps track of users transaction details such as date, amount, price and symbol.

<h2> Settings </h2>

User have the ability to update their password.
