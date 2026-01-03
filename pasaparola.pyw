import sys
import math
import json
import os
import pygame
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                             QPushButton, QVBoxLayout, QHBoxLayout, 
                             QMessageBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QDialog, 
                             QStackedWidget, QFileDialog, QLineEdit, QFormLayout, QComboBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor

# --- AYARLAR ---
GAME_TITLE = "⫸ PasaParola ⫷"
AUTHOR_TEXT = "by esofiso"
GITHUB_LINK = "https://github.com/esofiso"
CIRCLE_SIZE = 80  
FONT_SIZE_CIRCLE = 22
SCREEN_BG = "#152033" # Koyu Lacivert Arka Plan

# --- YARDIMCI SINIF: SAYISAL SIRALAMA İÇİN ---
class NumericItem(QTableWidgetItem):
    def __lt__(self, other):
        return (self.data(Qt.UserRole) < other.data(Qt.UserRole))

# --- ÖZEL OYUN SONU EKRANI (GRİ ARKA PLAN) ---
class GameOverDialog(QDialog):
    def __init__(self, score, correct, wrong, time_left, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Oyun Bitti")
        self.setFixedSize(400, 350)
        self.setStyleSheet("background-color: #7f8c8d; color: white; font-size: 16px; font-weight: bold;")
        
        layout = QVBoxLayout()
        
        title = QLabel("OYUN TAMAMLANDI!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; color: #f1c40f; margin-bottom: 20px;")
        layout.addWidget(title)

        # İstatistikler
        form_layout = QFormLayout()
        form_layout.addRow("Toplam Puan:", QLabel(f"{score}"))
        form_layout.addRow("Doğru Sayısı:", QLabel(f"{correct} (+{correct*25}p)"))
        form_layout.addRow("Yanlış Sayısı:", QLabel(f"{wrong} (-{wrong*10}p)"))
        form_layout.addRow("Kalan Süre:", QLabel(f"{time_left} sn (+{time_left}p)"))
        layout.addLayout(form_layout)
        
        layout.addSpacing(20)
        
        # İsim Girişi
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("İsminizi Giriniz")
        self.name_input.setStyleSheet("background-color: white; color: black; padding: 5px;")
        layout.addWidget(self.name_input)
        
        save_btn = QPushButton("KAYDET VE ÇIK")
        save_btn.setStyleSheet("background-color: #2ecc71; padding: 10px; border-radius: 5px;")
        save_btn.clicked.connect(self.accept)
        layout.addWidget(save_btn)
        
        self.setLayout(layout)

    def get_name(self):
        return self.name_input.text()

# --- SKOR TABLOSU ---
class ScoreBoardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Skor Tablosu")
        self.setFixedSize(900, 600)
        self.setStyleSheet("QDialog { background-color: #ecf0f1; } QTableWidget { background-color: white; color: black; }")
        
        layout = QVBoxLayout()
        self.table = QTableWidget()
        columns = ["İsim", "Puan", "Doğru", "Yanlış", "Kalan Süre", "Tür"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSortingEnabled(True)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_scores()

    def load_scores(self):
        if not os.path.exists('skorlar.json'): return
        try:
            with open('skorlar.json', 'r', encoding='utf-8') as f:
                scores = json.load(f)
                self.table.setRowCount(len(scores))
                for i, entry in enumerate(scores):
                    self.table.setItem(i, 0, QTableWidgetItem(entry['name']))
                    
                    score_item = NumericItem(str(entry['score']))
                    score_item.setData(Qt.UserRole, entry['score'])
                    self.table.setItem(i, 1, score_item)
                    
                    c_val = entry.get('correct', 0)
                    c_item = NumericItem(str(c_val))
                    c_item.setData(Qt.UserRole, c_val)
                    self.table.setItem(i, 2, c_item)
                    
                    w_val = entry.get('wrong', 0)
                    w_item = NumericItem(str(w_val))
                    w_item.setData(Qt.UserRole, w_val)
                    self.table.setItem(i, 3, w_item)
                    
                    t_val = entry.get('time_left', 0)
                    t_item = NumericItem(str(t_val))
                    t_item.setData(Qt.UserRole, t_val)
                    self.table.setItem(i, 4, t_item)
                    
                    self.table.setItem(i, 5, QTableWidgetItem(entry.get('type', '-')))
        except Exception as e: 
            print(f"Skor yükleme hatası: {e}")

class MainMenu(QWidget):
    def __init__(self, start_game_callback, start_custom_callback, show_scores_callback, exit_callback):
        super().__init__()
        self.setStyleSheet(f"background-color: {SCREEN_BG};")
        
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(15)

        title = QLabel(GAME_TITLE)
        title.setFont(QFont("TRT Bold", 48))
        title.setStyleSheet("color: #f1c40f; font-size: 100px; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        author = QLabel(f'<a href="{GITHUB_LINK}" style="color: #0BAC23; text-decoration: none;">{AUTHOR_TEXT}</a>')
        author.setAlignment(Qt.AlignCenter)
        author.setFont(QFont("TRT Bold", 16))
        author.setOpenExternalLinks(True)
        main_layout.addWidget(author)
        
        main_layout.addSpacing(40)

        # --- OYNA VE SET SEÇİM ALANI ---
        # Bu kısım bir konteyner içinde, altında açıklama metni olacak şekilde düzenlendi
        play_wrapper = QWidget()
        play_wrapper_layout = QVBoxLayout()
        play_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        play_wrapper_layout.setSpacing(5)

        # 1. Yatay Düzen (Combo + Buton)
        controls_container = QWidget()
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        self.set_combo = QComboBox()
        self.set_combo.setFont(QFont("TRT", 12))
        self.set_combo.setStyleSheet("""
            QComboBox {
                background-color: gray; color: black;
                border-radius: 10px; padding: 10px; min-width: 150px;
            }
            QComboBox::drop-down { border: 0px; }
        """)
        
        self.set_combo.addItem("⟫ Rastgele") 
        if os.path.exists('sorular.json'):
            try:
                with open('sorular.json', 'r', encoding='utf-8') as f:
                    sets = json.load(f)
                    for i in range(len(sets)):
                        self.set_combo.addItem(f"Set {i+1}")
            except: pass

        btn_play = QPushButton("OYNA")
        btn_play.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1; color: #2c3e50; 
                font-size: 24px; font-weight: bold; 
                padding: 15px; border-radius: 10px;
            }
            QPushButton:hover { background-color: #bdc3c7; }
        """)
        btn_play.setCursor(Qt.PointingHandCursor)
        btn_play.clicked.connect(lambda: start_game_callback(self.set_combo.currentIndex()))

        controls_layout.addWidget(self.set_combo, 1)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(btn_play, 2)
        
        controls_container.setLayout(controls_layout)
        
        # 2. Açıklama Metni (Altta)
        lbl_desc = QLabel("Hazır soru setlerinden sıradakini oynatır.")
        lbl_desc.setStyleSheet("color: #95a5a6; font-size: 14px; font-style: italic;")
        lbl_desc.setAlignment(Qt.AlignCenter)

        # Hepsini dikey düzene ekle
        play_wrapper_layout.addWidget(controls_container)
        play_wrapper_layout.addWidget(lbl_desc)
        
        play_wrapper.setLayout(play_wrapper_layout)
        play_wrapper.setFixedWidth(500)
        
        main_layout.addWidget(play_wrapper, alignment=Qt.AlignCenter)

        # Diğer Butonlar
        def create_menu_item(text, desc, callback, color="#8D9494", text_color="#0f0e1c"):
            container = QWidget()
            layout = QVBoxLayout()
            layout.setSpacing(5)
            layout.setContentsMargins(0, 10, 0, 10)
            
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color}; color: {text_color}; 
                    font-size: 24px; font-weight: bold; 
                    padding: 15px; border-radius: 12px; min-width: 300px;
                }}
                QPushButton:hover {{ background-color: #bdc3c7; }}
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(callback)
            layout.addWidget(btn, alignment=Qt.AlignCenter)
            
            lbl = QLabel(desc)
            lbl.setStyleSheet("color: #95a5a6; font-size: 14px; font-style: italic;")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl, alignment=Qt.AlignCenter)
            
            container.setLayout(layout)
            return container

        main_layout.addWidget(create_menu_item("ÖZEL OYUN", "Kendi hazırladığınız .txt dosyasını yükleyip oynayın.", start_custom_callback))
        main_layout.addWidget(create_menu_item("SKORLAR", "Geçmiş oyunların puan tablosunu görüntüleyin.", show_scores_callback))
        
        main_layout.addSpacing(20)

        btn_exit = QPushButton("ÇIKIŞ")
        btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #c0392b; color: white; 
                font-size: 18px; font-weight: bold; 
                padding: 10px; border-radius: 8px; min-width: 150px;
            }
            QPushButton:hover { background-color: #e74c3c; }
        """)
        btn_exit.setCursor(Qt.PointingHandCursor)
        btn_exit.clicked.connect(exit_callback)
        main_layout.addWidget(btn_exit, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

class GameScreen(QWidget):
    def __init__(self, return_menu_callback):
        super().__init__()
        self.return_menu_callback = return_menu_callback
        self.setStyleSheet(f"background-color: {SCREEN_BG};")
        
        self.questions = []
        self.circle_widgets = []
        self.current_index = 0
        self.time_left = 150
        
        self.correct_count = 0
        self.wrong_count = 0
        self.final_score = 0
        
        self.center_x = 960 
        self.center_y = 540
        self.initUI()
        
    def initUI(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        self.card_frame = QWidget(self)
        self.card_frame.setStyleSheet("background-color: rgba(0, 0, 0, 220); border-radius: 20px;")
        self.card_frame.hide()

        card_layout = QVBoxLayout()
        
        self.timer_label = QLabel("0", self.card_frame)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("color: #f1c40f; font-size: 36px; font-weight: bold; background: transparent;")
        card_layout.addWidget(self.timer_label)

        self.q_text = QLabel("...", self.card_frame)
        self.q_text.setWordWrap(True)
        self.q_text.setAlignment(Qt.AlignCenter)
        self.q_text.setStyleSheet("color: white; font-size: 26px; font-weight: bold; background: transparent; margin: 15px;")
        card_layout.addWidget(self.q_text)

        self.ans_text = QLabel("", self.card_frame)
        self.ans_text.setAlignment(Qt.AlignCenter)
        self.ans_text.setStyleSheet("color: #2ecc71; font-size: 30px; font-weight: bold; background: transparent;")
        self.ans_text.hide()
        card_layout.addWidget(self.ans_text)

        btn_layout = QHBoxLayout()
        btn_style = "padding: 12px; font-size: 18px; font-weight: bold; border-radius: 8px;"
        
        self.btn_reveal = QPushButton("CEVABI GÖR", self.card_frame)
        self.btn_reveal.setStyleSheet(f"background-color: #3498db; color: white; {btn_style}")
        self.btn_reveal.clicked.connect(self.reveal_answer)
        
        self.btn_pass = QPushButton("PAS", self.card_frame)
        self.btn_pass.setStyleSheet(f"background-color: #f1c40f; color: black; {btn_style}")
        self.btn_pass.clicked.connect(self.pass_question)

        self.btn_correct = QPushButton("DOĞRU", self.card_frame)
        self.btn_correct.setStyleSheet(f"background-color: #2ecc71; color: white; {btn_style}")
        self.btn_correct.clicked.connect(lambda: self.finalize_question(True))
        
        self.btn_wrong = QPushButton("YANLIŞ", self.card_frame)
        self.btn_wrong.setStyleSheet(f"background-color: #e74c3c; color: white; {btn_style}")
        self.btn_wrong.clicked.connect(lambda: self.finalize_question(False))

        btn_layout.addWidget(self.btn_reveal)
        btn_layout.addWidget(self.btn_correct)
        btn_layout.addWidget(self.btn_wrong)
        btn_layout.addWidget(self.btn_pass)
        card_layout.addLayout(btn_layout)
        self.card_frame.setLayout(card_layout)

        self.btn_exit = QPushButton("X", self)
        self.btn_exit.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; border-radius: 5px;")
        self.btn_exit.clicked.connect(self.quit_game)

    def resizeEvent(self, event):
        rect = self.rect()
        self.center_x = rect.width() // 2
        self.center_y = rect.height() // 2
        
        cw, ch = 700, 450
        self.card_frame.setGeometry(int(self.center_x - cw/2), int(self.center_y - ch/2), cw, ch)
        self.btn_exit.setGeometry(rect.width() - 60, 20, 40, 40)
        self.reposition_circles()
        super().resizeEvent(event)

    def reposition_circles(self):
        if not self.circle_widgets: return
        screen_min = min(self.width(), self.height())
        radius = screen_min * 0.40 
        total = len(self.circle_widgets)
        
        for i, lbl in enumerate(self.circle_widgets):
            angle = (2 * math.pi / total) * i - (math.pi / 2)
            x = self.center_x + radius * math.cos(angle) - (CIRCLE_SIZE / 2)
            y = self.center_y + radius * math.sin(angle) - (CIRCLE_SIZE / 2)
            lbl.move(int(x), int(y))

    def start_game(self, questions, game_type="Normal", duration=450):
        self.questions = questions
        self.current_game_type = game_type
        self.current_index = 0
        self.time_left = duration
        
        self.correct_count = 0
        self.wrong_count = 0
        self.final_score = 0
        
        rect = self.rect()
        self.center_x = rect.width() // 2
        self.center_y = rect.height() // 2
        if self.center_x < 50:
            screen = QApplication.primaryScreen().geometry()
            self.center_x = screen.width() // 2
            self.center_y = screen.height() // 2
        
        for widget in self.circle_widgets:
            widget.deleteLater()
        self.circle_widgets = []

        screen_min = min(self.width(), self.height())
        if screen_min < 100: screen_min = 800
        radius = screen_min * 0.40
        total = len(self.questions)
        
        for i, item in enumerate(self.questions):
            angle = (2 * math.pi / total) * i - (math.pi / 2)
            x = self.center_x + radius * math.cos(angle) - (CIRCLE_SIZE / 2)
            y = self.center_y + radius * math.sin(angle) - (CIRCLE_SIZE / 2)

            lbl = QLabel(item['letter'], self)
            lbl.setGeometry(int(x), int(y), CIRCLE_SIZE, CIRCLE_SIZE)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(QFont("TRT Bold", FONT_SIZE_CIRCLE, QFont.Bold))
            lbl.show()
            self.circle_widgets.append(lbl)
            item['status'] = 0 

        self.card_frame.show()
        self.update_ui_state()
        self.timer.start(1000)
        
        cw, ch = 700, 450
        self.card_frame.setGeometry(int(self.center_x - cw/2), int(self.center_y - ch/2), cw, ch)
        self.btn_exit.setGeometry(self.width() - 60, 20, 40, 40)

    def update_time(self):
        self.time_left -= 1
        self.timer_label.setText(f"Süre: {self.time_left}")
        if self.time_left <= 0:
            self.timer.stop()
            self.finish_game()

    def get_color_style(self, status, active=False):
        border = "5px solid #e67e22" if active else "2px solid white"
        bg, color = "#3498db", "white"
        if status == 1: bg = "#2ecc71"
        elif status == 2: bg = "#e74c3c"
        elif status == 3: bg, color = "#f1c40f", "black"
        return f"background-color: {bg}; color: {color}; border-radius: {CIRCLE_SIZE//2}px; border: {border};"

    def update_ui_state(self):
        q = self.questions[self.current_index]
        self.q_text.setText(f"({q['letter']}) - {q['question']}")
        self.ans_text.hide()
        self.btn_reveal.show()
        self.btn_pass.show()
        self.btn_correct.hide()
        self.btn_wrong.hide()

        for i, lbl in enumerate(self.circle_widgets):
            lbl.setStyleSheet(self.get_color_style(self.questions[i]['status'], i == self.current_index))

    def reveal_answer(self):
        self.ans_text.setText(self.questions[self.current_index]['answer'])
        self.ans_text.show()
        self.btn_reveal.hide()
        self.btn_pass.hide()
        self.btn_correct.show()
        self.btn_wrong.show()

    def pass_question(self):
        self.questions[self.current_index]['status'] = 3
        self.go_to_next()

    def finalize_question(self, is_correct):
        self.questions[self.current_index]['status'] = 1 if is_correct else 2
        
        if is_correct:
            self.correct_count += 1
        else:
            self.wrong_count += 1
            
        self.go_to_next()

    def go_to_next(self):
        start = self.current_index
        found = False
        for i in range(start + 1, len(self.questions)):
            if self.questions[i]['status'] in [0, 3]:
                self.current_index, found = i, True
                break
        if not found:
            for i in range(0, start + 1):
                if self.questions[i]['status'] in [0, 3]:
                    self.current_index, found = i, True
                    break
        
        if found: self.update_ui_state()
        else: self.finish_game()

    def finish_game(self):
        self.timer.stop()
        self.card_frame.hide()
        self.final_score = (self.correct_count * 25) - (self.wrong_count * 10) + (self.time_left * 1)
        
        dialog = GameOverDialog(self.final_score, self.correct_count, self.wrong_count, self.time_left, self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.get_name()
            if name:
                self.save_score(name)
                
        self.quit_game()

    def save_score(self, name):
        filename = 'skorlar.json'
        data = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f: data = json.load(f)
            except: pass
        
        new_entry = {
            'name': name, 
            'score': self.final_score, 
            'correct': self.correct_count,
            'wrong': self.wrong_count,
            'time_left': self.time_left,
            'type': self.current_game_type
        }
        
        data.append(new_entry)
        with open(filename, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

    def quit_game(self):
        self.timer.stop()
        self.return_menu_callback()

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PasaParola v8.3")
        self.showFullScreen() 
        self.setStyleSheet(f"QMainWindow {{ background-color: {SCREEN_BG}; }}")

        try:
            pygame.mixer.init()
            music_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music.mp3")
            
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.5) 
                pygame.mixer.music.play(-1) 
            else:
                print(f"Müzik dosyası bulunamadı: {music_path}")
        except Exception as e:
            print(f"Müzik hatası: {e}")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.menu_screen = MainMenu(self.start_normal_game, self.start_custom_game, self.show_scores, self.close)
        self.game_screen = GameScreen(self.go_to_menu)

        self.stack.addWidget(self.menu_screen)
        self.stack.addWidget(self.game_screen)

    def go_to_menu(self):
        self.stack.setCurrentIndex(0)

    def show_scores(self):
        dialog = ScoreBoardDialog(self)
        dialog.exec_()

    def start_normal_game(self, selected_index=0):
        if not os.path.exists('sorular.json'):
            QMessageBox.critical(self, "Hata", "sorular.json dosyası bulunamadı!")
            return

        try:
            with open('sorular.json', 'r', encoding='utf-8') as f:
                all_sets = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"JSON dosyası bozuk:\n{e}")
            return

        if selected_index == 0:
            score_count = 0
            if os.path.exists('skorlar.json'):
                try:
                    with open('skorlar.json', 'r') as f: score_count = len(json.load(f))
                except: pass
            set_index = score_count % len(all_sets)
        else:
            set_index = (selected_index - 1) % len(all_sets)
        
        selected_set = all_sets[set_index]
        
        import copy
        self.game_screen.start_game(copy.deepcopy(selected_set), f"Set {set_index + 1}", duration=450)
        self.stack.setCurrentIndex(1)

    def start_custom_game(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Soru Dosyası", "", "Text Files (*.txt);;All Files (*)", options=options)
        
        if file_path:
            try:
                questions, time_limit, set_name = self.parse_custom_file(file_path)
                if questions:
                    self.game_screen.start_game(questions, set_name, duration=time_limit)
                    self.stack.setCurrentIndex(1)
                else:
                    QMessageBox.warning(self, "Hata", "Dosya boş veya format hatalı!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya okunamadı:\n{str(e)}")

    def parse_custom_file(self, path):
        questions = []
        time_limit = 450
        set_name = "Özel Oyun"
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()] 
            
        if not lines:
            return [], 450, "Boş Dosya"

        current_line = 0
        if lines[0].isdigit():
            time_limit = int(lines[0])
            current_line += 1
            
        if current_line < len(lines) and lines[current_line].count('|') < 2:
            set_name = lines[current_line]
            current_line += 1
            
        for line in lines[current_line:]:
            parts = line.split('|')
            if len(parts) >= 3:
                questions.append({
                    'letter': parts[0].upper(),
                    'question': parts[1],
                    'answer': parts[2].upper(),
                    'status': 0
                })
                
        return questions, time_limit, set_name

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainApp()
    main.show()
    sys.exit(app.exec_())