# library imports
import uvicorn
import joblib
from fastapi import FastAPI, File
import requests
import json
from collections import defaultdict
from fastapi.middleware.cors import CORSMiddleware
import time
import pickle
import pandas as pd

# create the app object
app = FastAPI()

# 출처 명시
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000"
]

# 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = "RGAPI-f9bb08f5-8267-4773-8770-79efaa9130e4"

def get_test_df(response, data_columns, API_KEY):
    db = defaultdict(list)
    
    position = {0: 'TOP', 1: 'JUNGLE', 2: "MID", 3: "AD_CARRY", 4: "SUPPORT"}
    participant_data = response['info']['participants']
    gameDuration = response['info']['gameDuration']
    
    summonerNames = []
    for k in range(10):
        summonerName = response['info']['participants'][k]['summonerName']

        summonerNames.append(summonerName)
        
        sohwan_url = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName +'?api_key=' + API_KEY
        
        try: 
            r = requests.get(sohwan_url)
        except:
            time.sleep(1)
            r = requests.get(sohwan_url)
        sohwan_info = r.json()
        summonerID = sohwan_info['id']

        league_url = "https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/"+ summonerID +"?api_key=" + API_KEY
        try: 
            r = requests.get(league_url)
        except:
            time.sleep(1)        
            r = requests.get(league_url)

        league_info = r.json()
    
        db['position'].append(position[k%5])
        db['gameDuration'].append(gameDuration)
    
        for column in ['champLevel', 'kills', 'deaths', 'assists','totalDamageDealtToChampions', 'damageSelfMitigated', 'totalHeal', 'totalMinionsKilled', 'neutralMinionsKilled', 'wardsPlaced','visionScore', 'win']:
            db[column].append(participant_data[k][column])
    
        # 티어
        for league in league_info:
            if league["queueType"] == "RANKED_SOLO_5x5":
                db['tier'].append(league["tier"])
                break
        else:
            # 언랭은 실버 취급
            db['tier'].append("SILVER")
    
    result_df = pd.DataFrame(columns = data_columns)
    
    for k, column in enumerate(data_columns):
        if k <= 12:
            result_df[column] = db[column]
        elif k <= 16:
            if 'JUNGLE' in column:
                result_df[column] = [1 if x == 'JUNGLE' else 0  for x in db['position']]
            elif 'MID' in column:
                result_df[column] = [1 if x == 'MID' else 0  for x in db['position']]
            elif 'SUPPORT' in column:
                result_df[column] = [1 if x == 'SUPPORT' else 0  for x in db['position']]
            elif 'TOP' in column:
                result_df[column] = [1 if x == 'TOP' else 0  for x in db['position']]
        else:
            if 'DIAMOND' in column:
                result_df[column] = [1 if x == 'DIAMOND' else 0  for x in db['tier']]
            elif 'GOLD' in column:
                result_df[column] = [1 if x == 'GOLD' else 0  for x in db['tier']]
            elif 'GRANDMASTER' in column:
                result_df[column] = [1 if x == 'GRANDMASTER' else 0  for x in db['tier']]
            elif 'MASTER' in column:
                result_df[column] = [1 if x == 'MASTER' else 0  for x in db['tier']]            
            elif 'PLATINUM' in column:
                result_df[column] = [1 if x == 'PLATINUM' else 0  for x in db['tier']]  
            elif 'SILVER' in column:
                result_df[column] = [1 if x == 'SILVER' else 0  for x in db['tier']]  
                
    return result_df, summonerNames



@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/summoner/{name}")
def get_summoner_by_name(name: str):
    summoner = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/"+name+'?api_key='+api_key
    try: 
        response = requests.get(summoner)
    except:
        time.sleep(1)
        response = requests.get(summoner)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Unable to fetch summoner.", "status_code": response.status_code, "reason": response.reason}


@app.get("/summoner/{name}/matches")
def get_matches(name: str):
    summoner_info = get_summoner_by_name(name)
    puuid = summoner_info["puuid"]

    api_url = "https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/"+puuid+"/ids?start=0&count=20&api_key="+api_key
    try: 
        response = requests.get(api_url)
    except:
        time.sleep(1)
        response = requests.get(api_url)   

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Unable to fetch matches.", "status_code": response.status_code, "reason": response.reason}

@app.get("/summoner/{name}/matches/match_info")
def get_match_info(name: str):
    puuid = get_summoner_by_name(name)['puuid']
    matches = get_matches(name)
    db = {}
    for idx1, match in enumerate(matches):
        if idx1 == 10:
            break
        api_url = "https://asia.api.riotgames.com/lol/match/v5/matches/"+match+"?api_key="+api_key
        
        try:
            response = requests.get(api_url)
        except:
            time.sleep(1)
            response = requests.get(api_url)
        response = response.json()

        match_db = {}
        # 게임 소요 시간
        match_db['game_duration'] = [response['info']['gameDuration']]

        # 소환사명 저장
        all_summoner_names = []

        # 챔피언명 저장 (사진 불러오는 용도)
        all_champ_names = []

        # 검색된 소환사 정보
        searched_summoner = {}
        
        for idx, participant in enumerate(response['info']['participants']):
            all_summoner_names.append(participant['summonerName'])
            all_champ_names.append(participant['championName'])
            # 검색한 소환사에 대한 정보
            
            if participant['puuid'] == puuid:
                searched_summoner['summonerName'] = participant['summonerName']
                searched_summoner['championName'] = participant['championName']
                searched_summoner['kills'] = participant['kills']
                searched_summoner['deaths'] = participant['deaths']
                searched_summoner['assists'] = participant['assists']
                searched_summoner['cs'] = participant['neutralMinionsKilled']+participant['totalMinionsKilled']
                searched_summoner['win'] = participant['win']
        
        match_db['all_summoner_names'] = all_summoner_names
        match_db['all_champ_names'] = all_champ_names
        match_db['searched_summoner'] = [searched_summoner]
        
        # 챔피언 이미지 저장
        all_champ_images = {}
        for champ in all_champ_names:
            all_champ_images[champ] = "https://ddragon.leagueoflegends.com/cdn/13.9.1/img/champion/"+champ+".png"

        match_db['all_champ_images'] = all_champ_images

        db[match] = match_db
    
    json_db = json.dumps(db, separators=(',', ':'))

    return db


@app.get('/summoner/{name}/wpa')
def predict(name: str):
    matches = get_matches(name)

    data_columns = ['gameDuration', 'champLevel', 'kills', 'deaths', 'assists',\
        'totalDamageDealtToChampions', 'damageSelfMitigated', 'totalHeal',\
        'totalMinionsKilled', 'neutralMinionsKilled', 'wardsPlaced',\
        'visionScore', 'win', 'position_JUNGLE', 'position_MID',\
        'position_SUPPORT', 'position_TOP', 'tier_DIAMOND', 'tier_GOLD',\
        'tier_GRANDMASTER', 'tier_MASTER', 'tier_PLATINUM', 'tier_SILVER']

    test_db = {}
    champion_db = defaultdict(list)
    win_rate_db = defaultdict(list)


    # 매치별로 for문 돌기
    for idx1, match in enumerate(matches):
        if idx1 == 10:
            break
        api_url = "https://asia.api.riotgames.com/lol/match/v5/matches/"+match+"?api_key="+api_key
        response = requests.get(api_url)
        response = response.json()

        test_df, summonerNames = get_test_df(response, data_columns, api_key)

        #champion_db[idx1] = summonerNames



    
        # model load
        #model = pickle.loads("../model_grid.pkl")
    


    return 0


def main():
    uvicorn.run(app, host='127.0.0.1', port=5000)

if __name__ == '__main__':
    main()
