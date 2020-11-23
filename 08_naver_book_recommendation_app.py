import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QStringListModel
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from gensim.models import Word2Vec
from selenium import webdriver
import re
from konlpy.tag import Okt
from selenium.webdriver.common.keys import Keys

form_window = uic.loadUiType('./mainwidget.ui')[0] #GUI연결

class Exam(QWidget, form_window): #위젯형식(QWidget 등) 지정
    def __init__(self):
        super().__init__() #조상함수 호출 / 창 만들어짐 / 조상클래스
        self.setupUi(self) #함수호출
        self.initUI()

    def initUI(self):
        self.df_book_one_sentence = pd.read_csv('./crawling/cleaned_daum_book.csv', index_col=0) # 책_서평 리스트 불러오기
        self.stopwords = pd.read_csv('./datasets/stopwords_for_book.csv', index_col=0)
        # tfidf: 한문장안에 여러번 나오는 것 가중치, 여러문장에 여러번 나오는 것 역산한 점수
        self.Tfidf = TfidfVectorizer(sublinear_tf=True)
        self.Tfidf_matrix = self.Tfidf.fit_transform(self.df_book_one_sentence['cleaned_content'])
        self.btn_exec.clicked.connect(self.btn_exec_clicked_slot)
        self.titles = list(self.df_book_one_sentence['title'])

        #자동완성기능
        model = QStringListModel()
        model.setStringList(self.titles)
        completer =QCompleter()
        completer.setModel(model)
        self.le_title.setCompleter(completer)


    #영화 추천 함수
    def getRecommendation(self, cosine_sim):
        simScores = list(enumerate(cosine_sim[-1])) #유사도 점수 리스트로 만들기
        simScores = sorted(simScores, key=lambda x: x[1], reverse=True) #연관도 높은 순으로 정렬
        simScores = simScores[0:11] #출력할 책 갯수
        bookidx = [i[0] for i in simScores]
        RecBooklist = self.df_book_one_sentence.iloc[bookidx]
        return RecBooklist.title

    def btn_exec_clicked_slot(self):
        word = self.le_title.text() #입력창에 입력한 값
        #입력된 단어와 연관된 단어들을 불러와서 책을 추천해줌.
        embedding_model = Word2Vec.load('./model/word2VecModel_book.model')

        if word in self.titles:
            book_idx = self.df_book_one_sentence[self.df_book_one_sentence['title'] == word].index[0]
            # 책 사이의 유사도 점수
            cosine_sim = linear_kernel(self.Tfidf_matrix[book_idx], self.Tfidf_matrix)
            # 추천도서 출력
            print(list(self.getRecommendation(cosine_sim)))
            self.lb_recommend.setText('당신을 위한 추천도서입니다.\n\n'+'\n'.join(list(self.getRecommendation(cosine_sim)[1:])))

        elif word in embedding_model.wv.vocab:
            sim_words = embedding_model.wv.most_similar(word.split(' ')[0], topn=10)
            self.content = [word] * 11
            words = []
            for sim_word, _ in sim_words:
                words.append(sim_word)
            for i in range(10):
                self.content = self.content + ([words[i]]*(10-i))
            self.transform_slot()
        else:
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('disable-gpu')
            options.add_argument('lang=ko_KR')

            driver = webdriver.Chrome('./chromedriver', options=options)
            driver.implicitly_wait(3)  # 빨리 끝나면 기다리는 않는 유동적인 기다림
            driver.get('https://book.naver.com/')
            if word == '':
                driver.find_element_by_xpath('// *[ @ id = "owl"] / div / div / div[1] / a / div / span[1] / span').click()
                driver.switch_to.window(driver.window_handles[1])
                about_book = driver.find_element_by_xpath('//*[@id="content"]').text  # 서평 읽어보기
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            else:
                driver.find_element_by_id('nx_query').send_keys(word)
                driver.find_element_by_id('nx_query').send_keys(Keys.RETURN)  # 엔터키 클릭
                about_book = driver.find_element_by_xpath('//*[@id="content"]').text  # 서평 읽어보기

            driver.close()

            # 텍스트 전처리
            okt = Okt()
            sentence = re.sub('[^가-힣]', ' ', about_book)
            token = okt.pos(sentence, norm=True, stem=True)  # pos:품사 부착 #norm:현대적인 말은 원형으로 #stem:동사 원형으로
            df_token = pd.DataFrame(token, columns=['word', 'class'])  # 단어-품사 DF만듬
            cleaned_df_token = df_token[
                (df_token['class'] == 'Noun') | (df_token['class'] == 'Verb') | (df_token['class'] == 'Adjective')]
            self.content = []
            for word in cleaned_df_token['word']:
                if len(word) > 1:  # 1글자 없애기
                    if word not in (list(self.stopwords['stopword'])):  # stopwords없애기
                        self.content.append(word)
            self.transform_slot()

    def transform_slot(self):
        content = ' '.join(self.content)
        print(content)

        # 입력한 값을 Tfidf 점수로 변환
        title_vec = self.Tfidf.transform([content])
        # 책 사이의 유사도 점수
        cosine_sim = linear_kernel(title_vec, self.Tfidf_matrix)
        # 추천영화 출력
        print(list(self.getRecommendation(cosine_sim)))
        self.lb_recommend.setText('당신을 위한 추천도서입니다.\n\n'+'\n'.join(list(self.getRecommendation(cosine_sim))))


app = QApplication(sys.argv) #어플리케이션 클래스객체를 만듬 (매개변수), 이벤트 루프가 호출됨.
mainWindow = Exam()  #mainwindow에 exam class 얹고
mainWindow.show() #창을 띄운다. 뜬 창을 닫으면
sys.exit(app.exec_())  #종료하고 빠져나옴.구문이 끝남.(exec