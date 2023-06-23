import sys
import requests
import random
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
from PyQt5.QtCore import QTimer, QTime, Qt
from PyQt5.QtGui import QFont, QColor, QPalette

header = {
    'authorization': 'YOUR_AUTHORIZATION_TOKEN'
}

command_counts = {
    'wh': 0,
    'wb': 0,
    'ws': 0,
    'w cf': 0,
    'w cf t': 0
}

command_weights = [60, 20, 5, 10, 5] # Determines which class will come in what percentage.

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.send_message)
        self.start_time = QTime.currentTime()
        self.last_message_time = None
        self.is_bot_running = False
        
    def init_ui(self):
        self.setWindowTitle("Bot")
        self.setFixedSize(400, 400)
        
        layout = QVBoxLayout()
        
        self.layout_buttons = QHBoxLayout()

        self.button_start = QPushButton("Start BOT")
        self.button_start.clicked.connect(self.start_bot)
        
        self.button_stop = QPushButton("Stop BOT")
        self.button_stop.clicked.connect(self.stop_bot)
        
        self.layout_buttons.addWidget(self.button_start)
        self.layout_buttons.addWidget(self.button_stop)
        
        layout.addLayout(self.layout_buttons)
        
        self.layout_inputs = QHBoxLayout()

        # In this section, it allows you to choose a random float time between the two numbers you choose.

        self.line_edit_start = QLineEdit()  # Add QLineEdit for start time
        self.line_edit_start.setPlaceholderText("Rastgele Başlangıç")  # Hint to the user
        self.layout_inputs.addWidget(self.line_edit_start)

        self.line_edit_end = QLineEdit()  # Add QLineEdit for end time
        self.line_edit_end.setPlaceholderText("Rastgele Son")  # Hint to the user
        self.layout_inputs.addWidget(self.line_edit_end)
        
        layout.addLayout(self.layout_inputs)
        
        self.label_counts = QLabel("Komut Sayıları:")
        self.label_counts.setAlignment(Qt.AlignCenter)
        self.label_counts.setStyleSheet("color: white; font-size: 12pt;")
        layout.addWidget(self.label_counts)
        
        self.layout_commands = QHBoxLayout()
        for command, count in command_counts.items():
            label_command = QLabel(f"{command}: {count}")
            label_command.setStyleSheet("color: white; font-size: 12pt;")
            self.layout_commands.addWidget(label_command)
        
        layout.addLayout(self.layout_commands)
        
        self.label_time = QLabel("Saniye")
        self.label_time.setAlignment(Qt.AlignCenter)
        self.label_time.setStyleSheet("color: white; font-size: 12pt;")
        layout.addWidget(self.label_time)
        
        layout.addStretch()  # Used to set the spacing
        
        self.button_close = QPushButton("Pencereyi Kapat")
        self.button_close.clicked.connect(self.start_close_countdown)
        layout.addWidget(self.button_close)
        
        self.setLayout(layout)
        
        # Set background color
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(31, 31, 31))
        self.setPalette(palette)
        
    def start_bot(self):
        if not self.is_bot_running:
            start = self.line_edit_start.text()  # Get start time
            end = self.line_edit_end.text()  # Get end time

            try:
                start = int(float(start))  # Convert start time to integer
                end = int(float(end))  # Convert end time to integer


                interval = random.randint(start, end)  # Choose a random integer
            except ValueError:
                interval = random.randint(15, 20)  # Use random time in case of invalid login

            self.start_time = QTime.currentTime()
            self.timer.start(interval * 1000)  # Start timer (in milliseconds)
            self.is_bot_running = True
            self.send_message()  # Send the first message after starting the bot
            self.button_start.setStyleSheet("background-color: green")  # Make the background color of the start button green
            self.button_stop.setStyleSheet("")  # Reset background color of stop button
    
    def stop_bot(self):
        if self.is_bot_running:
            self.timer.stop()  # Stop timer
            self.is_bot_running = False
            self.button_start.setStyleSheet("")  # Reset the background color of the start button
        self.button_stop.setStyleSheet("background-color: red")  # Make the background color of the stop button red
        
    def send_message(self):
        content_choices = ['wh', 'wb', f'ws {random.randint(20, 100)}', f'w cf {random.randint(20, 100)}', f'w cf t {random.randint(20, 100)}']
        content = random.choices(content_choices, weights=command_weights)[0]
        payload = {
            'content': content
        }
        r = requests.post('DISCORD_API_URL', data=payload, headers=header)
        if r.status_code == 200:
            if 'ws' in content or 'w cf' in content or 'w cf t' in content:
                command_counts['ws'] += content.count('ws')
                command_counts['w cf'] += content.count('w cf')
                command_counts['w cf t'] += content.count('w cf t')
            else:
                command_counts[content] += 1
            
            self.update_counts_labels()  # Update command counts
            self.update_elapsed_time()  # Update elapsed time
            
    def update_counts_labels(self):
        for i in reversed(range(self.layout_commands.count())):
            self.layout_commands.itemAt(i).widget().setParent(None)
        
        for command, count in command_counts.items():
            label_command = QLabel(f"{command}: {count}")
            label_command.setStyleSheet("color: white; font-size: 12pt;")
            self.layout_commands.addWidget(label_command)
    
    def update_elapsed_time(self):
        current_time = QTime.currentTime()
        elapsed_seconds = self.start_time.msecsTo(current_time) / 1000.0
        if self.last_message_time:
            time_since_last_message = current_time.msecsTo(self.last_message_time) / 1000.0
        else:
            time_since_last_message = 0.0
        
        self.label_time.setText(f"SANİYE: {time_since_last_message:.6f} ")
        self.last_message_time = current_time
    
    def start_close_countdown(self):
        self.button_close.setText("Pencereyi Kapat")
        self.button_close.setEnabled(False)
        self.close_timer = QTimer()
        self.close_timer.timeout.connect(self.update_countdown)
        self.remaining_time = 5
        self.update_countdown()
        self.close_timer.start(1000)  # Update every 1 second

    def update_countdown(self):
        if self.remaining_time > 0:
            self.button_close.setText(f"Imha ediliyor ({self.remaining_time} saniye)")
            self.remaining_time -= 1
        else:
            self.close_window()

def close_window(self):
    self.close()

        
        
app = QApplication([])
window = MyWindow()
window.show()
sys.exit(app.exec_())
