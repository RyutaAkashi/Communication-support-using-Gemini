import pathlib
import textwrap
import os
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown
import time

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

genai.configure(api_key="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
model = genai.GenerativeModel('gemini-1.5-pro')

# 応答
prompt = """#依頼内容概要
会話文に対する自然な応答文の出力。

#依頼内容の具体
以下に現在の会話文を記述する。相手の話に対し、人間らしい自然な応答ができるように、事実に即した応答文を3つ出力せよ。

#フォーマット
<入力された会話文>
1.<1つ目の文>
2.<2つ目の文>
3.<3つ目の文>

#直前の会話文
"""
result="オリンピックの男子バレーボール、惜しかったね"
start = time.time()
response = model.generate_content(prompt+result)
#response = model.generate_content(pronpt, stream=True)

# output
print(to_markdown(response.text))
f = open("answer.txt", "w")
f.write(response.text)
f.close()

# time
end = time.time()
print("time:",end - start)
