import requests
import os
import pandas as pd
from pandas import json_normalize
import time
from tqdm import tqdm
from collections import defaultdict


# puuid를 얻는 함수
def get_puuid(api_key, tier, page):
    print("puuid 구하기 시작!!!")

    # 1. summonerName 구하기
    result_df = pd.DataFrame()
    # 챌린저, 그랜드마스터, 마스터는 I밖에 없으므로
    if tier in ["CHALLENGER", "GRANDMASTER", "MASTER"]:
        league_exp_url = 'https://kr.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/'+tier+'/I?page='+str(page)+'&api_key='+ api_key
        r = requests.get(league_exp_url)

        while r.status_code == 429:
            time.sleep(60)
            league_exp_url = 'https://kr.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/'+tier+'/I?page='+str(page)+'&api_key='+ api_key
            r = requests.get(league_exp_url)

        df = pd.DataFrame(r.json())
        result_df = pd.concat([result_df, df])
    # 나머지는 I, II, III, IV
    else:
        for level in ["I", "II", "III", "IV"]:
            league_exp_url = 'https://kr.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/'+tier+'/'+level+'?page='+str(page)+'&api_key='+ api_key
            r = requests.get(league_exp_url)
            while r.status_code == 429:
                time.sleep(60)
                league_exp_url = 'https://kr.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/'+tier+'/'+level+'?page='+str(page)+'&api_key='+ api_key
            r = requests.get(league_exp_url)


            df = pd.DataFrame(r.json())
            result_df = pd.concat([result_df, df])

    # 2. summonerName이용하여 puuid 구하기
    for i in tqdm(range(30)):
        try:
            summoner = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + result_df['summonerName'].iloc[i] + '?api_key=' + api_key
            
            r = requests.get(summoner)
            
            while r.status_code == 429:
                time.sleep(60)
                summoner = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + result_df['summonerName'].iloc[i] + '?api_key=' + api_key
            
                r = requests.get(summoner)       
                
            
                
            puuid = r.json()['puuid']

            result_df.iloc[i, -1] = puuid
        
        # summonerName존재하지만 puuid가 없는 경우 예외처리
        except:
            pass        
    new_result_df = pd.DataFrame()
    new_result_df['summonerName'] = result_df['summonerName']
    new_result_df['puuid'] = result_df.iloc[:,-1]

    # 결측치 제거
    new_result_df = new_result_df.dropna()
    
    return new_result_df


# puuid를 통해, match id 구하는 함수 (20경기)
def get_match_ids(api_key, df):
    print("match id 구하기 시작!!!")
    matchs = []
    for index, row in tqdm(df.iterrows()):
        try:
            puuid = row['puuid']
            if type(puuid) == str:
                api_url = "https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/"+puuid+"/ids?start=0&count=20&api_key="+api_key
            r = requests.get(api_url)
            while r.status_code == 429:
                time.sleep(60)
                if type(puuid) == str:
                    api_url = "https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/"+puuid+"/ids?start=0&count=20&api_key="+api_key
                r = requests.get(api_url)
            matchs += r.json()
        except:
            pass
    
    return matchs

# match id를 통해 match 정보 구하는 함수
def get_match_info(api_key, matchs, tier, information_db):
    print("match 정보 구하기 시작!!!")
    match_df = pd.DataFrame()

    position = {0: 'TOP', 1: 'JUNGLE', 2: "MID", 3: "AD_CARRY", 4: "SUPPORT"}

    for match in tqdm(matchs):
        try:
            api_url = "https://asia.api.riotgames.com/lol/match/v5/matches/"+match+"?api_key="+api_key
            r = requests.get(api_url)
            while r.status_code == 429:
                time.sleep(60)
                api_url = "https://asia.api.riotgames.com/lol/match/v5/matches/"+match+"?api_key="+api_key
                r = requests.get(api_url)
            json_data = r.json()
            participant_data = json_data['info']['participants']
            gameDuration = json_data['info']['gameDuration']
            for i in range(10):
                participant_pd = json_normalize(participant_data[i])
                information_db['position'].append(position[i%5])
                information_db['tier'].append(tier)
                information_db['gameDuration'].append(gameDuration)
                match_df = pd.concat([match_df, participant_pd])
        except:
            pass
    return match_df, information_db

def main():
    
    api_key = "RGAPI-221d4c9f-4589-40e2-893f-6bd383cebd2f"

    tiers = ["SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]

    page = 1

    for tier in tiers:
        information_db = defaultdict(list)
        result_df = pd.DataFrame()
        matchs = []
        print(tier + "티어 데이터 수집 시작!!!")
        puuid_df = get_puuid(api_key, tier, page)
        matchs += get_match_ids(api_key, puuid_df)

        match_df, information_db = get_match_info(api_key, matchs, tier, information_db)


        result_df = result_df.reset_index()
        match_df = match_df.reset_index()
        information_df = pd.DataFrame(information_db)
        information_df = information_df.reset_index()


        result_df = pd.concat([result_df, match_df])

        result_df = pd.concat([result_df, pd.DataFrame(information_df)], axis = 1)

        if not os.path.exists('data_9.csv'):
            result_df.to_csv('data_9.csv',mode='w', index=False)
        else:
            result_df.to_csv('data_9.csv',mode='a', index=False, header=False)

if __name__ == "__main__":
	main()