
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import string
import datetime
from datetime import datetime

from complements import error, login_required, live, lookup_matches,lookup_lineups


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///proyect.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    teams = []
    user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    user_str = str(user[0]['username'])
    user_cap = user_str.title()
    fav = db.execute("""
                     SELECT name FROM teams
                     JOIN favourites ON 
                     favourites.team_id = teams.id
                     WHERE(
                        favourites.users_id = ?
                     )""", session["user_id"])
    for row in fav:
        name = row['name']
        teams.append(name)

    return render_template("profile.html", teams=teams, user=user_cap)

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username:
            return error("Invalid username input")
        elif not password:
            return error("Invalid password input")

        rows = db.execute("SELECT * FROM  users WHERE username = ?", username)

        #ensuere username exist and password is correct
        if  len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return error("Invalid username and/or password")

        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template ("login.html")

@app.route("/logout")
def logout():
    session.clear()

    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not all([username, password, confirmation]):
            return error("Invalid input, please fulfill requirements")
        if db.execute("SELECT * FROM users WHERE username = ?", username) != []:
            return error("Invalid username, your username all ready taken")
        if password != confirmation:
            return error("password doesn't match")
        hash_password = generate_password_hash(password, method='pbkdf2', salt_length=16)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_password)
        row = db.execute("SELECT id FROM users WHERE username = ?", username)
        session["user_id"] = row[0]['id']
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/search", methods=["GET","POST"])
@login_required
def search():
    if request.method == "POST":
        team = request.form.get("team").lower()
        #query to optain team id and pass it to function
        team_id = db.execute("SELECT id FROM teams WHERE name = ?", team)
        if team_id != []: 
            matches = lookup_matches(team_id[0]['id'])
            if matches is not None:
                date_selected = None
                current_datetime = datetime.now()
                current_date = current_datetime.date()
                for match in matches:
                    date_str = match['date'] 
                    date_object = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z').date()
                    if current_date > date_object:
                        if date_selected is None or date_selected < date_object:
                            date_selected = date_object
                date_selected_str = date_selected.strftime("%Y-%m-%d")
                for match in matches:
                    if date_selected_str in match['date']:
                        fixture_id = match['id']
                lineups_teams = lookup_lineups(fixture_id)
                search_lineup = None
                if lineups_teams is not None:
                    team_cap= team.title()
                    for lineup in lineups_teams:
                        if team_cap == lineup[0]['name']:
                            search_lineup = lineup
                    return render_template("searched.html", team=team_cap, matches=matches, lineup=search_lineup)
                else:
                    return error("Unexpected error 502")
            else:
                return error("Unexpected error 503")
        else:
            return error("Enter a team from the 5 big leagues")
    else:
        return render_template("search.html")
    
@app.route("/searched", methods = ["GET","POST"])
@login_required
def searched():
    if request.method == "POST":
        team = request.form.get("team").lower()
        if not team:
            return error("500 Unexpected error")
        #add team in favourites user
        team_id = db.execute("SELECT id FROM teams WHERE name = ?", team)
        if not team_id:
            return error("Unexpected error. Confirm you have send the correct team 501")
        
        if db.execute("""SELECT * 
                      FROM favourites 
                      JOIN teams ON favourites.team_id = teams.id 
                      WHERE teams.name = ? 
                      AND favourites.users_id = ?""", team, session["user_id"]) == []:
            db.execute("INSERT INTO favourites(users_id, team_id) VALUES(?, ?)", session["user_id"], team_id[0]["id"])
        return redirect("/")
    else:
        return redirect("/search")

@app.route("/live")
@login_required
def matches():
    matches = live()
    fav = db.execute("""
                     SELECT name FROM teams
                     JOIN favourites ON 
                     favourites.team_id = teams.id
                     WHERE(
                        favourites.users_id = ?
                     )""", session["user_id"])
    teams = []
    for row in fav:
        name = row['name']
        teams.append(name)
    return render_template("live.html", matches=matches, teams=teams)
