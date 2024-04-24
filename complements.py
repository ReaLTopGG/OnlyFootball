import re
from flask import redirect, render_template, session
from functools import wraps
from jinja2 import TemplateNotFound
import requests
from cs50 import SQL
import json

db = SQL("sqlite:///proyect.db")

def error(message, code=404):
    try:
        return render_template("error.html", type=code, message=message)
    except TemplateNotFound:
        return render_template("unexpected.html", message="An unexpected error occurred", type=505)
    
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def lookup_matches(team_id):
    url = (f"https://v3.football.api-sports.io/fixtures?team={team_id}&season=2023")
    payload={}
    headers = {
    'x-rapidapi-key': 'a8c3c2b4b4ff527471c829ddf29258e3',
    'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()
        scope_data = data ["response"]
        teams_data =[]
        for dictionary in scope_data:
            home = dictionary["teams"]["home"]["name"]
            away = dictionary["teams"]["away"]["name"]
            h_goals = dictionary["goals"]["home"]
            a_goals = dictionary["goals"]["away"]
            date = dictionary["fixture"]["date"]
            id = dictionary["fixture"]["id"]
            home_winner = dictionary["teams"]["home"]["winner"]
            away_winner = dictionary["teams"]["away"]["winner"]
            teams_data.append({
                "id": id,
                "home": home,
                "away": away,
                "h_goals": h_goals,
                "a_goals": a_goals,
                "date":date,
                "home_winner": home_winner,
                "away_winner": away_winner
            })
        reversed_data =[]
        for team in reversed(teams_data):
            reversed_data.append(team)
        return reversed_data
    
    except requests.exceptions.HTTPError as err:
      print(f"API request failed: {err}")
      return None  
    except (KeyError, IndexError, requests.RequestException, ValueError, ):
        return None

    
def live():
    url = "https://v3.football.api-sports.io/fixtures?live=all"

    payload={}
    headers = {
    'x-rapidapi-key': 'a8c3c2b4b4ff527471c829ddf29258e3',
    'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()
        scope_data = data["response"]
        processed_data = []
        for match in scope_data:
            home_team = match['teams']['home']['name']
            away_team = match['teams']['away']['name']
            date = match['fixture']['date']
            home_score = match["goals"]["home"]
            away_score = match["goals"]["away"]
            processed_data.append({
                "home_team": home_team,
                "away_team": away_team,
                "date": date,
                "home_score": home_score,
                "away_score": away_score
            })
        return processed_data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def lookup_lineups(match_id):
    url = (f"https://v3.football.api-sports.io/fixtures/lineups?fixture={match_id}")
    payload={}
    headers = {
    'x-rapidapi-key': 'a8c3c2b4b4ff527471c829ddf29258e3',
    'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()
        scope_data = data['response']
        home_team_data = []
        away_team_data = []
        i = 0
        for team in scope_data:
            team_name = team['team']['name']
            formation = team['formation']
            players = team['startXI']
            players_ls=[]
            for player in players:
                player_name = player['player']['name']
                grid = player['player']['grid']
                number = player['player']['number']
                players_ls.append({
                    "name": player_name,
                    "grid": grid,
                    "number": number
                })
            if i == 0:
                home_team_data.append({
                    "name": team_name,
                    "formation": formation,
                    "players": players_ls
                })
                i += 1
            else: 
                away_team_data.append({
                    "name": team_name,
                    "formation": formation,
                    "players": players_ls
                })
        return(home_team_data, away_team_data)
    except requests.exceptions.HTTPError as err:
      print(f"API request failed: {err}")
      return None  
    except (KeyError, IndexError, requests.RequestException, ValueError, ):
        return None

def store():
    leagues =[39,78, 135, 140, 61]
    processed_data= []
    for league in leagues:
        url = (f"https://v3.football.api-sports.io/teams?league={league}&season=2023")
        payload={}
        headers = {
        'x-rapidapi-key': 'a8c3c2b4b4ff527471c829ddf29258e3',
        'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()
            scope = data ["response"]
            for team in scope:
                id = team["team"]["id"]
                name = team["team"]["name"].lower()
                processed_data.append({
                    "id":id,
                    "name":name,
                })
        except requests.exceptions.HTTPError as err:
            print(f"API request failed: {err}")
            return None
        except (KeyError, IndexError, requests.RequestException, ValueError, ):
            return None
    for dictionary in processed_data:
        db.execute("""
                   UPDATE teams 
                   SET name = ? 
                   WHERE ID = ? """, dictionary["name"],  dictionary["id"])

    