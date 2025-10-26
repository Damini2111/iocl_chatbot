import os
import mysql.connector
from dotenv import load_dotenv
from rapidfuzz import fuzz, process
import re


# Load environment variables
load_dotenv()

# DB Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "NewPassword123",
    "database": "holiday_db",
    "port": 3306
}

# === Intent Keywords ===
INTENT_MAP = {
    "procedure": ["booking procedure", "how to book", "steps", "procedure", "instructions", "how do i book"],
    "homes": ["holiday home", "guest house", "stay", "location", "udaipur", "goa", "manali"],
    "holidays": ["holiday", "calendar", "festival", "date", "diwali", "christmas"],
    "faq": ["who", "how", "what", "when", "can", "cancel", "book", "print", "confirmation", "login"]
}





# === Intent Detection ===
def detect_intent(user_input):
    input_lower = user_input.lower()
    for intent, keywords in INTENT_MAP.items():
        for keyword in keywords:
            if keyword in input_lower:
                return intent
    return None


# === Normalize User Input ===
def preprocess(text):
    return re.sub(r"[^\w\s]", "", text.lower())

def ask_bot(user_input_raw):
    user_input = preprocess(user_input_raw)
    intent = detect_intent(user_input_raw.lower())

    if intent == "faq":
        if any(word in user_input_raw.lower() for word in ["all", "list", "faqs", "show"]):
            return list_all_faqs()
        return match_faq(user_input_raw)  # Use raw input for better matching

    elif intent == "holidays":
        return get_holidays(user_input_raw)

    elif intent == "homes":
        return get_holiday_homes(user_input_raw)

    elif intent == "procedure":
        return get_booking_procedure()

    else:
        return "❌ Sorry, I didn’t understand your question. Ask about bookings, holidays, holiday homes, or FAQs."







# === Match FAQ with Fuzzy Logic ===
def match_faq(user_input):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT question, answer FROM faqs")
        faqs = cursor.fetchall()

        if not faqs:
            return "No FAQs found."

        questions = [row[0] for row in faqs]
        match = process.extractOne(user_input, questions, scorer=fuzz.token_sort_ratio)

        if match and match[1] >= 60:  # Reduced threshold
            for q, a in faqs:
                if q == match[0]:
                    return f"❓ {q}\n👉 {a}"
        return "🤖 I couldn’t find an exact FAQ match. Try rephrasing."
    finally:
        cursor.close()
        conn.close()



# === Holiday Calendar ===
def get_holidays(user_input):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Specific holiday search
        keyword = preprocess(user_input)
        cursor.execute("SELECT holiday, date FROM holiday_calendar")
        holidays = cursor.fetchall()

        filtered = [
            f"🎉 {h} on {d}" for h, d in holidays if keyword in preprocess(h)
        ]

        if filtered:
            return "\n".join(filtered)
        elif holidays:
            return "\n".join(f"🎉 {h} on {d}" for h, d in holidays)
        else:
            return "No holiday data found."
    finally:
        cursor.close()
        conn.close()

# === Holiday Homes ===
def get_holiday_homes(user_input):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        keyword = preprocess(user_input)
        cursor.execute("SELECT holiday_home_name, location FROM holiday_homes")
        homes = cursor.fetchall()

        filtered = [
            f"🏡 {name} — {loc}" for name, loc in homes if keyword in preprocess(name) or keyword in preprocess(loc)
        ]

        if filtered:
            return "\n".join(filtered)
        elif homes:
            return "\n".join(f"🏡 {name} — {loc}" for name, loc in homes)
        else:
            return "No holiday homes found."
    finally:
        cursor.close()
        conn.close()
# === Booking Procedure ===
def get_booking_procedure():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT step_number\n, instructions FROM booking_procedure ORDER BY step_number")
        steps = cursor.fetchall()

        if not steps:
            return "No booking steps found."
        return "\n".join(f"📝 Step {num}: {instr}" for num, instr in steps)
    finally:
        cursor.close()
        conn.close()

def list_all_faqs():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT question, answer FROM faqs")
        faqs = cursor.fetchall()

        if not faqs:
            return "No FAQs found in the database."

        response = "📘 List of FAQs:\n\n"
        for i, (q, a) in enumerate(faqs, start=1):
            response += f"{i}. ❓ {q}\n   💬 {a}\n\n"
        return response.strip()
    finally:
        cursor.close()
        conn.close()



# === CLI Loop ===
if __name__ == "__main__":
    print("🧠 IOCL Chatbot | Ask about bookings, holidays, homes, or FAQs.")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("❓ Your Question: ")
        if user_input.lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break
        print(ask_bot(user_input))