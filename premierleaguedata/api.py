'''
    Created by Erick Ghuron
'''
import json
import pandas as pd
import requests


def req_to_json(req: requests.Response) -> dict:
    if req.status_code == 200:
        return json.loads(req.text)
    else:
        raise ValueError(f'Error! status code:<{req.status_code}>')
    

class PremierLeagueAPI:
    def __init__(self) -> None:
        self.header = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.premierleague.com',
            'referer': 'https://www.premierleague.com/',
        }
        
        self.root_url = 'https://footballapi.pulselive.com/football/'
    
    def __api_call(self, path:str, qparams:dict = {}):
        url = self.root_url + path
        
        res = requests.get(url, headers=self.header, params= qparams)
        
        return req_to_json(res)

    def standings(self, compSeasons:str, altIds:str='true', detail:str ='2', FOOTBALL_COMPETITION:str = '1', live:str = 'true') -> dict:
        
        payload = {
            'compSeasons': compSeasons,
            'altIds': altIds,
            'detail': detail,
            'FOOTBALL_COMPETITION': FOOTBALL_COMPETITION,
            'live': live
        }

        return self.__api_call('standings', payload)

    def competitions(self, page:str = '0', pageSize:str = '1000', detail:str = '2') -> dict:
        
        payload = {
            'page': page,
            'pageSize': pageSize,
            'detail': detail
        }
        
        return self.__api_call('competitions', payload)

    def compseasons(self, page:str = '0', pageSize:str = '100') -> dict:
        
        payload = {
            'page': page,
            'pageSize': pageSize
        }

        res = requests.get('https://footballapi.pulselive.com/football/compseasons', headers=self.header, params=payload)
        
        return self.__api_call('compseasons', payload)
    
    def get_season_id(self, season_label: str = None) -> str:
        # Call API to get all season data
        seasons_data = self.__api_call("competitions/1/compseasons")

        # Make sure the API returns data
        if "content" not in seasons_data:
            raise ValueError

        # Find the ID of a given season
        if season_label:
            for season in seasons_data["content"]:
                if season["label"] == season_label:
                    return str(int(season["id"]))
            raise ValueError(f"Unable to find the season: {season_label}")

        # Get latest season ID (ID max)
        latest_season = max(seasons_data["content"], key=lambda x: x["id"])
        return str(int(latest_season["id"]))

    def club_incompseason(self, compseason:str) -> dict:
                
        return self.__api_call(f'compseasons/{compseason}/teams')

    def club_playedgames(self, compseason:str, teamId:str, altIds:str = 'true') -> dict:
                
        return self.__api_call(f'compseasons/{compseason}/standings/team/{teamId}?altIds={altIds}')

    def club_information(self, teamId:str ) -> dict:
               
        return self.__api_call(f'clubs/{teamId}')
    
    def get_player_stats(self, stat_type: str, season_id: str) -> pd.DataFrame:
        try:
            # Parameters
            params = {
                "pageSize": 50,
                "compSeasons": season_id,
                "comps": 1,
                "compCodeForActivePlayer": "EN_PR",
                "altIds": "true"
            }
            
            res = self.__api_call(
                f"stats/ranked/players/{stat_type}",
                qparams=params
            )
            
            # Parsing the data
            data = []
            for item in res.get("stats", {}).get("content", []):
                player = item.get("owner", {})
                data.append({
                    "Rank": item.get("rank"),
                    "Player": player.get("name", {}).get("display"),
                    "Club": player.get("currentTeam", {}).get("name"),
                    "Nationality": player.get("nationalTeam", {}).get("country"),
                    "Stat": item.get("value")
                })
            return pd.DataFrame(data)
        
        except Exception as e:
            print(f"Failed in geting {stat_type}: {str(e)}")
            return pd.DataFrame()