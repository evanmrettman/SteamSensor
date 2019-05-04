from objects.game import Game
import utility.logging as log
from collections import defaultdict

def CreateGames(json_dicts):
    games = defaultdict(Game)
    for i, steam_response in enumerate(json_dicts):
        appid = list(steam_response.keys())[0]
        inner_d = steam_response[appid]
        if inner_d["success"] == True:
            if inner_d["data"]["type"] == "game":
                games[int(appid)] = Game(steam_response)
        log.sofar("Creating Games",i,len(json_dicts),10)
    return games

def ProcessAddSteamSpy(json_dicts, games):
    log.processing("Adding steam spy data...")
    count = 0
    for game in games:
        game.addSteamSpyData(json_dicts)
        count += 1
        log.sofar("Adding steam spy data", count, len(json_dicts),10)


#retrieve list of all possible platforms, categories, genres, languages, and tags for vectorization
def getPlatforms(games):
    #TEST THIS?
    platforms = []
    for game in games.values():
        game_platforms = game.get_platforms()
        if game_platforms != None and len(game_platforms) != 0:
            for platform in game_platforms:
                if not platform in platforms:
                    platforms.append(platform)
    return platforms

def getDevelopers(games):
    #TEST THIS?
    developers = []
    for game in games.values():
        game_developers = game.get_developers()
        if game_developers != None and len(game_developers) != 0:
            for developer in game_developers:
                if not developer in developers:
                    developers.append(developer)
    return developers

def getPublishers(games):
    #TEST THIS?
    publishers = []
    for game in games.values():
        game_publishers = game.get_publishers()
        if game_publishers != None and len(game_publishers) != 0:
            for publisher in game_publishers:
                if not publisher in publishers:
                    publishers.append(publisher)
    return publishers

def getCategories(games):
    #TEST THIS?
    categories = []
    for game in games.values():
        game_categories = game.get_categories()
        if game_categories != None and len(game_categories) != 0:
            for category in game_categories:
                if not category in categories:
                    categories.append(category)

    return categories

def getGenres(games):
    #TEST THIS?
    genres = []
    for game in games.values():
        game_genres = game.get_genres()
        if game_genres != None and len(game_genres) != 0:
            for genre in game_genres:
                if not genre in genres:
                    genres.append(genre)

    return genres

def getLanguages(games):
    #TEST THIS?
    langs = []
    for game in games.values():
        game_langs = game.get_supported_languages()
        if game_langs != None and len(game_langs) != 0:
            for lang in game_langs:
                if not lang in langs:
                    langs.append(lang)

    return langs

#returns 
def getTags(games):
    #TEST THIS?
    tags = []
    for game in games.values():
        game_tags = game.get_tags()
        if game_tags != None and len(game_tags) != 0:
            for key in game_tags.keys():
                if not key in tags:
                    tags.append(key)

    return tags