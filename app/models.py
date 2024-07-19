import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re
import requests
from urllib.parse import urlparse
from app import app
import math
from datetime import datetime, timedelta
from cachetools import cached, TTLCache
from functools import lru_cache

cache = TTLCache(maxsize=100, ttl=300) 

class Player:
    def __init__(self, player_id, nickname, avatar, country, games, faceit_url, position, faceit_elo):
        self.player_id = player_id
        self.nickname = nickname
        self.avatar = avatar
        self.position = position
        self.country = country
        self.games = games
        self.faceit_elo = faceit_elo
        self.faceit_url = faceit_url

    @staticmethod
    def from_dict(data):
        games = {key: value for key, value in data.get('games', {}).items() if key in ['csgo', 'cs2']}
        return Player(
            player_id=data.get('player_id'),
            nickname=data.get('nickname'),
            country=data.get('country'),
        )

    @staticmethod
    @lru_cache(maxsize=128)
    def get_global_ranking(region, limit=40, offset=0):
        api_key = app.config['FACEIT_API_KEY']
        headers = {'Authorization': f'Bearer {api_key}'}
        url = f'https://open.faceit.com/data/v4/rankings/games/cs2/regions/{region}?limit={limit}&offset={offset}'

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json().get('items', [])

            for player in data:
                position = player['position']
                if position == 1:
                    player['rank'] = '1'
                elif position == 2:
                    player['rank'] = '2'
                elif position == 3:
                    player['rank'] = '3'
                elif 4 <= position <= 9:
                    player['rank'] = '4-9'
                elif 10 <= position <= 1000:
                    player['rank'] = '9-1000'

            return data
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Failed to fetch global ranking for region {region}: {str(e)}")
            return []

    @staticmethod
    @lru_cache(maxsize=128)
    def get_global_eu_ranking(limit=100, offset=0):
        return Player.get_global_ranking('EU', limit, offset)

    @staticmethod
    @lru_cache(maxsize=128)
    def get_global_na_ranking(limit=100, offset=0):
        return Player.get_global_ranking('NA', limit, offset)

    @staticmethod
    @lru_cache(maxsize=128)
    def get_global_sa_ranking(limit=100, offset=0):
        return Player.get_global_ranking('SA', limit, offset)

    @lru_cache(maxsize=128)
    def get_global_sea_ranking(limit=100, offset=0):
        return Player.get_global_ranking('SEA', limit, offset)

    @lru_cache(maxsize=128)
    def get_global_oce_ranking(limit=100, offset=0):
        return Player.get_global_ranking('OCE', limit, offset)

def get_steam_vanity_url(url):
    """ Получение части URL SteamID из профиля Steam """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')
    return path_parts[-2]


def get_steam_profiles_url(url):
    """ Получение части URL SteamID из ванильного профиля Steam """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')
    return path_parts[-1]


def search_faceit_nickname(nickname):
    """ Поиск SteamID64 по никнейму на Faceit """
    url = f'https://open.faceit.com/data/v4/players?nickname={nickname}'
    headers = {'Authorization': f'Bearer {app.config['FACEIT_API_KEY']}'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        steam_id_64 = data.get('steam_id_64', '')
        return steam_id_64
    except requests.exceptions.RequestException as e:
        return f"{e}"


def get_steamid64_from_vanity_url(vanity_url):
    """ Поиск SteamID64 по ванильному URL Steam """
    url = 'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/'
    params = {'key': app.config['STEAM_API_KEY'], 'vanityurl': vanity_url}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data['response']['success'] == 1:
            return data['response']['steamid']
        else:
            return None
    except requests.exceptions.RequestException as e:
        return f"{e}"


def search_steamid(steamid):
    """ Поиск информации по SteamID64 """
    url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
    params = {'key': app.config['STEAM_API_KEY'], 'steamids': steamid}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        players = data.get('response', {}).get('players', [])
        if players:
            return players[0]['steamid']
        else:
            return None
    except requests.exceptions.RequestException as e:
        return f"error: {e}"


def search_player(search_value):
    """ Функция для поиска игрока по заданному значению """
    result = search_by_value(search_value)
    return result


def search_value(form_search_value):
    search_value = form_search_value
    steamid_64 = search_player(search_value)


def determine_input_type(search_value):
    """ Определение типа ввода (SteamID64, URL Steam или никнейм Faceit) """
    if re.match(r'^\d{17}$', search_value):
        return 'steamid64'
    elif re.match(r'^https?://steamcommunity\.com/id/[a-zA-Z0-9_-]+/?$', search_value):
        return 'steam_url'
    elif re.match(r'^https?://steamcommunity\.com/profiles/[a-zA-Z0-9_-]+/?$', search_value):
        return 'ez_steamid64'
    else:
        return 'faceit_nickname'


def search_by_value(search_value):
    """ Поиск по заданному значению (SteamID64, URL Steam или никнейм Faceit) """
    input_type = determine_input_type(search_value)
    if input_type == 'ez_steamid64':
        return get_steam_profiles_url(search_value)
    if input_type == 'steamid64':
        return search_steamid(search_value)
    elif input_type == 'steam_url':
        vanity_url = get_steam_vanity_url(search_value)
        steamid64 = get_steamid64_from_vanity_url(vanity_url)
        if steamid64:
            return search_steamid(steamid64)
    elif input_type == 'faceit_nickname':
        return search_faceit_nickname(search_value)


def search_by_steamid_64(search_value):
    steamid_64 = search_player(search_value)  
    api_key = app.config['FACEIT_API_KEY']
    headers = {'Authorization': f'Bearer {api_key}'}
    get_player_info_url = f'https://open.faceit.com/data/v4/players?game=cs2&game_player_id={steamid_64}'

    try:
        player_info_response = requests.get(get_player_info_url, headers=headers)
        player_info_response.raise_for_status()
        player_info_data = player_info_response.json()

        if 'player_id' in player_info_data and 'nickname' in player_info_data:
            player_id = player_info_data['player_id']
            country = player_info_data['country']
            region = player_info_data['games']['cs2']['region']

            get_global_player_rank_url = f'https://open.faceit.com/data/v4/rankings/games/cs2/regions/{region}/players/{player_id}'
            player_global_rank_response = requests.get(get_global_player_rank_url, headers=headers)
            player_global_rank_response.raise_for_status()
            player_global_rank_data = player_global_rank_response.json()
            player_global_rank = next(
                (item['position'] for item in player_global_rank_data['items'] if item['player_id'] == player_id), 
                None
            )
            player_country_rank_url = f'https://open.faceit.com/data/v4/rankings/games/cs2/regions/{region}/players/{player_id}?country={country}'
            player_country_rank_response = requests.get(player_country_rank_url, headers=headers)
            player_country_rank_response.raise_for_status()
            player_country_rank_data = player_country_rank_response.json()
            player_country_rank = next(
                (item['position'] for item in player_country_rank_data['items'] if item['player_id'] == player_id), 
                None
            )

            return player_info_data, player_id, player_info_data['nickname'], player_global_rank, player_country_rank
        else:
            return None, None, None, None, None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching player info: {e}")
        return None, None, None, None, None


def get_player_stats(player_id, limit=100):
    api_key = app.config['FACEIT_API_KEY']
    headers = {'Authorization': f'Bearer {api_key}'}
    get_player_stats_url = f'https://open.faceit.com/data/v4/players/{player_id}/games/cs2/stats'
    get_full_player_stats_url = f'https://open.faceit.com/data/v4/players/{player_id}/stats/cs2'

    try:
        params = {'limit': limit}
        player_stats_response = requests.get(get_player_stats_url, headers=headers, params=params)
        player_stats_response.raise_for_status()
        player_stats_data = player_stats_response.json()

        if limit > 100:
            params['offset'] = 100
            additional_stats_response = requests.get(get_player_stats_url, headers=headers, params=params)
            additional_stats_response.raise_for_status()
            additional_stats_data = additional_stats_response.json()
            player_stats_data['items'].extend(additional_stats_data['items'])

        full_player_stats_response = requests.get(get_full_player_stats_url, headers=headers)
        full_player_stats_response.raise_for_status()
        full_player_stats_data = full_player_stats_response.json()

        return player_stats_data, full_player_stats_data
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching player stats: {e}")
        return None, None


def format_date(date_string):
    try:
        date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S%z")
        formatted_date = date_obj.strftime("%b %d, %Y")
        return formatted_date
    except ValueError:
        return "Invalid Date Format"


def format_time_since(datetime_string):
    try:
        updated_at = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        current_time = datetime.utcnow()
        time_difference = current_time - updated_at

        if time_difference.days > 7:
            formatted_date = updated_at.strftime("%d %b %Y - %H:%M")
        elif time_difference.days > 1:
            formatted_date = f"{time_difference.days} days ago"
        elif time_difference.days == 1:
            formatted_date = "1 day ago"
        elif time_difference.seconds >= 3600:
            hours = time_difference.seconds // 3600
            formatted_date = f"{hours} hours ago"
        elif time_difference.seconds >= 60:
            minutes = time_difference.seconds // 60
            formatted_date = f"{minutes} minutes ago"
        else:
            formatted_date = "just now"

        return formatted_date
    except ValueError:
        return "Invalid Date"



def calculate_averages(player_stats_data, num_matches, start_index=0):
    if not player_stats_data or 'items' not in player_stats_data:
        return None
    
    matches = player_stats_data['items'][start_index:start_index + num_matches]
    if not matches:
        return None

    total_kills = sum(int(match['stats']['Kills']) for match in matches) / num_matches
    total_assists = sum(float(match['stats']['Assists']) for match in matches) / num_matches
    total_deaths = sum(float(match['stats']['Deaths']) for match in matches) / num_matches
    total_kr_ratio = sum(float(match['stats']['K/R Ratio']) for match in matches) / num_matches
    total_kd_ratio = sum(float(match['stats']['K/D Ratio']) for match in matches) / num_matches
    total_hs_percentage = sum(float(match['stats']['Headshots %'].strip('%')) for match in matches) / num_matches

    avg_kills = math.ceil(total_kills) if num_matches > 0 else 0
    avg_assists = math.ceil(total_assists) if num_matches > 0 else 0
    avg_deaths = math.ceil(total_deaths) if num_matches > 0 else 0
    avg_kr_ratio = total_kr_ratio if num_matches > 0 else 0
    avg_kd_ratio = total_kd_ratio if num_matches > 0 else 0
    avg_hs_percentage = math.ceil(total_hs_percentage) if num_matches > 0 else 0

    return {
        'avg_kills': avg_kills,
        'avg_assists': avg_assists,
        'avg_deaths': avg_deaths,
        'avg_kr_ratio': avg_kr_ratio,
        'avg_kd_ratio': avg_kd_ratio,
        'avg_hs_procent': avg_hs_percentage,
    }


def calculate_cs2_statistics(player_stats):
    total_matches = 0
    total_kills = 0
    total_deaths = 0
    total_wins = 0
    total_matches_played = 0
    total_headshots = 0
    num_maps = 0
    map_labels = set(["Anubis", "Mirage", "Ancient", "Nuke", "Dust2", "Vertigo", "Overpass", "Inferno"])
    
    for segment in player_stats["segments"]:
        if segment.get("mode") == "5v5" and segment.get("label") in map_labels:
            num_maps += 1
            total_matches += int(segment["stats"]["Matches"])
            total_kills += int(segment["stats"]["Kills"])
            total_deaths += int(segment["stats"]["Deaths"])
            total_wins += int(segment["stats"]["Wins"])
            total_matches_played += int(segment["stats"]["Matches"])
            total_headshots += int(segment["stats"]["Headshots"])
    
    average_kd_ratio = total_kills / total_deaths if num_maps > 0 else 0
    win_rate_percentage = (total_wins / total_matches_played) * 100 if total_matches_played > 0 else 0
    average_headshots_percentage = (total_headshots / total_kills) * 100 if num_maps > 0 else 0
    
    return {
        "Matches": total_matches,
        "Average K/D Ratio": math.ceil(average_kd_ratio * 100) / 100,
        "Win Rate %": math.ceil(win_rate_percentage),
        "Average Headshots %": math.ceil(average_headshots_percentage)
    }