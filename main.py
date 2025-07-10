import sys
import sqlite3
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QStackedWidget, QMessageBox, QProgressBar, QGridLayout,QHeaderView, QInputDialog,QDialog) 
from PyQt5.QtCore import Qt, QTimer,QUrl
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas    

#1.PENCERE
class FirstWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.media_player = QMediaPlayer()
        self.music_file = "first_music.mp3" #1.pencere için
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.music_file)))
        self.media_player.setVolume(50)
        self.init_ui()
        self.create_db()
        self.load_scores()

    def init_ui(self):
        self.background_label = QLabel(self)
        pixmap = QPixmap("first_image.png")
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True) #resmi pencere boyutuna göre ayarlıyo
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        #pencere boyutu değişse de ona göre ayarlansın
        self.resizeEvent = self.on_resize
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial;
                font-size: 12pt;
            }
            QLabel {
                color: #333;
                padding: 5px;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
            }
            QPushButton {
                background-color: #14149c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dba102;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                gridline-color: #eee;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #ac87e0;
                color: white;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
            QPushButton#sound_button {
                background-color: #28a745;
                border-radius: 25px;
                min-width: 50px;
                max-width: 50px;
                min-height: 50px;
                max-height: 50px;
                padding: 0;
            }
            QPushButton#sound_button:hover {
                background-color: #218838;
            }
        """)
        #başlık, hoşgeldiniz
        main_title = QLabel("KİM MİLYONER OLMAK İSTER ?")
        main_title.setFont(QFont("Arial", 36, QFont.Bold))
        main_title.setAlignment(Qt.AlignCenter)
        main_title.setStyleSheet("color: orange; padding: 20px; font-size: 30pt; ")

        #kullanıcı giriş bilgileri
        self.name_input = QLineEdit()
        self.surname_input = QLineEdit()
        self.age_input = QLineEdit()

        self.joker_person1_input = QLineEdit()
        self.joker_person2_input = QLineEdit()
        self.joker_person3_input = QLineEdit()

        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        form_layout.addWidget(QLabel("Adınız:"), 0, 0)
        form_layout.addWidget(self.name_input, 0, 1)
        form_layout.addWidget(QLabel("Soyadınız:"), 1, 0)
        form_layout.addWidget(self.surname_input, 1, 1)
        form_layout.addWidget(QLabel("Yaşınız:"), 2, 0)
        form_layout.addWidget(self.age_input, 2, 1)

        #Joker giriş alan
        form_layout.addWidget(QLabel("Telefon Jokeri Kişi 1 (Zorunlu):"), 3, 0)
        form_layout.addWidget(self.joker_person1_input, 3, 1)
        form_layout.addWidget(QLabel("Telefon Jokeri Kişi 2 (İsteğe Bağlı):"), 4, 0)
        form_layout.addWidget(self.joker_person2_input, 4, 1)
        form_layout.addWidget(QLabel("Telefon Jokeri Kişi 3 (İsteğe Bağlı):"), 5, 0)
        form_layout.addWidget(self.joker_person3_input, 5, 1)
        
        #başla butonu
        start_button = QPushButton("Yarışmaya Başla")
        start_button.clicked.connect(self.start_game)
        start_button.setStyleSheet("background-color: #14149c; font-size: 16pt; hover:background-color: #dba102;")

        vbox_user = QVBoxLayout()
        vbox_user.addLayout(form_layout)
        vbox_user.addSpacing(20)
        vbox_user.addWidget(start_button, alignment=Qt.AlignCenter)

        user_widget_inner = QWidget()
        user_widget_inner.setLayout(vbox_user)
        user_widget = QWidget()
        user_widget.setLayout(vbox_user)

        #skor geçmişi tablo hali
        self.score_table = QTableWidget()
        self.score_table.setColumnCount(4)
        self.score_table.setHorizontalHeaderLabels(["ID", "Ad", "Soyad", "Kazanç"])
        self.score_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.score_table.horizontalHeader().setStretchLastSection(True)
        self.score_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        score_layout = QVBoxLayout()
        score_title = QLabel("Skor Geçmişi")
        score_title.setFont(QFont("Arial", 20, QFont.Bold))
        score_title.setAlignment(Qt.AlignCenter)
        score_layout.addWidget(score_title)
        score_layout.addWidget(self.score_table)

        score_widget = QWidget()
        score_widget.setLayout(score_layout)

        #sekmeler için alt sayfalar
        self.pages = QStackedWidget()
        self.pages.addWidget(user_widget)
        self.pages.addWidget(score_widget)

        btn_user = QPushButton("Yeni Yarışmacı")
        btn_scores = QPushButton("Skor Geçmişi")
        btn_user.setFixedWidth(200)
        btn_scores.setFixedWidth(200)
        btn_user.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        btn_scores.clicked.connect(lambda: self.pages.setCurrentIndex(1))

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(btn_user)
        button_layout.addSpacing(20)
        button_layout.addWidget(btn_scores)
        button_layout.addStretch()

       #ana içerik
        main_inner_layout = QVBoxLayout()
        main_inner_layout.addWidget(main_title)
        main_inner_layout.addLayout(button_layout)
        main_inner_layout.addWidget(self.pages)
        main_inner_layout.addStretch() #yukarı doğru itmek için kullandım

        #yatayda
        centered_h_layout = QHBoxLayout()
        centered_h_layout.addStretch()
        centered_h_layout.addLayout(main_inner_layout)
        centered_h_layout.addStretch()

        #dikeyde
        overall_layout = QVBoxLayout(self) # FirstWindow'un ana layout'u
        overall_layout.addStretch()
        overall_layout.addLayout(centered_h_layout)
        overall_layout.addStretch()

        #ses butonu
        self.sound_button = QPushButton()
        self.sound_button.setObjectName("sound_button")
        self.update_sound_button_icon()
        self.sound_button.clicked.connect(self.toggle_music)

        #ses butonu sol alta yerleştirmek için
        bottom_left_container = QWidget(self)
        bottom_left_layout = QVBoxLayout(bottom_left_container)
        bottom_left_layout.addStretch()
        bottom_left_layout.addWidget(self.sound_button, alignment=Qt.AlignBottom | Qt.AlignLeft)
        bottom_left_layout.setContentsMargins(10, 10, 10, 10) 
        self.sound_button.setParent(self)
        self.sound_button.move(10, self.height() - self.sound_button.height() - 10)
        self.resizeEvent = self.on_resize

    def on_resize(self, event):
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.sound_button.move(10, self.height() - self.sound_button.height() - 10)
        event.accept()

    #skor geçmişi için veritabanı
    def create_db(self):
        self.conn = sqlite3.connect("scores.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS skorlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT,
                soyad TEXT,
                kazanc TEXT
            )
        """)
        self.conn.commit()
        
    #skorları tabloya geçirme
    def load_scores(self):
        self.cursor.execute("SELECT * FROM skorlar ORDER BY id DESC")
        records = self.cursor.fetchall()
        self.score_table.setRowCount(len(records))
        for i, row in enumerate(records):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.score_table.setItem(i, j, item)

    #oyuna başlama/eksik alanlar varsa uyarı mesajları
    def start_game(self):
        ad = self.name_input.text().strip()
        soyad = self.surname_input.text().strip()
        yas = self.age_input.text().strip()
        joker_person1 = self.joker_person1_input.text().strip()

        if not ad or not soyad or not yas or not joker_person1:
            QMessageBox.warning(self, "Uyarı", "Lütfen tüm zorunlu alanları doldurunuz.")
            return
        try:
            int(yas)
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Yaş alanı sayı olmalıdır.")
            return
            
        # Joker kişilerini bir liste olarak hazırla
        self.joker_persons = [joker_person1]
        if self.joker_person2_input.text().strip():
            self.joker_persons.append(self.joker_person2_input.text().strip())
        if self.joker_person3_input.text().strip():
            self.joker_persons.append(self.joker_person3_input.text().strip())

    #2.pencereye geçiş
        self.stacked_widget.setCurrentIndex(1)

    def toggle_music(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
        self.update_sound_button_icon()

    def update_sound_button_icon(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            pixmap = QPixmap("sound_on.png") #ses açık
        else:
            pixmap = QPixmap("sound_off.png") #ses kapalı

        if pixmap.isNull():
            pixmap = QPixmap(50, 50)
            pixmap.fill(Qt.gray)
        else:
            pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.sound_button.setIcon(QIcon(pixmap))
        self.sound_button.setIconSize(pixmap.size())

#2.PENCERE
class SecondWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.media_player = QMediaPlayer()
        self.music_file = "game_music.mp3" #2.pencere müzik
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.music_file)))
        self.media_player.setVolume(80)

        self.time_per_question = 60
        self.time_left = self.time_per_question
        self.current_question_index = 0
        self.last_answered_question_prize_index = -1
        self.player_name = ""
        self.player_surname = ""
        self.joker_persons = [] #joker kişilerini tutacak
        self.conn = sqlite3.connect("scores.db")
        self.cursor = self.conn.cursor()
        self.fifty_fifty_used = False # joker takibi- yarı yarıya
        self.phone_joker_used = False #joker takibi - telefon 
        self.audience_joker_used = False #joker takibi- seyirci
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        #ödül kısmı
        self.oduller = [
            "1. 1.000 TL", "2. 2.000 TL", "3. 3.000 TL", "4. 5.000 TL",
            "5. 7.500 TL", "6. 15.000 TL", "7. 30.000 TL", "8. 60.000 TL",
            "9. 125.000 TL", "10. 250.000 TL", "11. 500.000 TL", "12. 1.000.000 TL"
        ]
        self.baraj_sorulari = [1, 6, 11]  #2, 7, 12.sorular

        #Sorular
        self.seviye1_sorular = [
            {"soru": "Halk arasında kullanılan ifadeye göre çok fikir değiştiren insanların hangisi gibi renkten renge girdiği söylenir?", "secenekler": ["Şempanze gibi", "Bukalemun gibi", "Bizon gibi", "Komodo ejderi gibi"], "dogru": "B"},
            {"soru": "Her takımın her maçın başlangıcında sahada kaç futbolcusu olmalıdır?", "secenekler": ["8", "9", "10", "11"], "dogru": "D"},
            {"soru": "Güneş'e en yakın gezegen hangisidir?", "secenekler": ["Venüs", "Merkür", "Mars", "Dünya"], "dogru": "B"},
            {"soru": "Türkiye kaç coğrafi bölgeden oluşur?", "secenekler": ["6", "7", "8", "5"], "dogru": "B"},
            {"soru": "En küçük asal sayı kaçtır?", "secenekler": ["0", "1", "2", "3"], "dogru": "C"},
            {"soru": "Elektrik akımının birimi nedir?", "secenekler": ["Volt", "Amper", "Watt", "Ohm"], "dogru": "B"},
            {"soru": "Halk arasında 'göz değmesini önlemek' amacıyla yaygın olarak kullanılan bir nesnedir?", "secenekler": ["Çan", "Nazar boncuğu", "Tespih", "Anahtar"], "dogru": "B"},
            {"soru": "Hangi organın dört odası vardır?", "secenekler": ["Kalp", "Mide", "Akciğer", "Karaciğer"], "dogru": "A"},
        ] 

        self.seviye2_sorular = [
            {"soru": "DNA'nın açılımı nedir?", "secenekler": ["Deoksiribonükleik Asit", "Dijital Nükleer Asit", "Dinamik Nöroaktif Asit", "Diyot Nöron Aktarıcı"], "dogru": "A"},
            {"soru": "Kahveye batırılmış kedi dili bisküvileri ve mascarpone peyniri ile yapılan İtalyan tatlısının adı nedir?", "secenekler": ["Kedi Pastası", "Trileçe", "Cheescake", "Tiramisu"], "dogru": "D"},
            {"soru": "Dünyanın en büyük okyanusu hangisidir?", "secenekler": ["Atlantik", "Hint", "Pasifik", "Arktik"], "dogru": "C"},
            {"soru": "Fatih Sultan Mehmet’in babası kimdir?", "secenekler": ["I.Mehmet", "II.Murad", "II.Mehmet", "Yıldırım Beyazıt"], "dogru": "B"},
            {"soru": "En uzun nehir hangisidir?", "secenekler": ["Nil", "Amazon", "Yangtze", "Mississippi"], "dogru": "A"},
            {"soru": "İlk çağda yazıyı bulan medeniyet hangisidir?", "secenekler": ["Sümerler", "Hititler", "Urartular", "Asurlar"], "dogru": "A"},
        ]

        self.seviye3_sorular = [
            {"soru": "İnternetin mucidi kimdir?", "secenekler": ["Tim Berners-Lee", "Bill Gates", "Steve Jobs", "Alan Turing"], "dogru": "A"},
            {"soru": "Divan-ı Lügatit Türk adlı eserin yazarı kimdir?", "secenekler": ["Kaşgarlı Mahmut", "Yusuf Has Hacip", "Ali Şir Nevai", "Ahmet Yesevi"], "dogru": "A"},
            {"soru": "Türkiye'nin en uzun nehri hangisidir?", "secenekler": ["Kızılırmak", "Fırat", "Dicle", "Yeşilırmak"], "dogru": "A"},
            {"soru": "Yunan mitolojisinde tanrıların kralı kimdir?", "secenekler": ["Eros", "Zeus", "İlyada", "Herkül"], "dogru": "B"},
            {"soru": "Porsche logosunda hangi hayvan görülebilir?", "secenekler": ["Aslan", "Kaplan", "Boğa", "At"], "dogru": "D"},
            {"soru": "Android uygulamaları geliştirmek için hangi programlama dili sıklıkla kullanılır?", "secenekler": ["Java", "Python", "C++", "C#"], "dogru": "A"},
            {"soru": "Işık hızı saniyede kaç kilometredir?", "secenekler": ["300,000 km/s", "150,000 km/s", "1,000,000 km/s", "500,000 km/s"], "dogru": "A"},
        ]


        self.seviye4_sorular = [
            {"soru": "Penisilini kim keşfetti?", "secenekler": ["Humphry Davy", "Robert Boyle", "Marie Curie", "Alexander Fleming"], "dogru": "D"},
            {"soru": "Hangisi Türkiye'de UNESCO Dünya Mirası Listesi'nde yer alan bir antik kenttir?", "secenekler": ["Çatalhöyük", "Ani Harabeleri", "Göbekli Tepe", "Hepsi"], "dogru": "D"},
            {"soru": "Fizikte 'Schrödinger'in kedisi' deneyi hangi alanla ilgilidir?", "secenekler": ["Mekanik", "Termodinamik", "Kuantum Fiziği", "Optik"], "dogru": "C"},
            {"soru": "Dünyanın en derin noktası neresidir?", "secenekler": ["Mariana Çukuru", "Tonga Çukuru", "Java Çukuru", "Puerto Rico Çukuru"], "dogru": "A"},
            {"soru": "Kuzey Işıkları olarak bilinen doğa olayı hangi gezegenin manyetik alanıyla ilgilidir?", "secenekler": ["Mars", "Merkür", "Dünya", "Uranüs"], "dogru": "C"},
            {"soru": "Türkçedeki 'mukavemet' kelimesi en çok ne anlamda kullanılır?", "secenekler": ["Sabırsızlık", "Direnç", "Hız", "Uyum"], "dogru": "B"},
        ]

        self.seviye5_sorular = [
            {"soru": "Marvel sinematik evreninde 'Kaptan Amerika' karakterini canlandıran oyuncu kimdir?", "secenekler": ["Chris Pratt", "Chris Hemsworth", "Chris Evans", "Robert Downey Jr."], "dogru": "C"},
            {"soru": "Genellikle 'Pop'un Kralı' olarak anılan ve 'Thriller', 'Billie Jean' gibi ikonik hitleriyle tanılan sanatçı kimdir?", "secenekler": ["Justin Bieber", "Micheal Jackson", "George Micheal", "The Weekend"], "dogru": "B"},
            {"soru": "Hangi popüler TV dizisinde Targaryen ve Stark hanedanı yer aldı?", "secenekler": ["Game of Thrones", "House of the Dragon", "The Walking Dead", "Supernatural"], "dogru": "A"},
            {"soru": "Thor hangi Tanrı'nın oğluydu?", "secenekler": ["Odin", "Loki", "Zeus", "Hades"], "dogru": "A"},
            {"soru": "Müzeyyen Senar hangi dönemde ün kazanmıştır?", "secenekler": ["1920'ler", "1940'lar", "1960'lar", "1980'ler"], "dogru": "B"},
            {"soru": "İlk Türk kadın romancı kimdir?", "secenekler": ["Halide Edip Adıvar", "Fatma Aliye Topuz", "Nezihe Muhiddin", "Afife Jale"], "dogru": "B"},
        ]


        self.seviye6_sorular = [
            {"soru": "On kıtadan oluşan İstiklal Marşı'nın tamamında, bu kelimelerden hangisi diğerlerinden daha az geçer?", "secenekler": ["Vatan", "Kan", "Toprak", "Yurt"], "dogru": "C"},
            {"soru": "Hangisi “Dede Korkut Hikayeleri”’ndeki karakterlerden biri değildir?", "secenekler": ["Bala Hatun", "Banu Çiçek", "Bamsı Beyrek", "Bayındır Han"], "dogru": "A"},
            {"soru": "Kur'an-ı Kerim'de hangisi üzerine yemin edilmemiştir?", "secenekler": ["Deniz", "Güneş", "Arı", "Kalem"], "dogru": "C"},
            {"soru": "Cumhurbaşkanlığı forsu ve armasındaki 16 Türk devleti arasında hangisi yoktur?", "secenekler": ["Batı Hun İmparatorluğu", "Harzemşahlar", "Avar İmparatorluğu", "Anadolu Selçuklu Devleti"], "dogru": "D"},
            {"soru": "Herodot'un deneyinde, konuşmayan çocuğun söylediği ilk kelime nedir?", "secenekler": ["Ver", "Anne", "Ekmek", "Su"], "dogru": "C"},
            {"soru": "Bu oyunlardan hangisi 'Başlangıç noktasından geçme, 200 $ alma' ifadesi içerir?", "secenekler": ["Pac-Man", "Tabu", "Monopoly", "Mlyoner"], "dogru": "C"},
            {"soru": "Hangi hayvanın beyni vücut ağırlığına oranla en büyüktür?", "secenekler": ["İnsan", "Fare", "Fil", "Karınca"], "dogru": "D"},
            {"soru": "Giza'da kaç tane piramit yapılmıştır?", "secenekler": ["2", "3", "4", "5"], "dogru": "B"},
] 

        self.sorular = []  
        self.init_ui()

    def init_ui(self):
        self.background_label = QLabel(self)
        pixmap = QPixmap("second_image.jpg")
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True) #resmi pencere boyutuna göre ayarlıyo
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.lower() 
        self.resizeEvent = self.on_resize
        self.setStyleSheet("""
            QWidget {
                background-color: #1a2a40;
                color: white;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11pt;
            }
            QLabel#question_label {
                background-color: #201f80;
                padding: 20px;
                border-radius: 10px;
                font-size: 16pt;
                font-weight: bold;
                color: white;
                text-align: center;
            }
            QPushButton {
                background-color: #201f80;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px 25px;
                font-size: 14pt;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #0056b3; /*koyu mavi */
            }
            QPushButton#quit_button {
                background-color: #e81324;
            }
            QPushButton#quit_button:hover {
                background-color: #c82333;
            }
            QProgressBar {
                border: 2px solid #007bff; /*süre*/
                border-radius: 5px;
                text-align: center;
                background-color: #e0e0e0;
                color: black;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 3px;
            }
            QLabel[highlight="true"] {
                background-color: #ba6330;
                color: black;
                border: 2px solid #ba6330;
                border-radius: 5px;
            }
            QLabel[safeline="true"] {
                background-color: #33789e; /* Cyan  */
                color: white;
                border: 2px solid #33789e;
                border-radius: 5px;
            }
            QLabel {
                padding: 5px;
            }
            QPushButton#sound_button {
                background-color: #28a745;
                border-radius: 25px;
                min-width: 50px;
                max-width: 50px;
                min-height: 50px;
                max-height: 50px;
                padding: 0;
            }
            QPushButton#sound_button:hover {
                background-color: #218838;
            }
        """)
        # sol-- jokerler,ödüller,ses simgesi
        # sağ-- sorular, geri çekil butonu, süre çubuğı

        # sol panel
        main_layout = QHBoxLayout()
        sol_layout = QVBoxLayout()
        sol_layout.setSpacing(10)
        sol_layout.setContentsMargins(10, 10, 10, 10)

        # jokerler
        joker_label = QLabel("Joker Hakları")
        joker_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        joker_label.setAlignment(Qt.AlignCenter)
        sol_layout.addWidget(joker_label)

        joker_layout = QHBoxLayout()
        joker_layout.setSpacing(15)
        self.joker_buttons = []

        # Seyirci jokeri
        btn_audience = QPushButton()
        pixmap_audience = QPixmap("person_joker.png")
        if pixmap_audience.isNull():
            pixmap_audience = QPixmap(40, 40)
            pixmap_audience.fill(Qt.gray)
        else:
            pixmap_audience = pixmap_audience.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        btn_audience.setIcon(QIcon(pixmap_audience))
        btn_audience.setIconSize(pixmap_audience.size())
        btn_audience.setFixedSize(60, 60)
        btn_audience.setStyleSheet("background-color: #6c757d; hover:background-color: #b31942;border-radius: 30px; border: 2px solid #5a6268;")
        btn_audience.clicked.connect(self.audience_lifeline) # Audience joker clicked
        self.joker_buttons.append(btn_audience)
        joker_layout.addWidget(btn_audience)

        # Yarı Yarıya jokeri
        btn_fifty_fifty = QPushButton()
        pixmap_fifty_fifty = QPixmap("50_joker.png")
        if pixmap_fifty_fifty.isNull():
            pixmap_fifty_fifty = QPixmap(40, 40)
            pixmap_fifty_fifty.fill(Qt.gray)
        else:
            pixmap_fifty_fifty = pixmap_fifty_fifty.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        btn_fifty_fifty.setIcon(QIcon(pixmap_fifty_fifty))
        btn_fifty_fifty.setIconSize(pixmap_fifty_fifty.size())
        btn_fifty_fifty.setFixedSize(60, 60)
        btn_fifty_fifty.setStyleSheet("background-color: #6c757d; hover:background-color: #b31942; border-radius: 30px; border: 2px solid #5a6268;")
        btn_fifty_fifty.clicked.connect(self.fifty_fifty_lifeline) # Bağlantı eklendi
        self.joker_buttons.append(btn_fifty_fifty)
        joker_layout.addWidget(btn_fifty_fifty)

        #telefon jokeri 
        self.btn_phone = QPushButton()
        pixmap_phone = QPixmap("phone_call_joker.png")
        if pixmap_phone.isNull():
            pixmap_phone = QPixmap(40, 40)
            pixmap_phone.fill(Qt.gray)
        else:
            pixmap_phone = pixmap_phone.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.btn_phone.setIcon(QIcon(pixmap_phone))
        self.btn_phone.setIconSize(pixmap_phone.size())
        self.btn_phone.setFixedSize(60, 60)
        self.btn_phone.setStyleSheet("background-color: #6c757d;hover:background-color: #b31942;  border-radius: 30px; border: 2px solid #5a6268;")
        self.btn_phone.clicked.connect(self.phone_lifeline) 
        self.joker_buttons.append(self.btn_phone)
        joker_layout.addWidget(self.btn_phone)

        sol_layout.addLayout(joker_layout)
        sol_layout.addSpacing(20)

        self.odul_labels = []

        # Ödülleri ters sırayla ekliyoruz
        for i, odul in reversed(list(enumerate(self.oduller))):
            lbl = QLabel(odul)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl.setFont(QFont("Segoe UI", 12))
            if i in self.baraj_sorulari:
                lbl.setProperty("safeline", "true")
                lbl.setStyleSheet("border: 1px solid #100f47; padding: 8px; background-color: #17a2b8; color: white; font-weight: bold; border-radius: 5px;")
            else:
                lbl.setStyleSheet("border: 1px solid #100f47; padding: 8px; background-color: #34495e; color: white; border-radius: 5px;")

            self.odul_labels.insert(0, lbl)
            sol_layout.addWidget(lbl)

        sol_layout.addStretch()

        # Ses butonu
        self.sound_button = QPushButton()
        self.sound_button.setObjectName("sound_button")
        self.update_sound_button_icon()
        self.sound_button.clicked.connect(self.toggle_music)

        # Ses butonunu sol alta yerleştiriyoruz
        bottom_left_layout = QHBoxLayout()
        bottom_left_layout.addWidget(self.sound_button)
        bottom_left_layout.addStretch() # Butonu sola yaslar

        sol_layout.addLayout(bottom_left_layout) # Sol layout'a ekle

        main_layout.addLayout(sol_layout, 1)

        # Sağ panel
        sag_layout = QVBoxLayout()
        sag_layout.setSpacing(20)
        sag_layout.setContentsMargins(20, 20, 20, 20)

        self.progress = QProgressBar()
        self.progress.setMaximum(self.time_per_question)
        self.progress.setValue(self.time_left)
        self.progress.setTextVisible(True)
        self.progress.setFont(QFont("Segoe UI", 10, QFont.Bold))
        sag_layout.addWidget(self.progress)

        self.question_label = QLabel("Soru burada görünecek.")
        self.question_label.setObjectName("question_label")
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(Qt.AlignCenter)
        sag_layout.addWidget(self.question_label)

        self.choices_layout = QGridLayout()
        self.choices_layout.setSpacing(15)
        self.choice_buttons = []
        for i in range(4):
            btn = QPushButton(f"Seçenek {chr(65 + i)}")
            btn.clicked.connect(self.answer_clicked)
            self.choice_buttons.append(btn)
            self.choices_layout.addWidget(btn, i // 2, i % 2)
        sag_layout.addLayout(self.choices_layout)

        back_button = QPushButton("Yarışmadan Çekil")
        back_button.setObjectName("quit_button")
        back_button.clicked.connect(self.back_button_clicked)
        sag_layout.addWidget(back_button, alignment=Qt.AlignRight)

        main_layout.addLayout(sag_layout, 3)
        self.setLayout(main_layout)
        self.mevcut_odulu_vurgula()

    def on_resize(self, event):
        #pencere boyutuna göre resim ve sesin büyüklüğüünü ayarla
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.sound_button.move(10, self.height() - self.sound_button.height() - 10)
        event.accept()

    def levele_gore_soru_secimi(self):
        seviye1_secim = random.sample(self.seviye1_sorular, 2)
        seviye2_secim = random.sample(self.seviye2_sorular, 2)
        seviye3_secim = random.sample(self.seviye3_sorular, 2)
        seviye4_secim = random.sample(self.seviye4_sorular, 2)
        seviye5_secim = random.sample(self.seviye5_sorular, 2)
        seviye6_secim = random.sample(self.seviye6_sorular, 2)

        self.questions = seviye1_secim + seviye2_secim+seviye3_secim+seviye4_secim+seviye5_secim+seviye6_secim

    # o anki sorunun ödülünü vurgulama
    def mevcut_odulu_vurgula(self):
        for i, lbl in enumerate(self.odul_labels):
            if i in self.baraj_sorulari:
                lbl.setStyleSheet("border: 1px solid #33789e; padding: 8px; background-color: #17a2b8; color: white; font-weight: bold; border-radius: 5px;")
            else:
                lbl.setStyleSheet("border: 1px solid #9ec7de; padding: 8px; background-color: #34495e; color: white; border-radius: 5px;")

        if self.current_question_index < len(self.oduller):
            current_lbl = self.odul_labels[self.current_question_index]
            current_lbl.setProperty("highlight", "true")
            current_lbl.setStyleSheet("border: 2px solid #ba6330; padding: 8px; background-color: #ffc107; color: black; font-weight: bold; border-radius: 5px;")
            current_lbl.style().polish(current_lbl)

    # ekrana soruyu yazdırma + butonlara şık yerleştirme
    def start_question(self):
        self.mevcut_odulu_vurgula()

        if self.current_question_index >= len(self.questions):
            self.game_over(win=True)
            return

        soru = self.questions[self.current_question_index]
        self.question_label.setText(soru["soru"])

        for i, btn in enumerate(self.choice_buttons):
            btn.setText(f"{chr(65+i)}: {soru['secenekler'][i]}")
            btn.setEnabled(True)
            btn.setStyleSheet("background-color:#201f80; hover:background-color: #100f47; color: white; border: none; border-radius: 10px; padding: 15px 25px; font-size: 14pt; font-weight: bold; min-width: 150px;")

        # 7. sorudan itibaren süreyi kaldır
        if self.current_question_index >= 7:
            self.timer.stop()
            self.progress.hide()
        else:
            self.progress.show() 
            self.time_left = self.time_per_question
            self.progress.setMaximum(self.time_per_question)
            self.progress.setValue(self.time_left)
            self.timer.start(1000)

    # süre akışı 1er saniye
    def update_timer(self):
        self.time_left -= 1
        self.progress.setValue(self.time_left)
        if self.time_left <= 0:
            self.timer.stop()
            QMessageBox.information(self, "Süre Doldu", "Süreniz doldu! Yanlış cevap kabul edildi.")
            self.game_over(win=False)

    # cevap kontrolleri
    def answer_clicked(self):
        sender = self.sender()
        secilen_harf = sender.text()[0]
        dogru_harf = self.questions[self.current_question_index]["dogru"]

        self.timer.stop()

        if secilen_harf == dogru_harf:
            QMessageBox.information(self, "Doğru!", "Tebrikler, doğru cevap!")
            
            # Doğru cevap verildiğinde, bir önceki (yani şu anki) sorunun ödül seviyesini kaydet
            self.last_answered_question_prize_index = self.current_question_index 

            self.current_question_index += 1
            if self.current_question_index >= len(self.questions):
                self.game_over(win=True)
            else:
                self.start_question()
        else:
            QMessageBox.warning(self, "Yanlış!", f"Yanlış cevap! Doğru cevap: {dogru_harf}: {self.questions[self.current_question_index]['secenekler'][ord(dogru_harf)-65]}.")
            self.game_over(win=False)

    # yarı yarıya joker hakkı
    def fifty_fifty_lifeline(self):
        if self.fifty_fifty_used:
            QMessageBox.warning(self, "Joker Hakkı", "Yarı yarıya jokerini zaten kullandınız.")
            return

        current_question = self.questions[self.current_question_index]
        correct_answer_index = ord(current_question["dogru"]) - ord('A')

        incorrect_indices = [i for i in range(4) if i != correct_answer_index and self.choice_buttons[i].isEnabled()]
        # En fazla 2 yanlış cevap silinmeli
        num_to_remove = min(2, len(incorrect_indices))
        if num_to_remove > 0:
            random_incorrect_to_remove = random.sample(incorrect_indices, num_to_remove)

            # random gelen yanlış cevapları sil
            for i in random_incorrect_to_remove:
                self.choice_buttons[i].setEnabled(False)
                self.choice_buttons[i].setText("")

        self.fifty_fifty_used = True
        self.joker_buttons[1].setEnabled(False)
        QMessageBox.information(self, "Yarı Yarıya", "İki yanlış cevap kaldırıldı.")

    # Telefon jokeri
    def phone_lifeline(self):
        if self.phone_joker_used:
            QMessageBox.warning(self, "Joker Hakkı", "Telefon jokerini zaten kullandınız.")
            return

        if not self.joker_persons:
            QMessageBox.warning(self, "Joker Hakkı", "Tanımlanmış joker kişi bulunmamaktadır. Lütfen ilk ekranda en az bir joker kişi tanımlayın.")
            return

        person, ok = QInputDialog.getItem(self, "Telefonla Joker", "Kimi aramak istersiniz?", self.joker_persons, 0, False)

        if ok and person:
            current_question = self.questions[self.current_question_index]
            correct_answer_index = ord(current_question["dogru"]) - ord('A')
            correct_answer_text = current_question["secenekler"][correct_answer_index]

            roll = random.randint(1, 10)
            response_text = ""
            #telefon jokeri cevap olasılıkları
            if roll <= 1:  # 1 gelirse cevap vermeesin
                response_text = f"Merhaba, ben {person}. Üzgünüm, bu konu hakkında hiçbir bilgim yok."
            elif roll <= 3:  # 2 veya 3 gelirse random cevap versin
                available_choices = [i for i in range(len(current_question["secenekler"])) if self.choice_buttons[i].isEnabled()]
                if available_choices:
                    random_choice_index = random.choice(available_choices)
                    random_answer_text = current_question["secenekler"][random_choice_index]
                    response_text = f"Merhaba, ben {person}. Emin değilim ama bence cevap '{random_answer_text}' olmalı."
                else: 
                    response_text = f"Merhaba, ben {person}. Hiç emin değilim ama tek kalan seçenek '{correct_answer_text}' gibi görünüyor."
            else:  # 4,5,6,7,8,9,10 gelirse kesinlikle doğru cevabı versin
                response_text = f"Merhaba, ben {person}. Cevap kesinlikle '{correct_answer_text}'olmalı, eminim!"

            QMessageBox.information(self, f"{person} Cevabı", response_text)
            self.phone_joker_used = True
            self.btn_phone.setEnabled(False)

    def audience_lifeline(self):
        if self.audience_joker_used:
            QMessageBox.warning(self, "Joker Hakkı", "Seyirci jokerini zaten kullandınız.")
            return

        current_question = self.questions[self.current_question_index]
        correct_answer_index = ord(current_question["dogru"]) - ord('A')
        choices = [f"{chr(65+i)}" for i in range(4)]
        percentages = [0] * 4 

        # doğru cevabı %30-35 arası random yapsın
        correct_vote = random.randint(30, 35) 
        percentages[correct_answer_index] = correct_vote

        remaining_vote = 100 - correct_vote
        incorrect_indices = [i for i in range(4) if i != correct_answer_index]

        #Kalan yüzdeyi diğer seçeneklere dağıtsın
        incorrect_options_percentages = []
        if len(incorrect_indices) > 0:
            #yalnış seçenkelerin ort
            avg_incorrect_vote = remaining_vote / len(incorrect_indices)
            
            for _ in range(len(incorrect_indices)):
                #ort. civarını sapmayla
                inc_options_range_min = max(1, int(avg_incorrect_vote - 7)) #negatif olmasın 
                inc_options_range_max = min(remaining_vote, int(avg_incorrect_vote + 7)) 
                inc_options_range_max = max(inc_options_range_min, inc_options_range_max)
                
                inc_votes_val = random.randint(inc_options_range_min, inc_options_range_max)
                incorrect_options_percentages.append(inc_votes_val)
            
            current_inc_sum = sum(incorrect_options_percentages)
            diff_inc = remaining_vote - current_inc_sum
            
            for i in range(len(incorrect_options_percentages)):
                if diff_inc == 0:
                    break
                if diff_inc > 0:
                    incorrect_options_percentages[i] += 1
                    diff_inc -= 1
                elif diff_inc < 0 and incorrect_options_percentages[i] > 1: # Avoid making percentage negative
                    incorrect_options_percentages[i] -= 1
                    diff_inc += 1
            
            if diff_inc != 0 and len(incorrect_options_percentages) > 0:
                incorrect_options_percentages[0] += diff_inc
            incorrect_options_percentages = [max(0, v) for v in incorrect_options_percentages]

            for i, idx in enumerate(incorrect_indices):
                percentages[idx] = incorrect_options_percentages[i]
        
        #yüzdelerin toplamı 100 olmalı kontrolü
        final_sum = sum(percentages)
        if final_sum != 100:
            diff_final = 100 - final_sum
            percentages[correct_answer_index] += diff_final
            percentages[correct_answer_index] = max(0, percentages[correct_answer_index]) # Ensure non-negative

        percentages = [int(p) for p in percentages]
        
        #grafiği görüntülemek için kutu
        dialog = QDialog(self)
        dialog.setWindowTitle("Seyirci Joker Hakkı Sonuçları")
        dialog_layout = QVBoxLayout()

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(choices, percentages, color=['blue', 'green', 'red', 'purple'])
        ax.set_ylim(0, 100)
        ax.set_title("Seyircilerin Cevap Yüzdeleri")
        ax.set_ylabel("Yüzde (%)")
        ax.set_xlabel("Seçenekler")

        for i, v in enumerate(percentages):
            ax.text(i, v + 2, f"{v}%", ha='center', va='bottom') 

        canvas = FigureCanvas(fig)
        dialog_layout.addWidget(canvas)

        dialog_message = QLabel("Seyircilerin verdiği cevap yüzdeleri aşağıdaki gibidir")
        dialog_message.setAlignment(Qt.AlignCenter)
        dialog_layout.addWidget(dialog_message)

        dialog.setLayout(dialog_layout)
        dialog.exec_()
        plt.close(fig) 
        self.audience_joker_used = True
        self.joker_buttons[0].setEnabled(False) # Seyirci butonu

    # oyun bitişi ve kazanılan ödülün bildirilişi
    def game_over(self, win: bool):
        self.timer.stop()
        kazanc = "0 TL"
        if win:
            kazanc = self.oduller[-1] # Son ödülü al
            msg = f"Tebrikler! Tüm soruları bildiniz ve {kazanc} kazandınız!"
        else:
            if self.last_safe_index >= 0:
                kazanc = self.oduller[self.last_safe_index] # Baraj sorusunda kalınan ödül
            msg = f"Yarışma sona erdi. {kazanc} kazandınız."

        self.save_score(kazanc)
        self.reset_game_state()

        #3. pencereye geçiş 
        if hasattr(self.stacked_widget.widget(2), 'display_score'):
            self.stacked_widget.widget(2).display_score(kazanc)
        self.stacked_widget.setCurrentIndex(2) 

    # skoru kaydetme
    def save_score(self, kazanc):
        self.cursor.execute("INSERT INTO skorlar (ad, soyad, kazanc) VALUES (?, ?, ?)",
                            (self.player_name, self.player_surname, kazanc))
        self.conn.commit()
        if hasattr(self.stacked_widget.widget(0), 'load_scores'):
            self.stacked_widget.widget(0).load_scores()

    # oyuna tekrar döndürür
    def reset_game_state(self):
        self.current_question_index = 0
        self.last_safe_index = -1
        self.timer.stop()
        self.fifty_fifty_used = False
        self.phone_joker_used = False 
        self.audience_joker_used = False
        # Tüm joker butonlarını tekrar etkinleştir
        for btn in self.joker_buttons:
            btn.setEnabled(True)
        # Cevap butonlarını da sıfırla
        for btn in self.choice_buttons:
            btn.setText("")
            btn.setEnabled(True)
        self.progress.show() # Zamanlayıcıyı tekrar göster
        self.mevcut_odulu_vurgula() 

    # geri çekilme butonu
    def back_button_clicked(self):
        self.timer.stop() # Zamanlayıcıyı durdur
        reply = QMessageBox.question(
            self,
            "Yarışmadan Çekil",
            "Yarışmadan çekilmek istediğinize emin misiniz? Çekilirseniz, bir önceki doğru cevapladığınız sorunun ödülünü kazanırsınız.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            kazanc = "0 TL" # Başlangıçta kazanç 0 TL olarak ayarla

            # last_answered_question_prize_index -1 değilse (yani en az bir soru doğru cevaplanmışsa)
            if self.last_answered_question_prize_index >= 0:
                kazanc = self.oduller[self.last_answered_question_prize_index]
            
            # Eğer kazanç stringi "X. Y TL" formatındaysa, sadece "Y TL" kısmını almak için:
            if ': ' in kazanc:
                kazanc_text_only = kazanc.split(': ')[1]
            else: # Zaten sadece "0 TL" gibi bir ifade ise
                kazanc_text_only = kazanc

            QMessageBox.information(self, "Yarışmadan Çekildiniz", f"{kazanc_text_only} kazandınız.")
            self.save_score(kazanc_text_only) # Veritabanına sadece para miktarını kaydet
            self.reset_game_state()
            if hasattr(self.stacked_widget.widget(2), 'display_score'):
                self.stacked_widget.widget(2).display_score(kazanc_text_only)
            self.stacked_widget.setCurrentIndex(2)
        else:
            # Kullanıcı çekilmek istemezse süreyi tekrar devam ettir (sadece 7. sorudan önce ise)
            if self.current_question_index < 7: # Zamanlayıcının görünür olduğu sorular için
                self.timer.start(1000)

    def set_stacked_widget(self, stacked_widget):
        self.stacked_widget = stacked_widget

    def toggle_music(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
        self.update_sound_button_icon()

    def update_sound_button_icon(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            pixmap = QPixmap("sound_on.png")
        else:
            pixmap = QPixmap("sound_off.png")

        if pixmap.isNull():
            pixmap = QPixmap(50, 50)
            pixmap.fill(Qt.gray)
        else:
            pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.sound_button.setIcon(QIcon(pixmap))
        self.sound_button.setIconSize(pixmap.size())

class ThirdWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.media_player = QMediaPlayer()
        self.music_file = "end_music.mp3" # Yeni müzik dosyası
        if QUrl.fromLocalFile(self.music_file).isValid():
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.music_file)))
        else:
            print(f"Uyarı: '{self.music_file}' müzik dosyası bulunamadı.")
        self.media_player.setVolume(60)
        self.init_ui()

    def init_ui(self):
        #arka plan resmi için
        self.background_label = QLabel(self)
        pixmap = QPixmap("first_image.png")
        if not pixmap.isNull():
            self.background_label.setPixmap(pixmap)
            self.background_label.setScaledContents(True)
        else:
            print("Uyarı: 'image.jpg' arka plan resmi bulunamadı. Arka plan rengi kullanılacak.")
            self.background_label.setStyleSheet("background-color: #2c3e50;") 
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.lower() #resmi widgetların arkasına koyalım

        self.resizeEvent = self.on_resize

        self.setStyleSheet("""
            QWidget {
                background-color: #dfe6ed;
                color: white;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14pt;
            }
            QLabel#title_label {
                font-size: 36pt;
                font-weight: bold;
                color: orange;
                margin-bottom: 20px;
            }
            QLabel#score_label {
                font-size: 48pt;
                font-weight: bold;
                color: orange;
                margin-top: 30px;
                margin-bottom: 40px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px 30px;
                font-size: 18pt;
                font-weight: bold;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton#exit_button {
                background-color: #e74c3c;
            }
            QPushButton#exit_button:hover {
                background-color: #c0392b;
            }
            QPushButton#sound_button {
                background-color: #28a745;
                border-radius: 25px;
                min-width: 50px;
                max-width: 50px;
                min-height: 50px;
                max-height: 50px;
                padding: 0;
            }
            QPushButton#sound_button:hover {
                background-color: #218838;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(50, 50, 50, 50)

        title_label = QLabel("Oyun Bitti!")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        self.score_label = QLabel("Kazancınız: 0 TL")
        self.score_label.setObjectName("score_label")
        self.score_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.score_label)

        play_again_button = QPushButton("Tekrar Oyna")
        play_again_button.clicked.connect(self.play_again)
        main_layout.addWidget(play_again_button)

        exit_game_button = QPushButton("Oyundan Çık")
        exit_game_button.setObjectName("exit_button")
        exit_game_button.clicked.connect(self.exit_game)
        main_layout.addWidget(exit_game_button)

        # Ses butonu
        self.sound_button = QPushButton()
        self.sound_button.setObjectName("sound_button")
        self.update_sound_button_icon()
        self.sound_button.clicked.connect(self.toggle_music)
        self.sound_button.setParent(self)
        self.sound_button.move(10, self.height() - self.sound_button.height() - 10)


    def on_resize(self, event):
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.sound_button.move(10, self.height() - self.sound_button.height() - 10)
        event.accept()

    def display_score(self, kazanc):
        self.score_label.setText(f"Kazancınız: {kazanc}")

    def play_again(self):
        self.stacked_widget.setCurrentIndex(0)

    def exit_game(self):
        #Uygulamayı kapat
        QApplication.instance().quit()

    def toggle_music(self):
        #sesi durakla/oynat
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
        self.update_sound_button_icon()

    def update_sound_button_icon(self):
        # Ses butonu ikonu
        if self.media_player.state() == QMediaPlayer.PlayingState:
            pixmap = QPixmap("sound_on.png")
        else:
            pixmap = QPixmap("sound_off.png")

        if pixmap.isNull():
            print("Uyarı: Ses ikonu dosyası bulunamadı. Varsayılan gri kare kullanılacak.")
            pixmap = QPixmap(50, 50)
            pixmap.fill(Qt.gray)
        else:
            pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.sound_button.setIcon(QIcon(pixmap))
        self.sound_button.setIconSize(pixmap.size())

# tüm pencere geçişleri, yönetimi
class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.first = FirstWindow(self)
        self.second = SecondWindow()
        self.third = ThirdWindow(self)
        self.second.set_stacked_widget(self)

        self.addWidget(self.first)
        self.addWidget(self.second)
        self.addWidget(self.third)

        self.setWindowTitle("Kim Milyoner Olmak İster?")
        self.resize(1000, 750)
        self.first.media_player.play()# Uygulama başladığında ilk pencerenin müziğini çal

    def setCurrentIndex(self, index: int) -> None:
        current_window = self.currentWidget()
        target_window = self.widget(index)
        if hasattr(current_window, 'media_player') and current_window.media_player.state() == QMediaPlayer.PlayingState:
            current_window.media_player.pause()

        super().setCurrentIndex(index)

        if hasattr(target_window, 'media_player'):
            if target_window.media_player.state() != QMediaPlayer.PlayingState:
                if not QUrl.fromLocalFile(target_window.music_file).isValid():
                    print(f"Müzik dosyası bulunamadı {type(target_window).__name__}: {target_window.music_file}")
                target_window.media_player.play()

        self.first.update_sound_button_icon()
        self.second.update_sound_button_icon()
        self.third.update_sound_button_icon()


        if index == 1:
            first_window = self.widget(0)
            self.second.player_name = first_window.name_input.text()
            self.second.player_surname = first_window.surname_input.text()

            self.second.joker_persons = first_window.joker_persons

            self.second.levele_gore_soru_secimi()
            self.second.start_question()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.showMaximized()
    sys.exit(app.exec_())