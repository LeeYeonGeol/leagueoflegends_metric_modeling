# leagueoflegends_metric_modeling
인분 지표 설계 및 구현

# Model
- XGBoost를 RandomizedSearchCV를 통해 돌린 결과
- `subsample` : 0.8
- `n_estimators` : 500
- `max_depth` : 20
- `learning_rate` : 0.05

# Algorithm
1. 이진분류에 사용된 로짓값을 IsotonicRegression을 통해 승률에 근사
2. 이를 바탕으로 팀원들간의 상대적 기여도 측정


# Site
- http://3.35.209.15:8501/
<img src="https://user-images.githubusercontent.com/48538655/236659294-16b56f1e-399c-47d8-b86f-ca591b9a60d1.png" alt="사이트 화면" width="500">

# Reference
- https://scienceon.kisti.re.kr/commons/util/originalView.do?cn=JAKO201714563379407&oCn=JAKO201714563379407&dbt=JAKO&journal=NJOU00294613
- https://shinminyong.tistory.com/11
- https://towardsdatascience.com/pythons-predict-proba-doesn-t-actually-predict-probabilities-and-how-to-fix-it-f582c21d63fc
- https://3months.tistory.com/490

# TODO 
- 인분 지표 사이트상에 출력
- 도커 사용
- 젠킨스, GITLAB 등 통해 무중단 배포
- 더 다양한 지표 혹은 모델 사용
