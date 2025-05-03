import socket
import whisper
from threading import Thread
from threading import Lock
import threading
import queue

import pathlib
import textwrap
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown
import time
import random

# IPアドレスとポート番号の設定
ip_address = '0.0.0.0'
port = XXXX
buffer_size = 1024

# クライアント情報の管理
clients = {}
file_numbers = {}
queues = {}

# ファイルの開始と終了のマーカー
FILE_START_MARKER = b"FILE_START"
FILE_END_MARKER = b"FILE_END"

# whisperの準備
WHISPER_MODEL_NAME = 'large' # tiny, base, small, medium, large
WHISPER_DEVICE = 'cuda' # cpu, cuda
print('loading whisper model', WHISPER_MODEL_NAME, WHISPER_DEVICE)
whisper_model = whisper.load_model(WHISPER_MODEL_NAME, device=WHISPER_DEVICE)

lock = threading.Lock()

response_candidates = [
    "Yes, that sounds good.",
    "No, I don't think so.",
    "Maybe, let me check.",
    "I'll get back to you.",
    "Could you clarify that?",
    "Let's talk about it later.",
    "Sure, let's do it."
]

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# 音声の文字起こし関数
def audio_text(input_file, output_file):
    # WHISPER_MODEL_NAME = 'large' # tiny, base, small, medium, large
    # WHISPER_DEVICE = 'cuda' # cpu, cuda
    # print('loading whisper model', WHISPER_MODEL_NAME, WHISPER_DEVICE)
    # whisper_model = whisper.load_model(WHISPER_MODEL_NAME, device=WHISPER_DEVICE)
    lock.acquire()
    result = whisper_model.transcribe(input_file, verbose=True, language='ja')
    lock.release()
    with open(output_file, "w", encoding="utf_8") as f:
        f.write(result["text"])
    return result["text"]

# gemini応答文作成関数
def create_gemini(transcribed_text):
    genai.configure(api_key="XXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 応答
    prompt = """#依頼内容概要
    会話文に対する自然な応答文の出力。

    #依頼内容の具体
    以下に現在の会話文を記述する。相手の話に対し、人間らしい自然な応答ができるように、事実に即した応答文を3つ出力せよ。
    出力はテキスト形式で行い、以下のように3つの応答文を|で区切り、一文にして出力せよ。
    
    #出力フォーマット
    <1つ目の文>|<2つ目の文>|<3つ目の文>

    #直前の会話文
    """
    start = time.time()
    response = model.generate_content(prompt+transcribed_text)
    print(response.text)

    # output
    with open(filename, 'wb') as f:
        f.write(response.text)
        f.write("\n")

    # time
    print(f"Gemini text creating time: ",time.time() - start)
    return response.text

# ファイルデータの受信関数
def file_receive(client_id, conn):
    # print(f"file_receive start {client_id}")
    global file_numbers
    while True:
        file_number = file_numbers.get(client_id, 0)
        filename = f"receive_{client_id}_{file_number}.wav"

        try:
            # ファイルの開始マーカーを受信
            start_marker = conn.recv(len(FILE_START_MARKER))
            if start_marker != FILE_START_MARKER:
                print(f"Invalid start marker received for client {client_id}")
                break
            else:
                print(f"start marker received for client {client_id}")
            
            # ファイルサイズ情報を受信
            file_size_data = conn.recv(4)
            file_size = int.from_bytes(file_size_data, byteorder='big')

            # ファイルデータの受信
            received_size = 0
            with open(filename, 'wb') as f:
                while True:
                    data = conn.recv(buffer_size)
                    if not data or FILE_END_MARKER in data:
                        print(f"end marker received for client {client_id}")
                        break
                    f.write(data)
                    received_size += len(data)
                    if received_size >= file_size:
                        # 指定サイズに達した場合も終了
                        break

            print(f"File received for client {client_id}: {filename}")
            queues[client_id].put(filename)
            file_numbers[client_id] = file_number + 1

        except Exception as e:
            print(f"Error during file receiving for client {client_id}: {e}")
            break


# テキストデータ送信関数
def text_send(client_id):
    while True:
        if not queues[client_id].empty():
            filename = queues[client_id].get_nowait()
            print(f"Transcribing audio from {filename} for client {client_id}")
            #lock.acquire()
            transcribed_text = audio_text(filename, f'received_text_{client_id}.txt')
            #lock.release()
            print(f"Transcribed text for client {client_id}: {transcribed_text}")

            gemini_text = create_gemini(transcribed_text)
            # for demo
            #gemini_text = random.choice(response_candidates)+ "|" + random.choice(response_candidates) + "|" + random.choice(response_candidates)

            # まとめて送信
            response = transcribed_text + "|" + str(gemini_text)
            conn, _ = clients[client_id]
            try:
                conn.sendall(response.encode())
                print(f"Transcribed and gemini text sent to client {client_id}")
            except Exception as e:
                print(f"Failed to send text to client {client_id}: {e}")
                break


# クライアント処理スレッド
def handle_client(client_id, conn, addr):
    clients[client_id] = (conn, addr)
    file_numbers[client_id] = 0
    queues[client_id] = queue.Queue()
    print(f"handle_client Start {file_numbers}")
    receive_wav_file_thread = Thread(target=file_receive, args=(client_id, conn))
    send_text_file_thread = Thread(target=text_send, args=(client_id,))
    print(f"file_receive_thread {client_id}")
    receive_wav_file_thread.start()
    send_text_file_thread.start()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((ip_address, port))
    s.listen(5)
    client_id = 1
    print("wait client")

    while True:
        conn, addr = s.accept()
        print(f"Accepted connection from {addr}")
        Thread(target=handle_client, args=(client_id, conn, addr)).start()
        client_id += 1
