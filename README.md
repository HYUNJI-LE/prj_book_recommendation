# prj_book_recommendation

## 네이버 도서 추천 시스템 만들기 프로젝트입니다


### 사용자가 원하는 도서를 추천해주는 도서 추천 어플리케이션 S-Book(Search-Book) 

- 유사도를 바탕으로 도서 추천 목록을 생성하는 추천 알고리즘
- 입력된 도서 제목 혹은 도서 관련 키워드를 통해 사용자에게 추천 도서 10권에 대한 정보를 제공
- 도서 제목을 일부 입력하였을 경우 자동 완성기능을 제공하고 있어 사용자가 보다 편리한 어플리케이션 이용 가능
- 원하는 키워드가 없을 경우 랜덤 형식으로 추천도서를 제공

### 사용 언어 

python

### 사용 툴 

pycharm, jupyter notebook, QT designer

### 구현 방법 

- TFIDF 와 Word2Vec 모델을 사용한 유사도 측정 
- 모델에 없는 키워드를 입력 시 'Naver Book' 에서 실시간 크롤링 후 유사도 측정

### 구현 결과 


- 키워드를 입력하여 도서 추천 받기 



![그림1](https://user-images.githubusercontent.com/72773190/99938152-8bea2400-2daa-11eb-8cfb-acfe37c55689.png)


- 책 제목을 입력하여 도서 추천 받기 



![그림2](https://user-images.githubusercontent.com/72773190/99938171-94425f00-2daa-11eb-86f7-d2371d4e2857.png)


- 랜덤으로 도서 추천 받기



![그림3](https://user-images.githubusercontent.com/72773190/99938179-999fa980-2daa-11eb-9fb5-1ab684fa6b34.png)
