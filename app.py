import joblib
import random
import re
from flask import Flask, request, jsonify, render_template
from pythainlp import word_tokenize
from pythainlp.corpus.common import thai_stopwords
from pythainlp.corpus.common import thai_stopwords as get_stopwords

stopwords_list = list(get_stopwords())

def split_by_space(text):
    return text.split(' ')

def preprocess(text):
    text = re.sub('[^ก-๙a-zA-Z]', ' ', text)
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word.lower() not in stopwords_list]
    return ' '.join(tokens)

app = Flask(__name__)

vectorizer = joblib.load('vectorizer.pkl')
model = joblib.load('trained_thai_model.sav')

positive_responses = [
    "ยอดเยี่ยม! ข้อความของคุณเต็มไปด้วยพลังบวก ✨",
    "ชื่นชมในพลังบวกของคุณมากครับ 😊",
    "อ่านแล้วรู้สึกสดใสดีใจไปด้วยเลย!",
    "ความรู้สึกดีของคุณเป็นพลังงานบวกมาก​ ๆ​ ถ้าหากมีใครผ่านมาอ่านคงไม่แปลกที่จะเผลอยิ้มออกมาแน่​ ๆ​  เลย",
    "มันดีมากเลยนะที่ได้เห็นเธอเจอเรื่องดีๆ แบบนี้",
	"ขอให้มีโมเมนต์แบบนี้เข้ามาในชีวิตเธอเรื่อยๆ เลยนะ",
	"เธอผ่านอะไรมาตั้งเยอะ สมควรได้เจอเรื่องดีๆ แบบนี้สุดๆ แล้ว",
	"แค่ได้ยินก็ยิ้มตามเลยนะ มันเป็นข่าวดีที่น่ารักมาก",
	"เธอควรจะได้รู้สึกภูมิใจในตัวเองจริงๆ ไม่ใช่แค่วันนี้ แต่ทุกวัน",
	"เห็นแล้วก็อดคิดไม่ได้ว่า ความพยายามมันไม่เคยเสียเปล่าเลย",
	"บางทีสิ่งดีๆ ก็ไม่ได้มาดังๆ แต่มันเงียบๆ แล้วอบอุ่นแบบนี้แหละ",
	"ขอให้วันนี้เป็นจุดเริ่มต้นของอะไรดีๆ อีกหลายอย่าง",
	"บางความสุขมันเรียบง่าย แต่มันทำให้เรารู้ว่าโลกนี้ยังใจดีกับเราอยู่",
	"เธอเป็นแสงให้ตัวเองได้ดีมากเลยนะวันนี้",
    "ดีใจกับเธอด้วยนะ เห็นแล้วรู้สึกอุ่นใจแทนเลย",
	"เธอสมควรได้รับสิ่งดีๆ แบบนี้จริงๆ",
	"เห็นเธอมีความสุข มันก็ดีไปถึงเราเลยนะ",
	"เก่งมากเลยนะ ไม่ใช่แค่เพราะผลลัพธ์ แต่เพราะระหว่างทางเธอก็พยายามมาตลอด",
	"มันไม่ใช่เรื่องเล็กๆ เลยนะ ภูมิใจด้วยจริงๆ",
	"ขอบคุณที่แบ่งความดีใจนี้ให้รู้สึกไปด้วยกัน",
	"จำไว้เลยนะ ว่าความสุขแบบนี้ เธอคู่ควรกับมันมาก",
	"ช่วงเวลานี้ดีมากเลย ขอให้มันอยู่กับเธอนานๆ"
]

negative_responses = [
    "ไม่เป็นไรนะครับ วันพรุ่งนี้ยังเริ่มใหม่ได้เสมอ 💙",
    "เข้าใจความรู้สึกเลย ขอเป็นกำลังใจให้นะครับ",
    "คุณไม่ได้อยู่คนเดียว เราอยู่ตรงนี้เสมอ 🫂",
    "ไม่เป็นไรเลยนะ เราทุกคนมีวันที่รู้สึกไม่โอเคได้ทั้งนั้น แค่คุณยังอยู่ตรงนี้ ยังหายใจ ยังพยายาม นั่นก็เก่งมากๆ แล้วนะ เราอยู่ตรงนี้เสมอสำหรับคุณนะ",
    "วันนี้อาจจะแย่ แต่พรุ่งนี้อาจจะดีกว่าที่คิดก็ได้นะ",
"ถ้าไม่ไหวจริงๆ ก็พักก่อนนะ ไม่มีใครว่าเธอหรอก",
"ไม่ต้องเก่งเสมอ ไม่ต้องยิ้มเสมอ แค่เป็นเธอในแบบที่เธอเป็นก็พอแล้ว",
"ไม่เป็นไรเลยที่จะพัก จะอ่อนแอ เราคือมนุษย์ไง",
"ความเจ็บปวดไม่ได้แปลว่าเธออ่อนแอ มันแปลว่าเธอมีหัวใจ",
"ถ้าไม่มีใครเข้าใจ เราเข้าใจนะ ว่ามันไม่ง่ายเลย",
"ไม่เป็นไรเลยที่ตอนนี้จะยังไม่โอเค เดี๋ยวมันก็ค่อยๆ ดีขึ้น",
"ไม่มีใครสมบูรณ์แบบหรอก มันเป็นส่วนหนึ่งของการเติบโต"
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    user_input = request.form['text']
    if not user_input.strip():
        return jsonify({'sentiment' : 'none', 'response' : 'โปรดใส่ข้อความก่อนวิเคราะห์'})
    
    processed = preprocess(user_input)
    text_vector = vectorizer.transform([processed])
    prediction = model.predict(text_vector)[0]

    if prediction == "บวก":
        sentiment = 'positive'
        response = random.choice(positive_responses)
    else:
        sentiment = 'negative'
        response = random.choice(negative_responses)

    return jsonify({'sentiment' : sentiment, 'response' : response})

if __name__ == '__main__':
    app.run(debug=True)