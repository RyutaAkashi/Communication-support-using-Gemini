Implemented in 2024.06-2024.12
# Communication support using Gemini
Implementation and evaluation of a mobile system that uses sentence generation AI and AR glasses to provide topics of conversation.

# Geminiを用いたコミュニケーション支援システム
## 目的
対面でのコミュニケーション機会が減少し、会話の難易度が高まっている現代において、円滑な人と人とのコミュニケーションを支援するシステムを構築する。

## 手法
マイクで録音した会話音声を、サーバーサイドのWhisperを用いて文字起こしする。この文字起こし結果に基づき、Geminiが会話内容に適した応答文を生成する。文字起こしされた会話文とGeminiが生成した応答文はクライアント（Raspberry Pi）に送信され、ARグラス上に表示される。
![image](https://github.com/RyutaAkashi/Communication-support-using-Gemini/blob/main/result/method.png)

## 実装詳細
### `main.py` (Raspberry Pi上で動作)
主に以下の4つのスレッドを非同期に並行処理する。
* **録音スレッド**: 音声を録音する。
* **ファイル作成スレッド**: 区切られた区間の録音データを音声ファイルとしてまとめる。
* **送信スレッド**: 文字起こしサーバーに音声ファイルを送信する。
* **受信・画面描画スレッド**: サーバーからテキストデータ（会話文、応答文）を受信し、ARグラスに表示するための画面を作成する。
![image](https://github.com/RyutaAkashi/Communication-support-using-Gemini/blob/main/result/thread.png)

### `record.py` (`main.py`から引用して使用)
録音用モジュール。リングバッファを利用し、無音区間を検知した場合に音声ファイルを作成する。以下から引用。
https://github.com/bbtit/Xreal-IoT

### `server.py` (文字起こしサーバー上で動作)
クライアントから受信した音声ファイルをWhisperを用いて文字起こしする。文字起こしされた会話文と、Geminiへの出力指示を含むプロンプトをGemini APIに送信し、応答文の候補を3例取得する。会話文と生成された応答文候補を元のクライアントに送信する。

## 結果
会話内容に応じた適切な応答文候補をARグラス上に表示することで、会話の補助を実現できた。
![image](https://github.com/RyutaAkashi/Communication-support-using-Gemini/blob/main/result/sight.png)

## 実行デモンストレーション
本プログラムの実際の動作については、以下の動画で確認できる。
* [文章生成AIとARグラスを用いた話題提供を行う携帯システム デモ動画](https://youtu.be/M1KEdIeTJfc)
![image](https://github.com/RyutaAkashi/Communication-support-using-Gemini/blob/main/result/result.png)
