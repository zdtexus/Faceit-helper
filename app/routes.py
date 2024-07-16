from flask import render_template, request, redirect, url_for, jsonify
from requests.exceptions import HTTPError
from app import app
from app.models import Player, search_by_steamid_64, get_player_stats, format_date, calculate_averages, calculate_cs2_statistics, format_time_since

class PlayerView:
    def __init__(self):
        self.error_message = None
        self.global_rankings = {
            'EU': [],
            'NA': [],
            'SA': []
        }
    
    def load_rankings(self):
        try:
            self.global_rankings['EU'] = Player.get_global_eu_ranking(limit=100, offset=0)
            self.global_rankings['NA'] = Player.get_global_na_ranking(limit=100, offset=0)
            self.global_rankings['SA'] = Player.get_global_sa_ranking(limit=100, offset=0)
        except Exception as e:
            self.error_message = f"Ошибка при загрузке топ игроков: {str(e)}"

    def render_index(self):
        return render_template('index.html', error_message=self.error_message,
                               global_eu_ranking=self.global_rankings['EU'],
                               global_na_ranking=self.global_rankings['NA'],
                               global_sa_ranking=self.global_rankings['SA'])

    def handle_search(self, search_value):
        try:
            player_info_data, player_id, nickname, player_global_rank, player_country_rank = search_by_steamid_64(search_value)
            if not player_id or not nickname:
                self.error_message = f"Игрок '{search_value}' не найден."
            else:
                return redirect(url_for('player_stats', nickname=nickname))
        except HTTPError as e:
            if e.response.status_code == 404:
                self.error_message = f"Ошибка при поиске игрока '{search_value}': игрок не найден."
    
    def get_rankings(self, region, limit=100, offset=0):
        rankings_methods = {
            'EU': Player.get_global_eu_ranking,
            'NA': Player.get_global_na_ranking,
            'SA': Player.get_global_sa_ranking
        }
        return rankings_methods.get(region, lambda x, y: [])(limit, offset)

player_view = PlayerView()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_value = request.form.get('search_value')
        response = player_view.handle_search(search_value)
        if response:
            return response
    
    player_view.load_rankings()
    return player_view.render_index()

@app.route('/load_more_rankings')
def load_more_rankings():
    region = request.args.get('region', 'EU')
    limit = 100
    offset = int(request.args.get('offset', 0))
    rankings = player_view.get_rankings(region, limit, offset)
    return jsonify(rankings)

class PlayerStatsView:
    def __init__(self):
        self.error_message = None
    
    def get_player_data(self, nickname):
        try:
            player_info_data, player_id, nickname, player_global_rank, player_country_rank = search_by_steamid_64(nickname)
            if player_id:
                player_stats_data, full_player_stats_data = get_player_stats(player_id, limit=200)
                if player_stats_data and full_player_stats_data:
                    return player_info_data, player_stats_data, full_player_stats_data, player_global_rank, player_country_rank
        except HTTPError as e:
            if e.response.status_code == 404:
                self.error_message = f"Ошибка при поиске игрока '{nickname}': игрок не найден."
            else:
                self.error_message = f"Ошибка при получении информации об игроке '{nickname}': {str(e)}"
        except Exception as e:
            self.error_message = f"Ошибка при получении информации об игроке '{nickname}': {str(e)}"
        return None, None, None, None, None

    def render_player_stats(self, nickname, player_info_data, player_stats_data, full_player_stats_data, player_global_rank, player_country_rank):
        formatted_activated_at = format_date(player_info_data['activated_at'])
        player_global_rank_formatted = "{:,}".format(player_global_rank) if player_global_rank is not None else None
        player_country_rank_formatted = "{:,}".format(player_country_rank) if player_country_rank is not None else None
        skill_level = str(player_info_data['games']['cs2']['skill_level']) if 'games' in player_info_data and 'cs2' in player_info_data['games'] and 'skill_level' in player_info_data['games']['cs2'] else None
        recent_results = full_player_stats_data['lifetime']['Recent Results']
        averages_last_20 = calculate_averages(player_stats_data, 20)
        averages_prev_20 = calculate_averages(player_stats_data, 20, start_index=20)
        averages_last_50 = calculate_averages(player_stats_data, 50)
        averages_prev_50 = calculate_averages(player_stats_data, 50, start_index=50)
        averages_last_100 = calculate_averages(player_stats_data, 100)
        averages_prev_100 = calculate_averages(player_stats_data, 100, start_index=100)
        main_statistics = calculate_cs2_statistics(full_player_stats_data)
        relevant_maps = ['Mirage', 'Anubis', 'Dust2', 'Vertigo', 'Ancient', 'Nuke', 'Overpass', 'Inferno']
        filtered_segments = [segment for segment in full_player_stats_data['segments'] if segment['mode'] == '5v5' and segment['label'] in relevant_maps]
        filtered_segments.sort(key=lambda x: relevant_maps.index(x['label']))

        return render_template('player_stats.html', nickname=nickname, player_stats_data=player_stats_data,
                               player_info_data=player_info_data, full_player_stats_data=full_player_stats_data,
                               player_global_rank=player_global_rank_formatted,
                               player_country_rank=player_country_rank_formatted, formatted_activated_at=formatted_activated_at,
                               recent_results=recent_results, skill_level=skill_level,
                               averages_last_20=averages_last_20,
                               averages_prev_20=averages_prev_20,
                               averages_last_50=averages_last_50,
                               averages_prev_50=averages_prev_50,
                               averages_last_100=averages_last_100,
                               averages_prev_100=averages_prev_100,
                               main_statistics=main_statistics,
                               format_time_since=format_time_since,
                               filtered_segments=filtered_segments)

player_stats_view = PlayerStatsView()

@app.route('/<nickname>')
def player_stats(nickname):
    player_info_data, player_stats_data, full_player_stats_data, player_global_rank, player_country_rank = player_stats_view.get_player_data(nickname)
    if player_info_data:
        return player_stats_view.render_player_stats(nickname, player_info_data, player_stats_data, full_player_stats_data, player_global_rank, player_country_rank)
    
    player_view.load_rankings()
    return render_template('index.html', error_message=player_stats_view.error_message,
                           global_eu_ranking=player_view.global_rankings['EU'],
                           global_na_ranking=player_view.global_rankings['NA'],
                           global_sa_ranking=player_view.global_rankings['SA'])
