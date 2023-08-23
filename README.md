# Finance Website

Hello, world!

In this project, I used Python's framework Flask, HTML, CSS, Bootstrap, and db sqlite3.

Working Principle: After successful registration, a symbolic 10.000$ is assigned to the user. Users can quote, buy and sell stocks by interacting with IEX (https://www.iexexchange.io/) API's. Additionally, users have the chance to see their portfolio, past transactions and are able to change their password.

Here are the features of each section:

<h2> Register </h2>

It is asked the user to provide a username and password in order to access the functionalities of the web application.
Password is stored in SQLite database with hash.

<h2> Login </h2>

Users can log in with their username and password.

<h2> Homepage </h2>

Users can see their current share(s), corresponding value, and cash balance.

<h2> Quote </h2>

Users can quote a valid stock by interacting with real data from IEX.

<h2> Buy </h2>

Users can buy a share(s) as long as they have sufficient funds.
After a successful transaction, the user is alerted and data is stored in the purchases table. 
Users can keep track of their transactions under history.

<h2> Sell </h2>

Users can sell share(s).
After a successful transaction, the user is alerted and data is stored in the purchases table as a negative value. 
Users can keep track of their transactions under history.

<h2> History </h2>

History keeps track of the user's transaction details such as date, amount, price, and symbol.

<h2> Settings </h2>

Users can update their password.
