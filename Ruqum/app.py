"""
رُقم — Backend Server
يخفي مفتاح API نهى من علم عن المستخدم
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os

# ── تحميل المتغيرات من ملف .env
load_dotenv()

app = Flask(__name__, static_folder=".")
CORS(app)  # يسمح للـ HTML بالتواصل مع السيرفر

# ── إعداد عميل نهى من علم
client = OpenAI(
    api_key=os.getenv("NAHYA_API_KEY"),
    base_url=os.getenv("NAHYA_BASE_URL", "https://elmodels.ngrok.app/v1")
)

SYSTEM_PROMPT = """أنت رُقم، مساعد ذكي متخصص في النقوش الثمودية القديمة وتاريخ الخط العربي.
أجب دائماً باللغة العربية الفصحى بأسلوب واضح ومشوّق.
تخصصك: النقوش الثمودية، تاريخها، مواقعها في شبه الجزيرة العربية، طريقة قراءتها، وعلاقتها بالخط العربي الحديث.
إذا سأل المستخدم عن موضوع خارج نطاق تخصصك، أجب بلطف وأعِد التوجيه نحو موضوع النقوش."""


# ── تقديم ملف الـ HTML
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


# ── نقطة نهاية الـ Chat (الـ Frontend يتصل بها)
@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        messages = data.get("messages", [])

        if not messages:
            return jsonify({"error": "لا توجد رسائل"}), 400

        # ── إرسال للـ API
        response = client.chat.completions.create(
            model=os.getenv("NAHYA_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *messages
            ],
            max_tokens=1024,
            temperature=0.7,
        )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"[خطأ API] {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 رُقم يعمل على: http://localhost:5000")
    app.run(debug=True, port=5000)
