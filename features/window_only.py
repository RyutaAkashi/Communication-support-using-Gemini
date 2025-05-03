import tkinter as tk
import random
import time
import threading
import textwrap 

# ランダムなチャットメッセージと応答候補のリスト
random_messages = [
    "Hello, how are you?", 
    "I'm fine, thank you!", 
    "What about you?", 
    "Let's catch up later!", 
    "Python is amazing! Tkinter makes GUIs easy and fun to work with, especially when building chat apps.",
    "Have a great day!", 
    "What are you up to lately? Let's have a chat."
]

response_candidates = [
    "Yes, that sounds good.",
    "No, I don't think so.",
    "Maybe, let me check.",
    "I'll get back to you.",
    "Could you clarify that?",
    "Let's talk about it later.",
    "Sure, let's do it."
]

# 話し手のリスト
speakers = ["self", "other"]

# メッセージの更新
def update_messages(canvas, chat_frame):
    while True:
        for widget in chat_frame.winfo_children():
            widget.destroy()
        
        # ランダムに会話文を選択して表示
        response = random.choice(random_messages)
        wrapped_response = textwrap.fill(response, width=60)

        label = tk.Label(chat_frame, text=wrapped_response, font=("Arial", 25), bg="blue", fg="white", anchor="c")
        label.pack(fill="x", pady=5)
    
        time.sleep(1)

# 応答文候補を更新
def update_response_candidates(response_frame):
    while True:
        for widget in response_frame.winfo_children():
            widget.destroy()
        
        # ランダムに応答候補を選択して表示
        for i in range(3):
            response = random.choice(response_candidates)
            label = tk.Label(response_frame, text=response, font=("Arial", 20), bg="gray", fg="white", anchor="w")
            label.pack(fill="x", pady=5)
            time.sleep(0.07)
        
        time.sleep(0.79)  # 1秒ごとに更新


def main():
    # Tkinterの設定
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg="black")

    # 下4分の1のチャット領域を作成
    chat_frame = tk.Frame(root, bg="blue")
    chat_frame.place(relwidth=0.60, relheight=0.20, relx=0.20, rely=0.75, anchor="nw")

    # キャンバスをチャット領域に配置
    canvas = tk.Canvas(chat_frame, bg="black", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    # 右3分の1の応答文候補表示領域を作成
    response_frame = tk.Frame(root, bg="black")
    response_frame.place(relwidth=0.33, relheight=0.20, relx=0.66, rely=0.55, anchor="nw")

    threading.Thread(target=update_messages, args=(canvas, chat_frame), daemon=True).start()
    threading.Thread(target=update_response_candidates, args=(response_frame,), daemon=True).start()
    root.mainloop()


if __name__ == "__main__":
    main()
