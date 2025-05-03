# client.py (combined with window.py)

import socket
import tkinter as tk
from threading import Thread
import queue
import pyaudio
import wave
import os
from record import SoundRecorder
import textwrap 

# サーバー設定
ip_address = '192.168.XX.XX'
port = XXXX
buffer_size = 1024

# ファイルの開始と終了のマーカー
FILE_START_MARKER = b"FILE_START"
FILE_END_MARKER = b"FILE_END"

# サーバーへの音声送信
def send_audio():
    if not record_queue.empty():
        filename = record_queue.get_nowait()
        with open(filename, 'rb') as f:
            file_data = f.read()

        try:
            file_size = os.path.getsize(filename)
            s.sendall(FILE_START_MARKER)
            s.sendall(file_size.to_bytes(4, byteorder='big'))
            s.sendall(file_data)
            s.sendall(FILE_END_MARKER)
            print(f"Sent file: {filename}")

        except Exception as e:
            print(f"Error during file sending: {e}")

# 非同期的にデータ送信
def send_wav_file():
    while True:
        send_audio()

# テキスト受信と画面の更新
def text_content():
    data = s.recv(buffer_size).decode()
    
    # 受信したデータを分割して画面更新
    transcribed_text, gemini_text1, gemini_text2, gemini_text3 = data.split('|')
    print("Received: {transcribed_text}, {gemini_text1}, {gemini_text2}, {gemini_text3}")
    
    update_message(transcribed_text)
    update_responses([gemini_text1, gemini_text2, gemini_text3])

# 非同期にデータ受信
def receive_text_file():
    while True:
        text_content()

# チャット領域更新
def update_message(message):
    for widget in chat_frame.winfo_children():
        widget.destroy()

    wrapped_message = textwrap.fill(message, width=60)
    label = tk.Label(chat_frame, text=wrapped_message, font=("Arial", 25), bg="blue", fg="white", anchor="c")
    label.pack(fill="x", pady=5)

# 応答文候補領域更新
def update_responses(responses):
    for widget in response_frame.winfo_children():
        widget.destroy()

    for response in responses:
        wrapped_response = textwrap.fill(response, width=60)
        label = tk.Label(response_frame, text=wrapped_response, font=("Arial", 20), bg="gray", fg="white", anchor="w")
        label.pack(fill="x", pady=5)

def main():
    global root, chat_frame, response_frame

    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg="black")

    # 下4分の1をチャット領域
    chat_frame = tk.Frame(root, bg="blue")
    chat_frame.place(relwidth=0.60, relheight=0.20, relx=0.20, rely=0.75, anchor="nw")

    # 右3分の1を応答文候補表示領域
    response_frame = tk.Frame(root, bg="black")
    response_frame.place(relwidth=0.33, relheight=0.20, relx=0.66, rely=0.55, anchor="nw")
    
    # 受信&画面描画スレッド
    Thread(target=receive_text_file, daemon=True).start()

    root.mainloop()

# サーバーに接続
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((ip_address, port))

    record_queue     : queue = queue.Queue()
    voice_angle_queue: queue = queue.Queue() #音声到来方向用キュー

    recoder = SoundRecorder(record_queue, voice_angle_queue)
    recoder.start_recording()

    # 録音スレッド&送信スレッド
    record_thread = Thread(target=recoder.run)
    send_wav_file_thread = Thread(target=send_wav_file)
    record_thread.start()
    send_wav_file_thread.start()

    main()
