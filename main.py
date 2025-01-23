from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
import requests
import sounddevice as sd
import numpy as np
import threading
import wave
import io

KV = '''
ScreenManager:
    MainScreen:

<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20

        MDLabel:
            text: "Статус: Ожидание"
            id: status_label
            halign: 'center'

        MDRaisedButton:
            text: "Начать запись"
            on_press: root.start_recording()
            pos_hint: {'center_x': 0.5}
'''

class MainScreen(Screen):
    def start_recording(self):
        self.ids.status_label.text = "Статус: Запись..."
        threading.Thread(target=self.record_audio).start()

    def record_audio(self):
        duration = 7  # Длительность записи в секундах
        sample_rate = 44100  # Частота дискретизации
        channels = 1  # Количество каналов (моно)

        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='int16')
        sd.wait()  # Ожидание завершения записи

        # Преобразование записи в байты
        audio_data = recording.tobytes()

        # Сохранение аудиоданных в файл для проверки
        with wave.open('recorded_audio.wav', 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # 2 байта на сэмпл (16 бит)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data)

        # Отправка записи на сервер
        with open('recorded_audio.wav', 'rb') as audio_file:
            response = requests.post('http://192.168.0.101:5000/upload_audio', files={'audio': audio_file})
            if response.status_code == 200:
                self.ids.status_label.text = "Статус: Успешно"
            else:
                self.ids.status_label.text = "Статус: Ошибка"

        # Вывод записанного текста в консоль
        print("Записанный текст: ", response.json())

class MyApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

if __name__ == '__main__':
    MyApp().run()
