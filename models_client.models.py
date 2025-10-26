


import mysql.connector
from rapidfuzz import fuzz, process
import re

# === DB CONFIGURATION ===
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "NewPassword123",
    "database": "holiday_db",
    "port": 3306
}

# === INTENT KEYWORDS ===
INTENT_MAP = {
    "homes": ["holiday home", "home", "guest house", "location", "udaipur", "manali", "goa", "nainital", "mussoorie", "ooty"],
    "holidays": ["holiday", "calendar", "festival", "deepawali", "diwali", "christmas", "date"],
    "procedure": ["steps", "procedure", "how to book", "instructions", "booking process"],
    "faq": ["who", "how", "what", "when", "can", "cancel", "book", "print", "confirmation", "login"]
}

# === Detect Intent ===
def detect_intent(user_input):
    scores = {}

    for intent, keywords in INTENT_MAP.items():
        max_score = 0
        for keyword in keywords:
            score = fuzz.partial_ratio(user_input.lower(), keyword)
            if score > max_score:
                max_score = score
        scores[intent] = max_score

    best_intent = max(scores, key=scores.get)
    if scores[best_intent] >= 50:  # You can tune this threshold
        return best_intent
    else:
        return None



# === Normalize User Input ===
def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text

# === Holiday Homes with Location Filter ===
def get_holiday_homes(user_input):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "SELECT holiday_home_name, location FROM holiday_homes"
        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            return "No holiday homes found."

        # Filter if location mentioned
        input_lower = user_input.lower()
        filtered = [row for row in results if any(loc.lower() in input_lower for loc in row[1].split())]

        homes = filtered if filtered else results  # show all if no specific match
        return "\n".join(f"🏡 {row[0]} — {row[1]}" for row in homes)

    finally:
        cursor.close()
        conn.close()

# === Holiday Calendar (with Specific Holiday Match) ===
def get_holidays(user_input):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "SELECT holiday, date FROM holiday_calendar"
        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            return "No holidays found."

        input_lower = user_input.lower()
        for holiday, date in results:
            if holiday.lower() in input_lower:
                return f"🎉 {holiday} is on {date}"

        return "\n".join(f"🎉 {holiday} — {date}" for holiday, date in results)

    finally:
        cursor.close()
        conn.close()

# === Booking Procedure Steps ===
def get_booking_procedure():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT step_number, instructions FROM booking_procedure ORDER BY step_number")
        steps = cursor.fetchall()

        if not steps:
            return "No booking procedure found."

        return "\n".join(f"📝 Step {step}: {instr}" for step, instr in steps)

    finally:
        cursor.close()
        conn.close()

# === Fuzzy Match FAQ ===
def get_faq_answer(user_input):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT question, answer FROM faqs")
        faqs = cursor.fetchall()

        questions = [q for q, _ in faqs]
        best_match = process.extractOne(user_input, questions, scorer=fuzz.token_sort_ratio)

        if best_match and best_match[1] >= 70:
            matched_q = best_match[0]
            for q, a in faqs:
                if q == matched_q:
                    return a

        return "❌ Sorry, I couldn't find a matching FAQ. Try rephrasing."

    finally:
        cursor.close()
        conn.close()

# === Chatbot Engine ===
def ask_bot(user_input):
    intent = detect_intent(user_input)

    if intent == "homes":
        return get_holiday_homes(user_input)

    elif intent == "holidays":
        return get_holidays(user_input)

    elif intent == "procedure":
        return get_booking_procedure()

    elif intent == "faq":
        return get_faq_answer(user_input)

    else:
        return "❌ Sorry, I didn’t understand that. Try asking about FAQs, bookings, holidays, or homes."

# === Command-Line Loop ===
if __name__ == "__main__":
    print("🤖 Welcome to IOCL Chatbot!")
    print("Ask about: FAQs, booking procedure, holiday calendar, or holiday homes.")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("❓ Your Question: ")
        if user_input.lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break
        response = ask_bot(user_input)
        print(response + "\n")


