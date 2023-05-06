import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import time

def header(url):
    st.markdown(f'<p style="background-color:#0066cc;color:#33ff33;font-size:24px;border-radius:2%;">{url}</p>', unsafe_allow_html=True)

# 제목과 부제목
st.title('League of Legends 전적검색')
st.subheader('게임 정보 및 플레이어 전적 확인하기')

API_KEY = "RGAPI-221d4c9f-4589-40e2-893f-6bd383cebd2f"

url = "http://0.0.0.0:5000"

@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data


with st.container():
    # 2개의 열(column) 생성
    col1, col2 = st.columns([3, 1])

    # col1에 검색어 입력 받기
    summoner_name = col1.text_input('소환사명을 입력하세요.')

    # col2에 검색 버튼 생성
    search_button = col2.button('검색')

if summoner_name:
    try:
        matches = requests.get(url=url+"/summoner/"+summoner_name+"/matches")
        time.sleep(2)
        matches.raise_for_status()  # HTTP 에러 체크
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error occurred: {e}")
    except:
        st.error("Unexpected error occurred.")

    # 매치
    response = requests.get(url=url+"/summoner/"+summoner_name+"/matches/match_info")
    time.sleep(2)
    match_data = response.json()



    # 데이터 출력
    for match_id in match_data:
        match = match_data[match_id]
        game_duration = match["game_duration"][0]
        searched_summoner = match['searched_summoner'][0]

        summonerName = searched_summoner['summonerName']
        summonerChamp = searched_summoner['championName']
        kills = searched_summoner['kills']
        deaths = searched_summoner['deaths']
        assists = searched_summoner['assists']
        cs = searched_summoner['cs']
        win = searched_summoner['win']
        my_image = match['all_champ_images'][summonerChamp]
        
        # 칼럼 설정
        col1, col2, col3, col4 = st.columns(spec=4)

        with col1:
            st.write("챔피언")
            # 챔피언 이미지 출력
            st.image(my_image, caption=summonerChamp, width=60)
            
        with col2:
            # KDA 및 승패 출력
            st.write("KDA: {} / {} / {}, {}".format(kills, deaths, assists, "승리" if win else "패배"))
            # CS 출력
            st.write("CS: {}".format(cs))
        with col3:
            team_members = []

            for i in range(5):
                Champ = match['all_champ_names'][i]
                team_members.append({"name": match['all_summoner_names'][i], "image_url": match['all_champ_images'][Champ]})

            team_member_info = []
            # 각 팀원 정보를 리스트에 추가
            for member in team_members:
                team_member_info.append(f"<img src='{member['image_url']}' width='30' height='30'> **{member['name']}**")

            # 팀원 정보를 Markdown 형식으로 출력
            st.markdown("<br>".join(team_member_info), unsafe_allow_html=True)
        with col4:
            team_members = []

            for i in range(5, 10):
                Champ = match['all_champ_names'][i]
                team_members.append({"name": match['all_summoner_names'][i], "image_url": match['all_champ_images'][Champ]})

            team_member_info = []
            # 각 팀원 정보를 리스트에 추가
            for member in team_members:
                team_member_info.append(f"<img src='{member['image_url']}' width='30' height='30'> **{member['name']}**")

            # 팀원 정보를 Markdown 형식으로 출력
            st.markdown("<br>".join(team_member_info), unsafe_allow_html=True)

    

    # 구분선
    st.write("---")

