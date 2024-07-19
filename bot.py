from typing import Final
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from app.models import Player, get_player_stats, search_by_steamid_64, format_date, calculate_averages, calculate_cs2_statistics
from app import app

TOKEN: Final = app.config['TELEGRAM_API_KEY']
BOT_USERNAME: Final = '@Faceit_helper_bot'

# Markups
start_markup = ReplyKeyboardMarkup(
    [[KeyboardButton("/find_player"), KeyboardButton("/top_players")]],
    resize_keyboard=True
)

select_region_markup = ReplyKeyboardMarkup(
    [[KeyboardButton("/EU"), KeyboardButton("/NA")],
     [KeyboardButton("/SA"), KeyboardButton("/SEA"), KeyboardButton("/OCE")]],
    resize_keyboard=True
)

add_more_20_player_markup = ReplyKeyboardMarkup(
    [[KeyboardButton("/add_more_20_player"), KeyboardButton("/back")]],
    resize_keyboard=True
)

avg_stats_markup = ReplyKeyboardMarkup(
    [[KeyboardButton("/last_10_avg"), KeyboardButton("/last_20_avg"), KeyboardButton("/last_50_avg"), KeyboardButton("/last_100_avg")]],
    resize_keyboard=True
)


# Functions
async def player_info(update: Update, context: ContextTypes.DEFAULT_TYPE, text):
    search_value = text
    try:
        player_info_data, _, nickname, player_global_rank, player_country_rank = search_by_steamid_64(search_value)

        if player_info_data and 'player_id' in player_info_data:
            player_stats_data, full_player_stats_data = get_player_stats(player_info_data['player_id'], limit=200)
            context.user_data['player_data'] = {'info': player_info_data, 'stats': player_stats_data}

            # Extract and format data
            lifetime_data = full_player_stats_data.get('lifetime', [{}])
            games_data = player_info_data.get('games', {}).get('cs2', {})

            response_message = (
                f"Nickname: {nickname} \n"
                f"{player_info_data['games']['cs2']['region'].upper()} rank: #{player_global_rank}\n"
                f"{player_info_data['country'].upper()} rank: #{player_country_rank}\n"
                f"ELO: {games_data.get('faceit_elo', 'N/A')}\n\n"
                f"K/D: {lifetime_data.get('Average K/D Ratio', 'N/A')}\n"
                f"HS: {lifetime_data.get('Average Headshots %', 'N/A')}%\n"
                f"Matches: {lifetime_data.get('Matches', 'N/A')}\n"
                f"Win Rate: {lifetime_data.get('Win Rate %', 'N/A')}%\n"
            )

            print('Bot', response_message)

            avatar_url = player_info_data.get('avatar', '')
            if avatar_url:
                await update.message.reply_photo(avatar_url, caption=response_message, reply_markup=avg_stats_markup)
            else:
                await update.message.reply_text(response_message, reply_markup=avg_stats_markup)
        else:
            await update.message.reply_text('Invalid value or Player has not played in CS2.', reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")
        print(f"Error handling message: {str(e)}") 

async def player_avg_stats(update: Update, context: ContextTypes.DEFAULT_TYPE, avg_index: int):
    player_data = context.user_data.get('player_data')
    if player_data:
        averages_last = calculate_averages(player_data['stats'], avg_index)
        averages_prev = calculate_averages(player_data['stats'], avg_index, start_index=avg_index)

        if averages_last is None or averages_prev is None:
            await update.message.reply_text('Error calculating averages. Please try again.', reply_markup=ReplyKeyboardRemove())
            return

        response_message = (
            f"Averages last {avg_index} matches:\n\n"
            f"K/D/A: {averages_last['avg_kills']}/{averages_last['avg_deaths']}/{averages_last['avg_assists']}\n"
            f"K/D: {averages_last['avg_kd_ratio']:.2f}\n"
            f"K/R: {averages_last['avg_kr_ratio']:.2f}\n"
            f"HS%: {averages_last['avg_hs_procent']}%\n\n"
        )

        await update.message.reply_text(response_message, reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text('No player data found. Please find a player first using /find_player.', reply_markup=ReplyKeyboardRemove())

async def add_more_20_player_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    offset = context.user_data.get('offset', 0)
    region = context.user_data.get('region', 'EU')

    offset += 20
    context.user_data['offset'] = offset

    if region == 'EU':
        rankings = Player.get_global_eu_ranking(limit=20, offset=offset)
    elif region == 'NA':
        rankings = Player.get_global_na_ranking(limit=20, offset=offset)
    elif region == 'SA':
        rankings = Player.get_global_sa_ranking(limit=20, offset=offset)
    elif region == 'SEA':
        rankings = Player.get_global_sea_ranking(limit=20, offset=offset)
    elif region == 'OCE':
        rankings = Player.get_global_oce_ranking(limit=20, offset=offset)
    else:
        await update.message.reply_text('Region not recognized.', reply_markup=ReplyKeyboardRemove())
        return

    await output_top(update, context, rankings, region)

async def output_top(update: Update, context: ContextTypes.DEFAULT_TYPE, rankings: list, region: str):
    if not rankings:
        await update.message.reply_text(f"No top players found for region {region}.", reply_markup=ReplyKeyboardRemove())
        return

    response_message = f"Top players in {region}:\n\n"
    for player in rankings:
        position = player.get('position', 'N/A')
        nickname = player.get('nickname', 'Unknown')
        faceit_elo = player.get('faceit_elo', 'N/A') 
        response_message += f"Rank {position}:   {nickname}    ELO: {faceit_elo}\n"

    await update.message.reply_text(response_message, reply_markup=add_more_20_player_markup)


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Hello! You can Find Player or check current Players Top.',
        reply_markup=start_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('With this BOT you can find player or look at top', reply_markup=ReplyKeyboardRemove())

async def back_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Navigated back.', reply_markup=ReplyKeyboardRemove())

async def find_player_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Enter: Faceit Nickname/Steam Url/SteamID/SteamID64',
        reply_markup=ReplyKeyboardRemove()
    )

async def last_10_avg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await player_avg_stats(update, context, avg_index=10)

async def last_20_avg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await player_avg_stats(update, context, avg_index=20)

async def last_50_avg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await player_avg_stats(update, context, avg_index=50)

async def last_100_avg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await player_avg_stats(update, context, avg_index=100)

async def top_players_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Choose region', reply_markup=select_region_markup
    )

async def eu_top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['region'] = 'EU'
    context.user_data['offset'] = 0 
    rankings = Player.get_global_eu_ranking(limit=20)
    await output_top(update, context, rankings, region='EU')

async def na_top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['region'] = 'NA'
    context.user_data['offset'] = 0 
    rankings = Player.get_global_na_ranking(limit=20)
    await output_top(update, context, rankings, region='NA')

async def sa_top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['region'] = 'SA'
    context.user_data['offset'] = 0 
    rankings = Player.get_global_sa_ranking(limit=20)
    await output_top(update, context, rankings, region='SA')

async def sea_top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['region'] = 'SEA'
    context.user_data['offset'] = 0 
    rankings = Player.get_global_sea_ranking(limit=20)
    await output_top(update, context, rankings, region='SEA')

async def oce_top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['region'] = 'OCE'
    context.user_data['offset'] = 0 
    rankings = Player.get_global_oce_ranking(limit=20)
    await output_top(update, context, rankings, region='OCE')


# Response
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    if text:
        await player_info(update, context, text)
        print(f'User ({update.message.id}) in {message_type}: "{text}"')


# Errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == '__main__':
    print('Starting...')

    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('find_player', find_player_command))
    app.add_handler(CommandHandler('top_players', top_players_command))
    app.add_handler(CommandHandler('EU', eu_top_command))
    app.add_handler(CommandHandler('NA', na_top_command))
    app.add_handler(CommandHandler('SA', sa_top_command))
    app.add_handler(CommandHandler('SEA', sea_top_command))
    app.add_handler(CommandHandler('OCE', oce_top_command))
    app.add_handler(CommandHandler('add_more_20_player', add_more_20_player_command))
    app.add_handler(CommandHandler('back', back_command))
    app.add_handler(CommandHandler('last_10_avg', last_10_avg_command))
    app.add_handler(CommandHandler('last_20_avg', last_20_avg_command))
    app.add_handler(CommandHandler('last_50_avg', last_50_avg_command))
    app.add_handler(CommandHandler('last_100_avg', last_100_avg_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Log all errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=5)