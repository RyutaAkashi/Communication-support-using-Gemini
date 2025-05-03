import tkinter as tk
import random
import time
import threading

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

# 吹き出しを作成する関数
def create_bubble(canvas, message, y_offset, canvas_width, speaker):
    bubble_padding = 10
    font_size = 14
    font = ("Arial", font_size)
    max_text_width = int(canvas_width * 0.7)  # 吹き出しの最大幅:キャンバスの70%

    # 吹き出しの位置と色
    if speaker == "self":
        text_anchor = "nw"
        bubble_color = "white"
        text_color = "black"
        x_offset = 10  # 左詰め
    else:
        text_anchor = "ne"
        bubble_color = "blue"
        text_color = "white"
        x_offset = canvas_width - 10  # 右詰め

    # 吹き出し内のテキスト追加
    text_id = canvas.create_text(x_offset, y_offset, anchor=text_anchor, text=message, font=font, fill=text_color, width=max_text_width)

    # テキストサイズに応じて吹き出し追加
    bbox = canvas.bbox(text_id)
    bubble_id = canvas.create_rectangle(
        bbox[0] - bubble_padding, bbox[1] - bubble_padding, 
        bbox[2] + bubble_padding, bbox[3] + bubble_padding, 
        fill=bubble_color, outline=""
    )

    # 吹き出しの後ろにテキストを配置
    canvas.tag_lower(bubble_id, text_id)

    return bbox[3] - bbox[1] + 2 * bubble_padding  # 吹き出しの高さ

# メッセージを追加し、古いメッセージを上にシフト
def add_message(canvas, chat_frame):
    canvas_width = chat_frame.winfo_width()

    message = random.choice(random_messages)
    speaker = random.choice(speakers)

    # キャンバスの内容を上にシフト
    canvas.yview_moveto(1)  # 常に一番下までスクロール
    y_offset = canvas.bbox("all")[3] + 20 if canvas.bbox("all") else 10  # 最新のメッセージの下に表示

    # 吹き出しをキャンバスに追加
    bubble_height = create_bubble(canvas, message, y_offset, canvas_width, speaker)

    # キャンバスのスクロール領域を更新
    canvas.config(scrollregion=canvas.bbox("all"))

# メッセージの更新を一定間隔で行うスレッド関数
def update_messages(canvas, chat_frame):
    while True:
        add_message(canvas, chat_frame)
        time.sleep(1)

# 応答文候補を更新する関数
def update_response_candidates(response_frame):
    while True:
        for widget in response_frame.winfo_children():
            widget.destroy()
        
        # ランダムに応答候補を選択して表示
        for i in range(3):
            response = random.choice(response_candidates)
            label = tk.Label(response_frame, text=response, font=("Arial", 25), bg="gray", fg="white", anchor="w")
            label.pack(fill="x", pady=5)
        
        time.sleep(1)  # 1秒ごとに更新

# マウスホイールでスクロールを実行
def on_mouse_wheel(event, canvas):
    if event.delta:
        # Windows/Linux
        canvas.yview_scroll(-1 * (event.delta // 120), "units")
    else:
        # macOS
        canvas.yview_scroll(-1 * event.delta, "units")


def main():
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg="black")

    # 左上3分の1、上4分の3のチャット領域を作成
    chat_frame = tk.Frame(root, bg="black")
    chat_frame.place(relwidth=0.33, relheight=0.75, anchor="nw")

    # キャンバスをチャット領域
    canvas = tk.Canvas(chat_frame, bg="black", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    # マウスホイールのイベントをバインド
    root.bind_all("<MouseWheel>", lambda event: on_mouse_wheel(event, canvas))
    root.bind_all("<Button-4>", lambda event: on_mouse_wheel(event, canvas))  # Linuxのスクロール対応
    root.bind_all("<Button-5>", lambda event: on_mouse_wheel(event, canvas))  # Linuxのスクロール対応

    # 下4分の1の応答文候補表示領域
    response_frame = tk.Frame(root, bg="black")
    response_frame.place(relwidth=0.60, relheight=0.20, relx=0.20, rely=0.80, anchor="nw")

    threading.Thread(target=update_messages, args=(canvas, chat_frame), daemon=True).start()
    threading.Thread(target=update_response_candidates, args=(response_frame,), daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    main()
