import sys
import sqlite3
import random
import logging
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QStackedWidget, QMessageBox, QProgressBar, QGridLayout,QHeaderView, QInputDialog,QDialog) 
from PyQt5.QtCore import Qt, QTimer,QUrl, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas    

#log yağılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='game_log.txt', # Log dosyasının adı
    filemode='a'
)
logger = logging.getLogger(__name__)

#1.PENCERE
class FirstWindow(QWidget):
    player_info_signal = pyqtSignal(str, str, list)
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.joker_persons = []
        self.media_player = QMediaPlayer()
        self.music_file = "first_music.mp3"
        if QUrl.fromLocalFile(self.music_file).isValid():
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.music_file)))
        else:
            print(f"Uyarı: '{self.music_file}' müzik dosyası bulunamadı.")
            logger.warning(f"Müzik dosyası bulunamadı: {self.music_file}") 
        self.media_player.setVolume(50)
        self.init_ui()
        self.init_db()
        self.load_scores()

    def init_db(self):
        try:
            self.conn = sqlite3.connect('milyoner_oyunu.db')
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
            logger.info("Veritabanı bağlantısı kuruldu ve skorlar tablosu kontrol edildi.")
        except sqlite3.Error as e:
            logger.error(f"Veritabanı hatası: {e}")
            QMessageBox.critical(self, "Veritabanı Hatası", f"Veritabanına bağlanılamadı veya tablo oluşturulamadı: {e}")

    def init_ui(self):
        self.background_label = QLabel(self)
        pixmap = QPixmap("image.jpg")
        if not pixmap.isNull():
            self.background_label.setPixmap(pixmap)
            self.background_label.setScaledContents(True)
        else:
            print("Uyarı: 'image.jpg' arka plan resmi bulunamadı. Arka plan rengi kullanılacak.")
            logger.warning("Arka plan resmi 'image.jpg' bulunamadı.") 
            self.background_label.setStyleSheet("background-color: #f0f0f0;") 
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.lower() 
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

        user_widget = QWidget()
        user_widget.setLayout(vbox_user)

        #skor geçmişi tablo hali
        self.scores_table = QTableWidget()
        self.scores_table.setColumnCount(4)
        self.scores_table.setHorizontalHeaderLabels(["ID", "Ad", "Soyad", "Kazanç"])
        self.scores_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.scores_table.horizontalHeader().setStretchLastSection(True)
        self.scores_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        score_layout = QVBoxLayout()
        score_title = QLabel("Skor Geçmişi")
        score_title.setFont(QFont("Arial", 20, QFont.Bold))
        score_title.setAlignment(Qt.AlignCenter)
        score_layout.addWidget(score_title)
        score_layout.addWidget(self.scores_table)

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

        self.sound_button.setParent(self) 
        self.sound_button.move(10, self.height() - self.sound_button.height() - 10)

    def on_resize(self, event):
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.sound_button.move(10, self.height() - self.sound_button.height() - 10)
        event.accept()

    def load_scores(self):
        self.cursor.execute("SELECT * FROM skorlar ORDER BY id DESC")
        records = self.cursor.fetchall()
        self.scores_table.setRowCount(len(records))
        for i, row in enumerate(records):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.scores_table.setItem(i, j, item)

    #oyuna başlama/eksik alanlar varsa uyarı mesajları
    def start_game(self):
        ad = self.name_input.text().strip()
        soyad = self.surname_input.text().strip()
        yas = self.age_input.text().strip()
        joker_person1 = self.joker_person1_input.text().strip()

        if not ad or not soyad or not yas or not joker_person1:
            QMessageBox.warning(self, "Uyarı", "Zorunlu alanları doldurunuz.")
            logger.warning("Kullanıcı bilgileri eksik bırakıldı. Oyun başlatılamadı.") # Loglama eklendi
            return

        try:
            int(yas)
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Yaş alanı sayı olmalıdır.")
            logger.warning(f"Yaş alanı geçersiz girildi: {yas}. Oyun başlatılamadı.") # Loglama eklendi
            return
            
        logger.info(f"Yeni oyun başlatıldı. Oyuncu: {ad} {soyad}, Yaş: {yas}")
        joker_persons_list = [joker_person1]
        if self.joker_person2_input.text().strip():
            joker_persons_list.append(self.joker_person2_input.text().strip())
        if self.joker_person3_input.text().strip():
            joker_persons_list.append(self.joker_person3_input.text().strip())
        self.player_info_signal.emit(ad, soyad, joker_persons_list)
        #2.pencereye geçiş
        self.stacked_widget.setCurrentIndex(1)

    def toggle_music(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            logger.info("Müzik duraklatıldı (FirstWindow).")
        else:
            self.media_player.play()
            logger.info("Müzik oynatılıyor (FirstWindow).")
        self.update_sound_button_icon()

    def update_sound_button_icon(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            pixmap = QPixmap("sound_on.png") #ses açık
        else:
            pixmap = QPixmap("sound_off.png") #ses kapalı

        if pixmap.isNull():
            print("Uyarı: Ses ikonu dosyası bulunamadı. Varsayılan gri kare kullanılacak.")
            logger.warning("Ses ikonu dosyası bulunamadı. Varsayılan kullanılacak.")
            pixmap = QPixmap(50, 50)
            pixmap.fill(Qt.gray)
        else:
            pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.sound_button.setIcon(QIcon(pixmap))
        self.sound_button.setIconSize(pixmap.size())

#2.PENCERE
class SecondWindow(QWidget):
    def __init__(self,stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.media_player = QMediaPlayer()
        self.music_file = "game_music.mp3" #2.pencere müzik
        if QUrl.fromLocalFile(self.music_file).isValid():
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.music_file)))
        else:
            print(f"Uyarı: '{self.music_file}' müzik dosyası bulunamadı.")
            logger.warning(f"Müzik dosyası bulunamadı: {self.music_file}") 
        self.media_player.setVolume(80)

        # Doğru ve yanlış cevap ses efektleri için yeni QMediaPlayer nesneleri
        self.correct_sound_player = QMediaPlayer()
        self.correct_sound_file = "correct_answer.mp3" # Doğru cevap sesi dosyası
        if QUrl.fromLocalFile(self.correct_sound_file).isValid():
            self.correct_sound_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.correct_sound_file)))
        else:
            print(f"Uyarı: '{self.correct_sound_file}' müzik dosyası bulunamadı.")
            logger.warning(f"Doğru cevap sesi dosyası bulunamadı: {self.correct_sound_file}")
        self.correct_sound_player.setVolume(100) # Ses seviyesini ayarlayabilirsiniz

        self.incorrect_sound_player = QMediaPlayer()
        self.incorrect_sound_file = "incorrect_answer.mp3" # Yanlış cevap sesi dosyası
        if QUrl.fromLocalFile(self.incorrect_sound_file).isValid():
            self.incorrect_sound_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.incorrect_sound_file)))
        else:
            print(f"Uyarı: '{self.incorrect_sound_file}' müzik dosyası bulunamadı.")
            logger.warning(f"Yanlış cevap sesi dosyası bulunamadı: {self.incorrect_sound_file}") 
        self.incorrect_sound_player.setVolume(100)

        self.time_per_question = 60
        self.time_left = self.time_per_question
        self.current_question_index = 0
        self.last_safe_index = -1 
        self.player_name = ""
        self.player_surname = ""
        self.joker_persons = []
        self.conn = sqlite3.connect("scores.db")
        self.cursor = self.conn.cursor()

        self.fifty_fifty_used = False # joker takibi- yarı yarıya
        self.phone_joker_used = False #joker takibi - telefon 
        self.audience_joker_used = False #joker takibi- seyirci
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        #ödül kısmı
        self.oduller = [
            "1.000 TL", "2.000 TL", "3.000 TL", "5.000 TL",
            "7.500 TL", "15.000 TL", "30.000 TL", "60.000 TL",
            "125.000 TL", "250.000 TL", "500.000 TL", "1.000.000 TL"
        ]
        self.baraj_sorulari = [1, 6, 11]  #2, 7, 12.sorular

        # Müzik ve ses efektleri
        self.media_player = QMediaPlayer()
        self.music_file = "game_music.mp3"
        if QUrl.fromLocalFile(self.music_file).isValid():
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.music_file)))
        else:
            print(f"Uyarı: '{self.music_file}' müzik dosyası bulunamadı.")
            logger.warning(f"Müzik dosyası bulunamadı: {self.music_file}")
        self.media_player.setVolume(50)

        self.correct_sound_player = QMediaPlayer()
        correct_sound_file = "correct_answer.mp3"
        if QUrl.fromLocalFile(correct_sound_file).isValid():
            self.correct_sound_player.setMedia(QMediaContent(QUrl.fromLocalFile(correct_sound_file)))
        else:
            print(f"Uyarı: '{correct_sound_file}' ses dosyası bulunamadı.")
            logger.warning(f"Ses dosyası bulunamadı: {correct_sound_file}")
        self.correct_sound_player.setVolume(80)

        self.incorrect_sound_player = QMediaPlayer()
        incorrect_sound_file = "incorrect_answer.mp3"
        if QUrl.fromLocalFile(incorrect_sound_file).isValid():
            self.incorrect_sound_player.setMedia(QMediaContent(QUrl.fromLocalFile(incorrect_sound_file)))
        else:
            print(f"Uyarı: '{incorrect_sound_file}' ses dosyası bulunamadı.")
            logger.warning(f"Ses dosyası bulunamadı: {incorrect_sound_file}")
        self.incorrect_sound_player.setVolume(80)

        # Veritabanı bağlantısı
        self.conn = sqlite3.connect('milyoner_oyunu.db')
        self.cursor = self.conn.cursor()
        self.create_questions_table()
        self.insert_initial_questions() #sadece ilk çalıştırmada ya da boşsa ekler
        self.load_questions_from_db() 
        self.levele_gore_soru_secimi()

        self.init_ui()

    def create_questions_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    soru_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seviye INTEGER NOT NULL,
                    soru_metni TEXT NOT NULL,
                    secenek_a TEXT NOT NULL,
                    secenek_b TEXT NOT NULL,
                    secenek_c TEXT NOT NULL,
                    secenek_d TEXT NOT NULL,
                    dogru_cevap TEXT NOT NULL
                )
            """)
            self.conn.commit()
            logger.info("Sorular tablosu kontrol edildi/oluşturuldu.")
        except sqlite3.Error as e:
            logger.error(f"Sorular tablosu oluşturulurken hata oluştu: {e}")
            QMessageBox.critical(self, "Veritabanı Hatası", f"Sorular tablosu oluşturulamadı: {e}")

    def insert_initial_questions(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM questions")
            if self.cursor.fetchone()[0] == 0:
                questions_to_insert = [
                    # Seviye 1 
                    (1, "Halk arasında bilinen bir bilgiye göre, hangi hayvan süt verir?", "Horoz", "Kedi", "Tavuk", "Ördek", "B"),
                    (1, "Halk arasında bilinen bir bilgiye göre, kırmızı ışıkta ne yapılır?", "Durulur", "Geçilir", "Zıplanır", "Koşulur", "A"),
                    (1, "Halk arasında bilinen bir bilgiye göre, yazın insanlar genelde ne yer?", "Kestane", "Dondurma", "Lahana", "Balık", "B"),
                    (1, "Halk arasında bilinen bir bilgiye göre, düğünde ne takılır?", "Bardak", "Havlu", "Altın", "Kitap", "C"),
                    (1, "Halk arasında bilinen bir bilgiye göre, kahvaltıda ne yenir?", "Karpuz", "Pasta", "Makarna", "Peynir", "D"),
                    (1, "Halk arasında bilinen bir bilgiye göre, nazardan korunmak için ne takılır?", "Ayakkabı", "Gözlük", "Nazar boncuğu", "Kravat", "C"),
                    (1, "Hangi hayvan uçamaz?", "Serçe", "Kartal", "Tavuk", "Güvercin", "C"),
                    (1, "Güneş hangi yönden doğar?", "Kuzey", "Güney", "Doğu", "Batı", "C"),
                    (1, "Bir yıl kaç aydır?", "10", "11", "12", "13", "C"),
                    (1, "Hangisi bir meyvedir?", "Patates", "Elma", "Havuç", "Soğan", "B"),
                    (1, "Bir tavşan ne ile beslenir?", "Et", "Otu", "Balık", "Meyve", "B"),
                    (1, "En küçük tek haneli sayı hangisidir?", "0", "1", "2", "3", "B"),
                    (1, "Güneşin en parlak olduğu zaman dilimi hangisidir?", "Sabah", "Öğle", "Akşam", "Gece", "B"),
                    (1, "Suda yaşayan hayvan hangisidir?", "Kedi", "Köpek", "Kertenkele", "Balık", "D"),
                    (1, "Bir yılda kaç mevsim vardır?", "2", "3", "4", "5", "C"),
                    (1, "Hangi meyve turuncu renklidir?", "Elma", "Muz", "Portakal", "Üzüm", "C"),
                    (1, "Saatte kaç dakika vardır?", "30", "60", "90", "120", "B"),
                    (1, "Hangi hayvan havlayarak iletişim kurar?", "Kedi", "Köpek", "Kuş", "At", "B"),
                    (1, "Gözlük ne amaçla kullanılır?", "Görmek", "Yüzmek", "Uçmak", "Yemek", "A"),
                    (1, "Deniz nerede bulunur?", "Dağlarda", "Şehirde", "Ormanda", "Okyanusta", "D"),
                    #Seviye 2
                    (2, "Nobel Ödülleri hangi alanda verilmez?", "Fizik", "Kimya", "Matematik", "Edebiyat", "C"),
                    (2, "Hangi okyanus dünyanın en büyüğüdür?", "Atlantik Okyanusu", "Hint Okyanusu", "Arktik Okyanusu", "Pasifik Okyanusu", "D"),
                    (2, "En uzun kış mevsimi hangi yarımkürede yaşanır?", "Kuzey Yarımküre", "Güney Yarımküre", "Her ikisi", "Hiçbiri", "A"),
                    (2, "Türkiye'nin en büyük gölü hangisidir?", "Tuz Gölü", "Van Gölü", "Beyşehir Gölü", "Eğirdir Gölü", "B"),
                    (2, "Bir otomobil hangi yakıtla çalışmaz?", "Benzin", "Dizel", "Elektrik", "Su", "D"),
                    (2, "Dünya'nın uydusu hangisidir?", "Mars", "Venüs", "Ay", "Jüpiter", "C"),
                    (2, "Bir yıl kaç haftadan oluşur?", "52", "48", "50", "45", "A"),
                    (2, "Hangi renk gökyüzünün rengidir?", "Kırmızı", "Mavi", "Sarı", "Yeşil", "B"),
                    (2, "İlk insan hangi kıtada yaşamıştır?", "Avrupa", "Asya", "Afrika", "Amerika", "C"),
                    (2, "Hangisi sebze değildir?", "Domates", "Patates", "Elma", "Havuç", "C"),
                    (2, "Güneş sistemi kaç gezegenden oluşur?", "7", "8", "9", "10", "B"),
                    (2, "Türkiye hangi kıtalar arasında yer alır?", "Avrupa ve Asya", "Avrupa ve Afrika", "Asya ve Afrika", "Afrika ve Amerika", "A"),
                    (2, "DNA'nın açılımı nedir?", "Deoksiribonükleik Asit", "Dijital Nükleer Asit", "Dinamik Nöroaktif Asit", "Diyot Nöron Aktarıcı", "A"),
                    (2, "Kahveye batırılmış kedi dili bisküvileri ve mascarpone peyniri ile yapılan İtalyan tatlısının adı nedir?", "Kedi Pastası", "Trileçe", "Cheescake", "Tiramisu", "D"),
                    (2, "Dünyanın en büyük okyanusu hangisidir?", "Atlantik", "Hint", "Pasifik", "Arktik", "C"),
                    (2, "Fatih Sultan Mehmet’in babası kimdir?", "I.Mehmet", "II.Murad", "II.Mehmet", "Yıldırım Beyazıt", "B"),
                    (2, "En uzun nehir hangisidir?", "Nil", "Amazon", "Yangtze", "Mississippi", "A"),
                    (2, "İlk çağda yazıyı bulan medeniyet hangisidir?", "Sümerler", "Hititler", "Urartular", "Asurlar", "A"),
                    (2, "Nobel Ödülleri hangi alanda verilmez?", "Fizik", "Kimya", "Matematik", "Edebiyat", "C"),
                    (2, "Hangi okyanus dünyanın en büyüğüdür?", "Atlantik Okyanusu", "Hint Okyanusu", "Arktik Okyanusu", "Pasifik Okyanusu", "D"),
                    (2, "Hangi gezegenin halkaları vardır?", "Venüs", "Mars", "Satürn", "Merkür", "C"),
                    (2, "Hangi ülke Eiffel Kulesi ile ünlüdür?", "İtalya", "İspanya", "Fransa", "Almanya", "C"),
                    # Seviye 3
                    (3, "Kanın pıhtılaşmasında hangi vitamin rol oynar?", "C Vitamini", "D Vitamini", "K Vitamini", "B12 Vitamini", "C"),
                    (3, "İnternetin mucidi kimdir?", "Tim Berners-Lee", "Bill Gates", "Steve Jobs", "Alan Turing", "A"),
                    (3, "Divan-ı Lügatit Türk adlı eserin yazarı kimdir?", "Kaşgarlı Mahmut", "Yusuf Has Hacip", "Ali Şir Nevai", "Ahmet Yesevi", "A"),
                    (3, "Türkiye'nin en uzun nehri hangisidir?", "Kızılırmak", "Fırat", "Dicle", "Yeşilırmak", "A"),
                    (3, "Yunan mitolojisinde tanrıların kralı kimdir?", "Eros", "Zeus", "İlyada", "Herkül", "B"),
                    (3, "Porsche logosunda hangi hayvan görülebilir?", "Aslan", "Kaplan", "Boğa", "At", "D"),
                    (3, "Android uygulamaları geliştirmek için hangi programlama dili sıklıkla kullanılır?", "Java", "Python", "C++", "C#", "A"),
                    (3, "Işık hızı saniyede kaç kilometredir?", "300,000 km/s", "150,000 km/s", "1,000,000 km/s", "500,000 km/s", "A"),
                    (3, "Kanın pıhtılaşmasında hangi vitamin rol oynar?", "C Vitamini", "D Vitamini", "K Vitamini", "B12 Vitamini", "C"),
                    (3, "Leonardo da Vinci'nin ünlü eseri Mona Lisa nerede sergilenmektedir?", "British Museum", "Louvre Müzesi", "Metropolitan Sanat Müzesi", "Uffizi Galerisi", "B"),
                    (3, "Hangisi elektrik akımını iletmez?", "Bakır", "Alüminyum", "Plastik", "Demir", "C"),
                    (3, "Leonardo da Vinci'nin ünlü eseri Mona Lisa nerede sergilenmektedir?", "British Museum", "Louvre Müzesi", "Metropolitan Sanat Müzesi", "Uffizi Galerisi", "B"),
                    (3, "Bir insan vücudundaki en büyük organ hangisidir?", "Kalp", "Beyin", "Deri", "Karaciğer", "C"),
                    (3, "Türkler hangi yıl İslamiyet’i kabul etmiştir?", "751", "840", "1071", "930", "A"),
                    (3, "Dünyanın en büyük çölü hangisidir?", "Sahara", "Gobi", "Kalahari", "Antarktika", "D"),
                    (3, "Hangi element kimyasal sembolü ‘Fe’ ile gösterilir?", "Kurşun", "Demir", "Altın", "Gümüş", "B"),
                    (3, "Türkiye'nin ilk anayasası hangisidir?", "Kanun-i Esasi", "Medeni Kanun", "Teşkilat-ı Esasiye", "Tanzimat", "A"),
                    (3, "Bir insanın DNA’sı kaç kromozom içerir?", "23", "46", "92", "44", "B"),
                    (3, "Klasik müzik bestecisi Mozart hangi ülkedendir?", "Almanya", "Avusturya", "İtalya", "Fransa", "B"),
                    (3, "Hangi bilim insanı yer çekimi kanununu keşfetmiştir?", "Newton", "Einstein", "Galileo", "Tesla", "A"),
                    (3, "Bir ışık yılı neyi ifade eder?", "Işığın bir saniyede aldığı yol", "Işığın bir yılda aldığı yol", "Işığın hızını", "Işığın enerjisini", "B"),
                    (3, "Türkiye'nin en kalabalık şehri hangisidir?", "İzmir", "Ankara", "İstanbul", "Bursa", "C"),
                    # Seviye 4
                    (4, "Fotosentez hangi organelde gerçekleşir?", "Mitokondri", "Ribozom", "Kloroplast", "Endoplazmik Retikulum", "C"),
                    (4, "Hangi dağ dünyanın en yüksek dağıdır?", "K2", "Kangchenjunga", "Everest", "Lhotse", "C"),
                    (4, "Penisilini kim keşfetti?", "Humphry Davy", "Robert Boyle", "Marie Curie", "Alexander Fleming", "D"),
                    (4, "Hangisi Türkiye'de UNESCO Dünya Mirası Listesi'nde yer alan bir antik kenttir?", "Çatalhöyük", "Ani Harabeleri", "Göbekli Tepe", "Hepsi", "D"),
                    (4, "Fizikte 'Schrödinger'in kedisi' deneyi hangi alanla ilgilidir?", "Mekanik", "Termodinamik", "Kuantum Fiziği", "Optik", "C"),
                    (4, "Dünyanın en derin noktası neresidir?", "Mariana Çukuru", "Tonga Çukuru", "Java Çukuru", "Puerto Rico Çukuru", "A"),
                    (4, "Kuzey Işıkları olarak bilinen doğa olayı hangi gezegenin manyetik alanıyla ilgilidir?", "Mars", "Merkür", "Dünya", "Uranüs", "C"),
                    (4, "Türkçedeki 'mukavemet' kelimesi en çok ne anlamda kullanılır?", "Sabırsızlık", "Direnç", "Hız", "Uyum", "B"),
                    (4, "Fotosentez hangi organelde gerçekleşir?", "Mitokondri", "Ribozom", "Kloroplast", "Endoplazmik Retikulum", "C"),
                    (4, "Hangi dağ dünyanın en yüksek dağıdır?", "K2", "Kangchenjunga", "Everest", "Lhotse", "C"),
                    (4, "Albert Einstein hangi kuramıyla ünlüdür?", "Yerçekimi", "Elektromanyetizma", "Görelilik", "Termodinamik", "C"),
                    (4, "Hangi gezegen gaz devi olarak bilinir?", "Mars", "Venüs", "Jüpiter", "Merkür", "C"),
                    (4, "Roma İmparatorluğu’nun başkenti neresidir?", "Atina", "Roma", "Kartaca", "İstanbul", "B"),
                    (4, "Hangisi dünya dinlerinden biri değildir?", "Budizm", "Şamanizm", "Taoizm", "Astroloji", "D"),
                    (4, "İncil hangi dillerde yazılmıştır?", "Yunanca ve İbranice", "Latince ve Fransızca", "İngilizce ve Almanca", "Rusça ve Yunanca", "A"),
                    (4, "DNA replikasyonu hangi hücre organelinde gerçekleşir?", "Çekirdek", "Mitokondri", "Lizozom", "Ribozom", "A"),
                    (4, "Hangi savaş Osmanlı’nın Avrupa’daki son büyük yenilgisidir?", "II. Viyana Kuşatması", "Kırım Savaşı", "I. Balkan Savaşı", "II. Balkan Savaşı", "D"),
                    (4, "Türk kültüründe 'Nazarlık' ne amaçla kullanılır?", "Kötü ruhları uzaklaştırmak", "Hastalık tedavisi", "Zenginlik artırmak", "Sevgi göstermek", "A"),
                    (4, "Hangi matematikçi modern cebirin kurucusudur?", "Euclid", "René Descartes", "Carl Gauss", "Niels Abel", "B"),
                    # Seviye 5
                    (5, "Evrenin Büyük Patlama teorisini destekleyen ilk gözlemsel kanıt neydi?", "Kozmik Mikrodalga Arka Plan Radyasyonu", "Galaksilerin Kırmızıya Kayması", "Süpernova Patlamaları", "Kara Deliklerin Varlığı", "A"),
                    (5, "Atom bombasının geliştirilmesine öncülük eden proje hangisidir?", "Apollo Projesi", "Manhattan Projesi", "Star Wars Projesi", "Artemis Projesi", "B"),
                    (5, "Marvel sinematik evreninde 'Kaptan Amerika' karakterini canlandıran oyuncu kimdir?", "Chris Pratt", "Chris Hemsworth", "Chris Evans", "Robert Downey Jr.", "C"),
                    (5, "Genellikle 'Pop'un Kralı' olarak anılan ve 'Thriller', 'Billie Jean' gibi ikonik hitleriyle tanılan sanatçı kimdir?", "Justin Bieber", "Micheal Jackson", "George Micheal", "The Weekend", "B"),
                    (5, "Hangi popüler TV dizisinde Targaryen ve Stark hanedanı yer aldı?", "Game of Thrones", "House of the Dragon", "The Walking Dead", "Supernatural", "A"),
                    (5, "Thor hangi Tanrı'nın oğluydu?", "Odin", "Loki", "Zeus", "Hades", "A"),
                    (5, "Müzeyyen Senar hangi dönemde ün kazanmıştır?", "1920'ler", "1940'lar", "1960'lar", "1980'ler", "B"),
                    (5, "İlk Türk kadın romancı kimdir?", "Halide Edip Adıvar", "Fatma Aliye Topuz", "Nezihe Muhiddin", "Afife Jale", "B"),
                    (5, "Evrenin Büyük Patlama teorisini destekleyen ilk gözlemsel kanıt neydi?", "Kozmik Mikrodalga Arka Plan Radyasyonu", "Galaksilerin Kırmızıya Kayması", "Süpernova Patlamaları", "Kara Deliklerin Varlığı", "A"),
                    (5, "Atom bombasının geliştirilmesine öncülük eden proje hangisidir?", "Apollo Projesi", "Manhattan Projesi", "Star Wars Projesi", "Artemis Projesi", "B"),
                    (5, "Dünyanın en büyük çölü hangisidir?", "Sahara", "Gobi", "Antarktika", "Kalahari", "C"),
                    (5, "Hangisi bir Shakespeare oyunudur?", "Hamlet", "Don Kişot", "Sefiller", "Anna Karenina", "A"),
                    (5, "Kuantum dolanıklık kavramını ilk kim ortaya atmıştır?", "Albert Einstein", "Erwin Schrödinger", "Niels Bohr", "John Bell", "D"),
                    (5, "Türkiye'nin en uzun kesintisiz kara sınırı hangi ülkedir?", "İran", "Suriye", "Yunanistan", "Ermenistan", "A"),
                    (5, "Büyük Patlama’dan sonra ilk oluşan element hangisidir?", "Helyum", "Hidrojen", "Lityum", "Berilyum", "B"),
                    (5, "İnsan beynindeki sinir hücrelerine ne ad verilir?", "Nöron", "Lenfosit", "Glia", "Osteosit", "A"),
                    (5, "P vs NP problemi hangi alanın önemli bir sorunudur?", "Fizik", "Bilgisayar Bilimi", "Matematik", "Kimya", "B"),
                    (5, "Türkiye Cumhuriyeti’nin kurucu lideri kimdir?", "İsmet İnönü", "Mustafa Kemal Atatürk", "Celal Bayar", "Fevzi Çakmak", "B"),
                    (5, "DNA’da guanin hangi bazla eşleşir?", "Timin", "Adenin", "Sitozin", "Uracil", "C"),
                    (5, "Hangi filozof ‘Cogito, ergo sum’ (Düşünüyorum, öyleyse varım) demiştir?", "Platon", "Descartes", "Aristoteles", "Nietzsche", "B"),
                    (5, "Dünya Sağlık Örgütü (WHO) ne zaman kurulmuştur?", "1945", "1948", "1950", "1955", "B"),
                    (5, "Büyük İskender’in doğduğu şehir neresidir?", "Atina", "Pella", "Sparta", "Korint", "B"),
                    # Seviye 6
                    (6, "Görelilik teorisi kim tarafından geliştirilmiştir?", "Isaac Newton", "Albert Einstein", "Stephen Hawking", "Niels Bohr", "B"),
                    (6, "Dünyadaki en büyük mercan resifi sistemi hangisidir?", "Belize Bariyer Resifi", "Yeni Kaledonya Bariyer Resifi", "Büyük Set Resifi", "Florida Resif Sistemi", "C"),
                    (6, "On kıtadan oluşan İstiklal Marşı'nın tamamında, bu kelimelerden hangisi diğerlerinden daha az geçer?", "Vatan", "Kan", "Toprak", "Yurt", "C"),
                    (6, "Hangisi “Dede Korkut Hikayeleri”’ndeki karakterlerden biri değildir?", "Bala Hatun", "Banu Çiçek", "Bamsı Beyrek", "Bayındır Han", "A"),
                    (6, "Kur'an-ı Kerim'de hangisi üzerine yemin edilmemiştir?", "Deniz", "Güneş", "Arı", "Kalem", "C"),
                    (6, "Cumhurbaşkanlığı forsu ve armasındaki 16 Türk devleti arasında hangisi yoktur?", "Batı Hun İmparatorluğu", "Harzemşahlar", "Avar İmparatorluğu", "Anadolu Selçuklu Devleti", "D"),
                    (6, "Herodot'un deneyinde, konuşmayan çocuğun söylediği ilk kelime nedir?", "Ver", "Anne", "Ekmek", "Su", "C"),
                    (6, "Bu oyunlardan hangisi 'Başlangıç noktasından geçme, 200 $ alma' ifadesi içerir?", "Pac-Man", "Tabu", "Monopoly", "Milyoner", "C"),
                    (6, "Hangi hayvanın beyni vücut ağırlığına oranla en büyüktür?", "İnsan", "Fare", "Fil", "Karınca", "D"),
                    (6, "Giza'da kaç tane piramit yapılmıştır?", "2", "3", "4", "5", "B"),
                    (6, "Görelilik teorisi kim tarafından geliştirilmiştir?", "Isaac Newton", "Albert Einstein", "Stephen Hawking", "Niels Bohr", "B"),
                    (6, "Dünyadaki en büyük mercan resifi sistemi hangisidir?", "Belize Bariyer Resifi", "Yeni Kaledonya Bariyer Resifi", "Büyük Set Resifi", "Florida Resif Sistemi", "C"),
                    (6, "İstiklal Marşı kaç kıtadan oluşur?", "10", "8", "11", "9", "A"),
                    (6, "Dede Korkut hikayeleri hangi döneme aittir?", "İslamiyet öncesi Türk dönemi", "Osmanlı dönemi", "Selçuklu dönemi", "Cumhuriyet dönemi", "A"),
                    (6, "Kur'an-ı Kerim'de yemin edilmeyen varlık hangisidir?", "Arı", "Deniz", "Güneş", "Kalem", "A"),
                    (6, "Görelilik teorisini kim geliştirmiştir?", "Isaac Newton", "Albert Einstein", "Nikola Tesla", "Galileo Galilei", "B"),
                    (6, "Hangisi klasik Osmanlı mimarisinin önemli eserlerinden biri değildir?", "Süleymaniye Camii", "Topkapı Sarayı", "Selimiye Camii", "Anıtkabir", "D"),
                    (6, "Büyük İskender hangi imparatorluğu yenilgiye uğratmıştır?", "Pers İmparatorluğu", "Roma İmparatorluğu", "Mısır", "Babiller", "A"),
                    (6, "Türkçedeki 'Mukavemet' kelimesinin anlamı nedir?", "Direnç", "Sabır", "Güçsüzlük", "Uyum", "A"),
                    (6, "Kuantum fiziğinde Heisenberg’in belirsizlik ilkesi neyi ifade eder?", "Bir parçacığın konumu ve hızının aynı anda kesin olarak bilinememesi", "Bir parçacığın enerjisinin korunması", "Işığın dalga ve parçacık özelliği", "Atom çekirdeğinin kararlılığı", "A"),
                ]
                self.cursor.executemany("""
                    INSERT INTO questions (seviye, soru_metni, secenek_a, secenek_b, secenek_c, secenek_d, dogru_cevap)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, questions_to_insert)
                self.conn.commit()
                logger.info(f"{len(questions_to_insert)} başlangıç sorusu veritabanına eklendi.")
            else:
                logger.info("Sorular tablosu zaten dolu, başlangıç soruları eklenmedi.")
        except sqlite3.Error as e:
            logger.error(f"Başlangıç soruları eklenirken hata oluştu: {e}")
            QMessageBox.critical(self, "Veritabanı Hatası", f"Başlangıç soruları eklenemedi: {e}")

    def load_questions_from_db(self):
        self.seviye1_sorular = []
        self.seviye2_sorular = []
        self.seviye3_sorular = []
        self.seviye4_sorular = []
        self.seviye5_sorular = []
        self.seviye6_sorular = []
        self.questions = []

        try:
            self.cursor.execute("SELECT seviye, soru_metni, secenek_a, secenek_b, secenek_c, secenek_d, dogru_cevap FROM questions ORDER BY seviye, RANDOM()")
            rows = self.cursor.fetchall()
            for row in rows:
                seviye, soru_metni, secenek_a, secenek_b, secenek_c, secenek_d, dogru_cevap = row
                question_dict = {
                    "soru": soru_metni,
                    "secenekler": [secenek_a, secenek_b, secenek_c, secenek_d],
                    "dogru": dogru_cevap
                }
                if seviye == 1:
                    self.seviye1_sorular.append(question_dict)
                elif seviye == 2:
                    self.seviye2_sorular.append(question_dict)
                elif seviye == 3:
                    self.seviye3_sorular.append(question_dict)
                elif seviye == 4:
                    self.seviye4_sorular.append(question_dict)
                elif seviye == 5:
                    self.seviye5_sorular.append(question_dict)
                elif seviye == 6:
                    self.seviye6_sorular.append(question_dict)
            
            logger.info("Sorular veritabanından yüklendi ve seviyelere göre ayrıldı.")
        except sqlite3.Error as e:
            logger.error(f"Sorular veritabanından yüklenirken hata oluştu: {e}")
            QMessageBox.critical(self, "Veritabanı Hatası", f"Sorular yüklenirken bir hata oluştu: {e}")

    def init_ui(self):
        self.background_label = QLabel(self)
        pixmap = QPixmap("second_image.jpg")
        if not pixmap.isNull():
            self.background_label.setPixmap(pixmap)
            self.background_label.setScaledContents(True)
        else:
            print("Uyarı: 'second_image.jpg' arka plan resmi bulunamadı. Arka plan rengi kullanılacak.")
            logger.warning("Arka plan resmi 'second_image.jpg' bulunamadı.")     
            self.background_label.setStyleSheet("background-color: #1a2a40;") # Varsayılan arka plan rengi
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
        btn_audience.setObjectName("btn_audience") 
        pixmap_audience = QPixmap("person_joker.png")
        if pixmap_audience.isNull():
            print("Uyarı: 'person_joker.png' ikonu bulunamadı. Varsayılan gri kare kullanılacak.")
            logger.warning("Joker ikonu 'person_joker.png' bulunamadı.") 
            pixmap_audience = QPixmap(40, 40)
            pixmap_audience.fill(Qt.gray)
        else:
            pixmap_audience = pixmap_audience.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        btn_audience.setIcon(QIcon(pixmap_audience))
        btn_audience.setIconSize(pixmap_audience.size())
        btn_audience.setFixedSize(60, 60)
        btn_audience.setStyleSheet("background-color: #6c757d; hover:background-color: #b31942;border-radius: 30px; border: 2px solid #5a6268;")
        btn_audience.clicked.connect(self.audience_lifeline)
        self.joker_buttons.append(btn_audience)
        joker_layout.addWidget(btn_audience)

        # Yarı Yarıya jokeri
        btn_fifty_fifty = QPushButton()
        btn_fifty_fifty.setObjectName("btn_fifty_fifty")
        pixmap_fifty_fifty = QPixmap("50_joker.png")
        if pixmap_fifty_fifty.isNull():
            print("Uyarı: '50_joker.png' ikonu bulunamadı. Varsayılan gri kare kullanılacak.")
            logger.warning("Joker ikonu '50_joker.png' bulunamadı.")
            pixmap_fifty_fifty = QPixmap(40, 40)
            pixmap_fifty_fifty.fill(Qt.gray)
        else:
            pixmap_fifty_fifty = pixmap_fifty_fifty.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        btn_fifty_fifty.setIcon(QIcon(pixmap_fifty_fifty))
        btn_fifty_fifty.setIconSize(pixmap_fifty_fifty.size())
        btn_fifty_fifty.setFixedSize(60, 60)
        btn_fifty_fifty.setStyleSheet("background-color: #6c757d; hover:background-color: #b31942; border-radius: 30px; border: 2px solid #5a6268;")
        btn_fifty_fifty.clicked.connect(self.fifty_fifty_lifeline)
        self.joker_buttons.append(btn_fifty_fifty)
        joker_layout.addWidget(btn_fifty_fifty)

        #telefon jokeri 
        self.btn_phone = QPushButton()
        self.btn_phone.setObjectName("btn_phone") 
        pixmap_phone = QPixmap("phone_call_joker.png")
        if pixmap_phone.isNull():
            print("Uyarı: 'phone_call_joker.png' ikonu bulunamadı. Varsayılan gri kare kullanılacak.")
            logger.warning("Joker ikonu 'phone_call_joker.png' bulunamadı.")
            pixmap_phone = QPixmap(40, 40)
            pixmap_phone.fill(Qt.gray)
        else:
            pixmap_phone = pixmap_phone.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.btn_phone.setIcon(QIcon(pixmap_phone))
        self.btn_phone.setIconSize(pixmap_phone.size())
        self.btn_phone.setFixedSize(60, 60)
        self.btn_phone.setStyleSheet("background-color: #6c757d;hover:background-color: #b31942; border-radius: 30px; border: 2px solid #5a6268;")
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

        self.sound_button.setParent(self)
        self.sound_button.move(10, self.height() - self.sound_button.height() - 10)

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
            btn = QPushButton(f"Seç. {chr(65 + i)}")
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
       def get_random_questions(question_list, count):
            return random.sample(question_list, min(count, len(question_list)))

       seviye1_secim = get_random_questions(self.seviye1_sorular, 2)
       seviye2_secim = get_random_questions(self.seviye2_sorular, 2)
       seviye3_secim = get_random_questions(self.seviye3_sorular, 2)
       seviye4_secim = get_random_questions(self.seviye4_sorular, 2)
       seviye5_secim = get_random_questions(self.seviye5_sorular, 2)
       seviye6_secim = get_random_questions(self.seviye6_sorular, 2)

       self.questions = seviye1_secim + seviye2_secim + seviye3_secim + seviye4_secim + seviye5_secim + seviye6_secim
       logger.info(f"Oyun için toplam {len(self.questions)} soru rastgele seçildi.")
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
        self.time_left = self.time_per_question

        if self.current_question_index >= len(self.questions):
            self.game_over(win=True)
            return

        soru = self.questions[self.current_question_index]
        self.question_label.setText(soru["soru"])
        choices_text = ", ".join([f"{chr(65+i)}: {choice}" for i, choice in enumerate(soru['secenekler'])])
        logger.info(f"Soru {self.current_question_index + 1} gösterildi: '{soru['soru']}'. Seçenekler: [{choices_text}]. Doğru Cevap: {soru['dogru']}")

        for i, btn in enumerate(self.choice_buttons):
            btn.setText(f"{chr(65+i)}: {soru['secenekler'][i]}")
            btn.setEnabled(True)
            btn.setStyleSheet("background-color:#201f80; hover:background-color: #100f47; color: white; border: none; border-radius: 10px; padding: 15px 25px; font-size: 14pt; font-weight: bold; min-width: 150px;")

        # 7. sorudan itibaren süreyi kaldır
        if self.current_question_index >= 6:
            self.timer.stop()
            self.progress.hide()
            logger.info(f"Süre sınırı 7. sorudan itibaren kaldırıldı.")
        else:
            self.progress.show() 
            self.progress.setMaximum(self.time_per_question) 
            self.progress.setValue(self.time_left) 
            self.timer.start(1000)


    # süre akışı 1er saniye
    def update_timer(self):
        self.time_left -= 1
        self.progress.setValue(self.time_left)
        if self.time_left <= 0:
            self.timer.stop()
            QMessageBox.information(self, "Süre Doldu", "Süreniz bitti! Oyun sona erdi.")
            logger.warning(f"Süre soru {self.current_question_index + 1} için doldu. Oyun sona erdi.") 
            self.game_over(win=False)

    # cevap kontrolleri
    def answer_clicked(self):
        sender = self.sender()
        secilen_harf = sender.text()[0]
        dogru_harf = self.questions[self.current_question_index]["dogru"]
        secilen_cevap_metni = sender.text()[3:]
        dogru_cevap_metni = self.questions[self.current_question_index]["secenekler"][ord(dogru_harf)-ord('A')]

        self.timer.stop()

        if secilen_harf == dogru_harf:
            self.correct_sound_player.play() # Doğru cevap sesi çal
            QMessageBox.information(self, "Doğru!", "Tebrikler! Doğru cevap.")
            logger.info(f"Soru {self.current_question_index + 1} doğru cevaplandı. Seçilen Şık: {secilen_harf} ({secilen_cevap_metni}). Doğru Cevap: {dogru_harf} ({dogru_cevap_metni}).")  
            if self.current_question_index in self.baraj_sorulari:
                self.last_safe_index = self.current_question_index # Baraj sorusu geçildiyse güvenli indeksi güncelle
                logger.info(f"Baraj sorusu {self.current_question_index + 1} geçildi. Yeni güvenli ödül: {self.oduller[self.current_question_index]}.") 
            self.current_question_index += 1
            if self.current_question_index >= len(self.questions):
                self.game_over(win=True)
            else:
                self.start_question()
        else:
            self.incorrect_sound_player.play()
            QMessageBox.warning(self, "Yanlış!", f"Yanlış cevap! Doğru cevap {dogru_harf}: {dogru_cevap_metni}.")
            logger.warning(f"Soru {self.current_question_index + 1} yanlış cevaplandı. Seçilen Şık: {secilen_harf} ({secilen_cevap_metni}). Doğru Cevap: {dogru_harf} ({dogru_cevap_metni}). Oyun sona erdi.")
            self.game_over(win=False)

    # yarı yarıya joker hakkı
    def fifty_fifty_lifeline(self):
        if self.fifty_fifty_used:
            QMessageBox.warning(self, "Joker Hakkı", "Bu joker hakkını zaten kullandınız.")
            logger.warning("50/50 joker hakkı tekrar kullanılmaya çalışıldı.")
            return

        current_question = self.questions[self.current_question_index]
        correct_answer_index = ord(current_question["dogru"]) - ord('A')

        incorrect_indices = [i for i in range(4) if i != correct_answer_index and self.choice_buttons[i].isEnabled()]
        # En fazla 2 yanlış cevap silinmeli
        num_to_remove = min(2, len(incorrect_indices))
        removed_choices_text = []
        if num_to_remove > 0:
            random_incorrect_to_remove = random.sample(incorrect_indices, num_to_remove)

            # random gelen yanlış cevapları sil
            for i in random_incorrect_to_remove:
                removed_choices_text.append(self.choice_buttons[i].text())
                self.choice_buttons[i].setEnabled(False)
                self.choice_buttons[i].setText("")

        self.fifty_fifty_used = True
        self.joker_buttons[1].setEnabled(False)
        QMessageBox.information(self, "Yarı Yarıya", "İki yanlış cevap seçeneklerden kaldırıldı.")
        logger.info(f"50/50 joker hakkı soru {self.current_question_index + 1} için kullanıldı. Kaldırılan şıklar: {', '.join(removed_choices_text) if removed_choices_text else 'Hiç şık kaldırılmadı.'}")


    # Telefon jokeri
    def phone_lifeline(self):
        if self.phone_joker_used:
            QMessageBox.warning(self, "Joker Hakkı", "Bu joker hakkını zaten kullandınız.")
            logger.warning("Telefon jokeri hakkı tekrar kullanılmaya çalışıldı.") 
            return
        if not self.joker_persons:
            QMessageBox.warning(self, "Joker Hakkı", "Telefonla arayacak kimse bulunamadı. Lütfen ana ekranda joker kişileri giriniz.")
            logger.warning("Telefon jokeri kullanılmaya çalışıldı ancak joker kişi listesi boş.") 
            return

        person, ok = QInputDialog.getItem(self, "Telefon Jokeri", "Kimi aramak istersiniz?", self.joker_persons, 0, False)

        if ok and person:
            current_question = self.questions[self.current_question_index]
            correct_answer_index = ord(current_question["dogru"]) - ord('A')
            correct_answer_text = current_question["secenekler"][correct_answer_index]

            roll = random.randint(1, 10)
            response_text = ""
            given_answer = ""
            #telefon jokeri cevap olasılıkları
            if roll <= 1:  # 1 gelirse cevap vermeesin
                response_text = f"Merhaba, ben {person}. Üzgünüm, bu soru hakkında bilgim yok."
                given_answer = "Bilmiyorum"
            elif roll <= 3:  # 2 veya 3 gelirse random cevap versin
                available_choices = [i for i in range(len(current_question["secenekler"])) if self.choice_buttons[i].isEnabled()]
                if available_choices:
                    random_choice_index = random.choice(available_choices)
                    random_answer_text = current_question["secenekler"][random_choice_index]
                    response_text = f"Merhaba, ben {person}. Bence cevap '{random_answer_text}' olabilir."
                    given_answer = f"Rastgele: {chr(65+random_choice_index)} ({random_answer_text})"
                else:
                    response_text = f"Merhaba, ben {person}. Tek seçenek '{correct_answer_text}' gibi görünüyor."
                    given_answer = f"Tek seçenek: {current_question['dogru']} ({correct_answer_text})"
            else:  # 4,5,6,7,8,9,10 gelirse kesinlikle doğru cevabı versin
                response_text = f"Merhaba, ben {person}. Kesinlikle '{correct_answer_text}' olmalı!"
                given_answer = f"Kesin: {current_question['dogru']} ({correct_answer_text})"

            QMessageBox.information(self, f"{person} Cevabı", response_text)
            self.phone_joker_used = True
            self.btn_phone.setEnabled(False)
            logger.info(f"Telefon jokeri soru {self.current_question_index + 1} için kullanıldı. Arayan Kişi: {person}. Verilen Cevap: {given_answer}.")

    def audience_lifeline(self):
        if self.audience_joker_used:
            QMessageBox.warning(self, "Joker Hakkı", "Bu joker hakkını zaten kullandınız.")
            logger.warning("Seyirci jokeri hakkı tekrar kullanılmaya çalışıldı.")
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
                # Yanlış seçenekler için rastgele yüzdeler ata
                inc_options_range_min = max(1, int(avg_incorrect_vote - 7))
                inc_options_range_max = min(remaining_vote, int(avg_incorrect_vote + 7))
                inc_options_range_max = max(inc_options_range_min, inc_options_range_max) # Ensure min <= max
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
                elif diff_inc < 0 and incorrect_options_percentages[i] > 1:
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
            percentages[correct_answer_index] = max(0, percentages[correct_answer_index])

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
        percentages_str = ", ".join([f"{choices[i]}: {percentages[i]}%" for i in range(len(choices))])
        logger.info(f"Seyirciye sorma jokeri soru {self.current_question_index + 1} için kullanıldı. Yüzdeler: [{percentages_str}].")

    # oyun bitişi ve kazanılan ödülün bildirilişi
    def game_over(self, win: bool):
        self.timer.stop() 

        kazanc = "0 TL"
        if win:
            kazanc = self.oduller[-1]# Son ödülü kazanmış
            logger.info(f"Oyun kazanıldı! Kazanılan miktar: {kazanc}.") 
        else:
            if self.current_question_index > 0:
                kazanc = self.oduller[self.current_question_index - 1]
            if self.last_safe_index != -1 and self.current_question_index > self.last_safe_index:
                kazanc = self.oduller[self.last_safe_index]
            logger.info(f"Oyun kaybedildi. Kazanılan miktar: {kazanc}.")
        self.save_score(kazanc)
        self.reset_game_state()
        self.media_player.stop()
        if hasattr(self.stacked_widget.widget(2), 'display_score'):
            self.stacked_widget.widget(2).display_score(kazanc)
        self.stacked_widget.setCurrentIndex(2)

    # skoru kaydetme
    def save_score(self, kazanc):
        try:
            self.cursor.execute("INSERT INTO skorlar (ad, soyad, kazanc) VALUES (?, ?, ?)",
                                 (self.player_name, self.player_surname, kazanc))
            self.conn.commit()
            logger.info(f"Skor veritabanına kaydedildi: {self.player_name} {self.player_surname}, Kazanç: {kazanc}.")
        except sqlite3.Error as e:
            logger.error(f"Skor kaydedilirken hata oluştu: {e}")

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
            if btn.objectName() == "btn_phone":
                pixmap_phone = QPixmap("phone_call_joker.png")
                if not pixmap_phone.isNull():
                    pixmap_phone = pixmap_phone.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    btn.setIcon(QIcon(pixmap_phone))
            elif btn.objectName() == "btn_fifty_fifty":
                pixmap_fifty_fifty = QPixmap("50_joker.png")
                if not pixmap_fifty_fifty.isNull():
                    pixmap_fifty_fifty = pixmap_fifty_fifty.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    btn.setIcon(QIcon(pixmap_fifty_fifty))
            elif btn.objectName() == "btn_audience":
                pixmap_audience = QPixmap("person_joker.png")
                if not pixmap_audience.isNull():
                    pixmap_audience = pixmap_audience.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    btn.setIcon(QIcon(pixmap_audience))
            btn.setStyleSheet("background-color: #6c757d; hover:background-color: #b31942; border-radius: 30px; border: 2px solid #5a6268;")


        for btn in self.choice_buttons:
            btn.setText("")
            btn.setEnabled(True)
            btn.setStyleSheet("background-color:#201f80; hover:background-color: #100f47; color: white; border: none; border-radius: 10px; padding: 15px 25px; font-size: 14pt; font-weight: bold; min-width: 150px;")
        self.progress.show() # Zamanlayıcıyı tekrar göster
        self.mevcut_odulu_vurgula() 
        self.load_questions_from_db() 
        logger.info("Oyun durumu sıfırlandı.")

    # geri çekilme butonu
    def back_button_clicked(self):
        # Yarışmadan çekil butonu
        self.timer.stop() # Zamanlayıcıyı durdu
        kazanc = "0 TL"
        if self.current_question_index > 0:
            kazanc = self.oduller[self.current_question_index - 1]
        reply = QMessageBox.question(
            self,
            "Yarışmadan Çekil",
            f"Yarışmadan çekilmek istediğinize emin misiniz? Çekilirseniz, {kazanc} ile ayrılırsınız.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            logger.info(f"Oyuncu yarışmadan çekildi. Kazanılan miktar: {kazanc}.")
            self.save_score(kazanc)
            self.reset_game_state() # Oyun durumunu sıfırla
            # Üçüncü pencereye geçiş yap ve kazancı göster
            self.media_player.stop()
            if hasattr(self.stacked_widget.widget(2), 'display_score'):
                self.stacked_widget.widget(2).display_score(kazanc)
            self.stacked_widget.setCurrentIndex(2) # Üçüncü pencereye geç
        else:
            logger.info(f"Oyuncu yarışmadan çekilmekten vazgeçti.") 
            # Eğer kullanıcı çekilmek istemezse ve zamanlayıcı daha önce durdurulmamışsa tekrar başlat
            if self.current_question_index < 6: # Sadece ilk 6 soru için zamanlayıcıyı tekrar başlat
                self.timer.start(1000)

    def toggle_music(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            logger.info("Müzik duraklatıldı (SecondWindow).")
        else:
            self.media_player.play()
            logger.info("Müzik oynatılıyor (SecondWindow).")
        self.update_sound_button_icon()

    def update_sound_button_icon(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            pixmap = QPixmap("sound_on.png")
        else:
            pixmap = QPixmap("sound_off.png")

        if pixmap.isNull():
            print("Uyarı: Ses ikonu dosyası bulunamadı. Varsayılan gri kare kullanılacak.")
            logger.warning("Ses ikonu dosyası bulunamadı. Varsayılan kullanılacak.") 
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
            logger.warning(f"Müzik dosyası bulunamadı: {self.music_file}")
        self.media_player.setVolume(60)
        self.init_ui()

    def init_ui(self):
        #arka plan resmi için
        self.background_label = QLabel(self)
        pixmap = QPixmap("third_image.png")
        if not pixmap.isNull():
            self.background_label.setPixmap(pixmap)
            self.background_label.setScaledContents(True)
        else:
            print("Uyarı: 'third_image.png' arka plan resmi bulunamadı. Arka plan rengi kullanılacak.") 
            logger.warning("Arka plan resmi 'third_image.png' bulunamadı.")
            self.background_label.setStyleSheet("background-color: #2c3e50;") 
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.lower() 

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
        logger.info("Oyuncu 'Tekrar Oyna' butonuna tıkladı. İlk pencereye dönülüyor.")
        self.stacked_widget.setCurrentIndex(0)

    def exit_game(self):
        logger.info("Oyuncu 'Oyundan Çık' butonuna tıkladı. Uygulama kapatılıyor.")
        QApplication.instance().quit()

    def toggle_music(self):
        #sesi durakla/oynat
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            logger.info("Müzik duraklatıldı (ThirdWindow).")
        else:
            self.media_player.play()
            logger.info("Müzik oynatılıyor (ThirdWindow).")
        self.update_sound_button_icon()

    def update_sound_button_icon(self):
        # Ses butonu ikonu
        if self.media_player.state() == QMediaPlayer.PlayingState:
            pixmap = QPixmap("sound_on.png")
        else:
            pixmap = QPixmap("sound_off.png")

        if pixmap.isNull():
            print("Uyarı: Ses ikonu dosyası bulunamadı. Varsayılan gri kare kullanılacak.")
            logger.warning("Ses ikonu dosyası bulunamadı. Varsayılan kullanılacak.") 
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
        logger.info("Uygulama başlatılıyor.")
        self.first = FirstWindow(self)
        self.second = SecondWindow(self)
        self.third = ThirdWindow(self)

        self.addWidget(self.first)
        self.addWidget(self.second)
        self.addWidget(self.third)
        self.first.player_info_signal.connect(self.set_second_window_player_info)

        self.setWindowTitle("Kim Milyoner Olmak İster?")
        self.resize(1000, 750)
        self.first.media_player.play()# Uygulama başladığında ilk pencerenin müziğini çal

    def set_second_window_player_info(self, ad, soyad, joker_persons_list):
        """FirstWindow'dan gelen oyuncu bilgilerini SecondWindow'a aktarır."""
        self.second.player_name = ad
        self.second.player_surname = soyad
        self.second.joker_persons = joker_persons_list
        logger.info(f"SecondWindow oyuncu bilgileri güncellendi: {ad} {soyad}, Jokerler: {joker_persons_list}")

    def setCurrentIndex(self, index: int) -> None:
        current_window = self.currentWidget()
        target_window = self.widget(index)
        logger.info(f"Pencere değişimi: {type(current_window).__name__} -> {type(target_window).__name__}")

        if hasattr(current_window, 'media_player') and current_window.media_player.state() == QMediaPlayer.PlayingState:
            current_window.media_player.stop() 

        super().setCurrentIndex(index)

        if hasattr(target_window, 'media_player'):
            if target_window.media_player.state() != QMediaPlayer.PlayingState:
                if QUrl.fromLocalFile(target_window.music_file).isValid():
                    target_window.media_player.play()
                else:
                    print(f"Müzik dosyası bulunamadı {type(target_window).__name__}: {target_window.music_file}")
                    logger.warning(f"Müzik dosyası bulunamadı: {target_window.music_file}")

        self.first.update_sound_button_icon()
        self.second.update_sound_button_icon()
        self.third.update_sound_button_icon()


        if index == 1:
            self.second.load_questions_from_db() 
            self.second.levele_gore_soru_secimi()
            self.second.start_question()
        elif index == 0:
            self.first.load_scores()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.showMaximized()
    sys.exit(app.exec_())
    logger.info("Uygulama kapatılıyor.")