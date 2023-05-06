# library imports
import uvicorn
import joblib
from fastapi import FastAPI
import requests
import json
from collections import defaultdict
from fastapi.middleware.cors import CORSMiddleware
import time

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

api_key = "RGAPI-221d4c9f-4589-40e2-893f-6bd383cebd2f"

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/summoner/{name}")
def get_summoner_by_name(name: str):
    summoner = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/"+name+'?api_key='+api_key
    try: 
        response = requests.get(summoner)
    except:
        time.sleep(5)
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
        time.sleep(5)
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
            time.sleep(5)
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


@app.post('/predict')
def predict(data):
    return 0

'''
def main():
    uvicorn.run(app, host='127.0.0.1', port=8000)

if __name__ == '__main__':
    main()
'''