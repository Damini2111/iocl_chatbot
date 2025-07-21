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
    "faq": ["who", "how", "what", "when", "can", "cancel", "book", "print", "confirmation", "login"],
    "holidays": ["holiday", "calendar", "festival", "date", "deepawali", "diwali", "christmas"],
    "homes": ["holiday home", "home", "guest house", "udaipur", "manali", "goa", "location", "place", "stay"],
    "procedure": ["steps", "procedure", "how to", "booking process", "instructions"]
}
def get_faq_answer(user_input, cursor):
    cursor.execute("SELECT question, answer FROM faqs")
    faqs = cursor.fetchall()

    input_cleaned = clean(user_input)
    matches = []

    for question, answer in faqs:
        score = fuzz.token_sort_ratio(input_cleaned, clean(question))
        if score >= 70:
            matches.append(f"❓ {question}\n👉 {answer}")

    if matches:
        return "\n\n".join(matches)
    else:
        return "🤖 I couldn’t find any close FAQ matches. Try rephrasing."


# === Intent Detection ===
def detect_intent(user_input):
    input_lower = user_input.lower()
    for intent, keywords in INTENT_MAP.items():
        if any(word in input_lower for word in keywords):
            return intent
    return None

# === Normalize User Input ===
def preprocess(text):
    return re.sub(r"[^\w\s]", "", text.lower())

# === Match FAQ with Fuzzy Logic ===
def match_faq(user_input):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT question, answer FROM faqs")
        faqs = cursor.fetchall()

        questions = [row[0] for row in faqs]
        match = process.extractOne(user_input, questions, scorer=fuzz.token_sort_ratio)

        if match and match[1] >= 70:
            for q, a in faqs:
                if q == match[0]:
                    return a
        return "🤖 I couldn’t find an exact FAQ match. Try rephrasing."
    finally:
        cursor.close()
        conn.close()

# === Holiday Calendar ===

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
        cursor.execute("SELECT step_number, instructions FROM booking_procedure ORDER BY step_number")
        steps = cursor.fetchall()

        if not steps:
            return "No booking steps found."
        return "\n".join(f"📝 Step {num}: {instr}" for num, instr in steps)
    finally:
        cursor.close()
        conn.close()

# === Master Handler ===
def ask_bot(user_input):
    user_input = preprocess(user_input)
    intent = detect_intent(user_input)

    if intent == "faq":
        return match_faq(user_input)
    elif intent == "holidays":
        return get_holidays(user_input)
    elif intent == "homes":
        return get_holiday_homes(user_input)
    elif intent == "procedure":
        return get_booking_procedure()
    else:
        return "❌ Sorry, I didn’t understand your question. Ask about bookings, holidays, holiday homes, or FAQs."

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


 
