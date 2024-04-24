# OnlyFootball
#### Video Demo:  <URL HERE>
#### Description: A place for Only football fans. Search your favourite team future, and past matches, as well as The live matches of the moment. 
The code created is for a webpage wich objective is to be a space to search for football information, such as the games that are live in the moment, your favourite team past matches, some of the future matches and the players that are currently playing.

This code is divided in several files such as the proyect.db that is the data base of the proyect; the app.py file, wich have the routes of the proyect; the complements.py file, wich handles all the api request and complement functions for the prpgram to run, the styles.css that renders the desing for the web page and the templates that where the user interacts with the data and the program. 

The program uses an API call API-football [documentation](https://www.api-football.com/documentation-v3)

## Proyect.db:
proyect.db is the database of the proyect written in sqlite3. It stores 3 tables. First of all is the users table wich i created for have more interaction with users, use cookies and a personalize experience; this table store the id primary key that autoincrement, the usersname and the hash that is the password hashed. The second table is the teams table wich is a table that i created, wich purpose is to store the id from the football teams and the name. The second table was designed thinking about the users usage because the API is access mostly with the team_id that they store, so for that my first goal was to store all the teams for the 5 principal leagues of the world in my database(this process is explained in complements.py). And finally the third table is favourites and storethe id primary key that autoincrements and two foreign keys that are users_id and teams_id; the objective of this table is to store the favourite teams of each user.

## Complements.py:
The complements.py file is a file created to handle all the API query information, as well as some other functiones such as "error" "login_required", "store" that were necesary for the function of the hole code.  Libraries used: Flask, jinja, requests and cs50
### Store:
the score function was created to populate the sql table "teams". This function was used only one time and it should be used only once in a year. This function first stores in a list the id from the five big leagues(sorry for the hardcode but was the most efficient way) "la liga", "serie A", "Premier league", "Bundesliga" and the "ligue 1". After that is a variable call processed_data wich value is a empty dictionary that is going to be populated after. Then there is a loop that goes all through the leagues list for query all the teams from each league; for that there is the API request 
```python
url = (f"https://v3.football.api-sports.io/teams?league={league}&season=2023")
        payload={}
        headers = {
        'x-rapidapi-key': 'a8c3c2b4b4ff527471c829ddf29258e3',
        'x-rapidapi-host': 'v3.football.api-sports.io'
        }
```

After the API request there are the blocks for 'try' and 'except' wich main reason is to try the code exept if the API request or json fails. In the try block is all the handle response and 'raise.for.status' to make sure all is good. Then I make the response a list of dictionaries with json. After that i need to scope the data because there is more information besides response and finally there is the for loop to select the id from each team, select the name of the team and make it to lower for better usage and case insensitive during the hole program. Finally there are the except blocks with there own error types.

Finaly the last part is the sql query to update the teams data base usign the CS50 library.

### Error:
This is a function just created to render a template wich the input is a message used in the main functions and send the message to the template when the user makes an error, if that template fails for any reason there is an unexpected error template.

### Login_required:
This function was taken from CS50 problem set finance and is used as a complement to make some routes avaliable only to users wich are login.

### Lookup_matches
Lookup_matches function recieves as an imput the team_id that is render by other function. The first part is similar to the store function and query the API. 

Then the try block checks for the answer and response, scope the data, and sets a empty list call teams_data. After this, we use a for loop to first retieve the values from the response of the name of the home team, the away team, the goal from the teams, the date of the match, the id of the match and the winner value that is a boolean expresion. After that we append this data as a dictionary wich keys are the ones metion above and the values. After doing that for each match in the response from the API we create a empty list call reversed data, so on, we make a loop to reverse the data optained and append it to reversed data. This is because if we didn't reverse the user will see as a first match the first match of the team in the season, so we make this to create a LIFO(Last in, first out) structure.

### live
this function is the same as the matches function, it just change the API endpoind and the way it store the data.

### Lookup_lineups
The top of the function and the first part of the try block is the same as the lookup_matches function, it just change the endpoint.

In this function what changes is that we have to list that are home_team and away_team aswell as i variable whose value is 0. After this we created a loop divided in two parts:

The outside loop is going to loop to store the team name, the formation and all the players data in 3 variables. After that we are going to set an empty list that is going to be populated in the inner loop but is going to be empty each time the loop runs. After that there are the conditionals. When 'i == 0' is going to append all the information of the first team in the home list, and after appending is going to add 1 to i, so for the next time is going to store all the information in the away teams list

The inner loop is going select for all the players of a team, the player name, the grid and the number for appending it to the players_ls variable that is going to be appendet in the conditionals to one of the other lists as a dictionary

## App.py 
This is the main file of the backend in wich is run the program. The functions here runs all the routes from flask. The used libraries are: cs50 for sql commands; flask for the routes functions and session; werkzeug.security for the security commands of the password; datetime for make datetime objects and complements.py. 

### route("/")
This route is the homepage of the user. First we create a variable teams and set it equal to a list, after we make the sql query to have the username, and after that we make some adjustments to the user object, first to an str and then as an str we set it the title attibute to capitalize the first letters of the users name. 

Then we set the variable "fav" equal to the favourite teams of the user using another sql query and with a loop we append the name to the teams list.

### ("/login")
In this route we have two methods 'GET' and 'POST'. First clear all the last sessions and if the method is post we request from the template username and password, then some conditionals to check that the user at least post both. Then we set the variable rows = to all where the username is the one that the user inputs. After that we cheack first that the the username exist and it password is correck, finally we set the session id to the user id. If 'GET' we render the login template

### logout
Clear the session and redirect to the homepage, than then will redirect to the login. 

### register
Register have two methods. If 'POST': gets username, password and confirmation from the template, checks if the 3 were send, then checks if the username is avaliable and check if the password is equal to the confirmation. After it hashes the password with the generate_password_hash function, and insert it to the database; and then start the session with the users id. If 'GET': renders the register template

### Search:
If request method is 'POST': gets team searched from the search template and gives the attribute lower to the hole string, this is the method selected to standarize all the data. After that we search into the database the teams id, check if the team exists in the database else, return error; after we use the 'lookup_matches' function to store all the matches of that team, then check that matches have a value in case something goes wrong, after we create a variable call date_selected and set it equal to None, current_datetime that is the date in wich the user makes the search and after that we need to set that variable to a date type object for making the comparisons thereafter. After we search into the matches with a loop to see wich was the last match played, thats why we use the current_data variable and we set date_selected to the date of the last match played. Then as we were comparing date objects, we need to set the time equal to a str to compared after in a loop and select in the matches list the id of the match with that date. Then, we check using the 'lookup_lineups' function the lineup of the team that last match. As that function returns both teams we select and store the lineup of the team searched, Then we render the name of the team, the matches and the lineup.

If 'GET': renders the search template

### Searched
If 'POST' select the team from the searched templated, select the id of the team if the team is correct, then check if the user already add that team as a favourite, in case it doesen't add it as favourite and redirect to the homepage

If 'GET': renders the searched template

### Live:
This routes execute the live function from the complements.py file and store the return value, also search the favourite teams of the user and return the templates with both information

## Templates:

### layout:
This template as the name say is the layout template for the rest. In this template's head first we set some meta types for the contend, after, we import bootstrap for the style usage and the styles.css file.

then in the body we set the bootstrap theme dark and create the navbar for the user interaction with diferent routes. This navbar is created with some containers for bootstrap animation, and the span for decoration and that renders to the homepage. Then the child divition is specific for the routes that is an unordered list if the there is set up the cookies, it case they arent, the navbar only shows the register and login routes. This conditionals were make usign jinja. 

After there is the main of the body by wich using jinja we create the blocks in wich are going to go the templates. 

In the footer is a validator for the web that was used during to proccess to allways check the HTML code. Also there is the API script. 

### login:
All the blocks start the same, first with the jinja template extending the layout, then with the block title with the tittle of the page and the main block in wich goes the html code. In this template we have the form with wtho divitions for each imput and the button , all styled with bootstrap as a stylistc choise.

### error:
Is have a header with a type jinaja palceholder that is render by the function of error. Then we make a class with the custom danger from bootstrap and some paragraphs tags with the message.

### unexpected:
Is the same as error but in case that something went wrong with the other template render

### register:
This template have a title with the registration template, the form and the 3 divitions for the inputs, the name, the password and the confirmation 

### Profile:
It has a tittle with a jinja placeholder for the name, a paragraph for a messaje and if the user is following any team, it shows as a unorder list and with a jinja "for loop" a form with a button with the name of each team, so when the user clicks the button automaticaly is redirected to the searched route with the name of the team. 

if not follow teams appers a messaje. 

### Search:
this templates has the tittle and a form for the user to enter the team that want to search. 

### Searched:
Searched templated was the most complicated to make. I started making the template like a table that only shows the teams games and resoults, but then i also wanted to add the names of the players, but when i make it it goes like disorganized. After that I learned how to use the tool of flexbox, to customize the space and use it better. But then after using flexbox the table started to correct the design and all was not behaving like it should, so i see that flexbox combine better with divitons that are the ones used to the matches. For this we have a container div, with the first child content-area1. With a jinja tempate for each match i make a diferent div, with child divs that are a span with the dates, teams names and goals. 

Then after the end of the forloop, is the content-area2 wich display each player a divition.

### live:
This tempalte uses the same idea as the searched template with the table matches if there are matches in the current moment, if there are not matches, there would render the favourite teams of the user if the user has favourite teams, else would invite the user to add teams searching their favourites by a hiperlink. 

## styles.css:
Styles.css have the design of the web page.
```css
nav .navbar-brand
{
    font-size: xx-large;
}

/* Colors for brand */
nav .navbar-brand .white
{
    color: #fff;
    text-shadow: 0.08em 0.08em 0.08em #000;
    font-size: xx-large;
}
nav .navbar-brand .green
{
    color: #2e944b;
    font-size: xx-large;
    text-shadow: 0.08em 0.08em 0.08em #000;
}
```
This code is mainly to give the style to the navbar, Then the '@media' is for adjust the size to small devises

After '.container' and the following classes are for style of the flexbox. '.match-detailes' Give the table style to each of the matches data and the rest of the code is just color stle of the page and the font size.  




