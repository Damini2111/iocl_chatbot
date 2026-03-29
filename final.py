import re
from rapidfuzz import fuzz, process
from db import get_connection

def detect_intent(user_input):
    input_lower = user_input.lower()
    
    if "who can" in input_lower or "eligib" in input_lower:
        return "faq"
    if "cancel" in input_lower:
        return "faq"
    if "print" in input_lower:
        return "faq"
    if "confirmation" in input_lower or "how long" in input_lower or "wait" in input_lower:
        return "faq"
    if "how many nights" in input_lower or "maximum" in input_lower:
        return "faq"
    if "how to book" in input_lower or "booking procedure" in input_lower or "steps" in input_lower:
        return "procedure"
    if "holiday calendar" in input_lower or "festival" in input_lower or "diwali" in input_lower or "christmas" in input_lower:
        return "holidays"
    if "show homes" in input_lower or "guest house" in input_lower or "udaipur" in input_lower or "goa" in input_lower or "manali" in input_lower:
        return "homes"
    if "holiday home" in input_lower and "who" not in input_lower:
        return "homes"
    return "faq"

def preprocess(text):
    return re.sub(r"[^\w\s]", "", text.lower())

def ask_bot(user_input_raw):
    user_input = preprocess(user_input_raw)
    intent = detect_intent(user_input_raw.lower())
    if intent == "faq":
        if any(word in user_input_raw.lower() for word in ["all", "list", "faqs", "show all"]):
            return list_all_faqs()
        return match_faq(user_input_raw)
    elif intent == "holidays":
        return get_holidays(user_input_raw)
    elif intent == "homes":
        return get_holiday_homes(user_input_raw)
    elif intent == "procedure":
        return get_booking_procedure()
    else:
        return match_faq(user_input_raw)

def match_faq(user_input):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT question, answer FROM faqs")
        faqs = cursor.fetchall()
        if not faqs:
            return "No FAQs found."
        input_lower = user_input.lower()
        if "who can" in input_lower or "eligib" in input_lower:
            for q, a in faqs:
                if "who can" in q.lower():
                    return "FAQ: " + str(q) + "\nAnswer: " + str(a)
        if "cancel" in input_lower:
            for q, a in faqs:
                if "cancel" in q.lower():
                    return "FAQ: " + str(q) + "\nAnswer: " + str(a)
        if "print" in input_lower:
            for q, a in faqs:
                if "print" in q.lower():
                    return "FAQ: " + str(q) + "\nAnswer: " + str(a)
        if "confirmation" in input_lower or "how long" in input_lower or "wait" in input_lower:
            for q, a in faqs:
                if "confirmation" in q.lower() or "long" in q.lower():
                    return "FAQ: " + str(q) + "\nAnswer: " + str(a)
        if "how many nights" in input_lower or "maximum" in input_lower or "nights" in input_lower:
            for q, a in faqs:
                if "nights" in q.lower():
                    return "FAQ: " + str(q) + "\nAnswer: " + str(a)
        questions = [row[0] for row in faqs]
        match = process.extractOne(user_input, questions, scorer=fuzz.token_sort_ratio)
        if match and match[1] >= 60:
            for q, a in faqs:
                if q == match[0]:
                    return "FAQ: " + str(q) + "\nAnswer: " + str(a)
        return "I could not find an exact match. Try rephrasing."
    except Exception as e:
        return "Database error: " + str(e)
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_holidays(user_input):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        keyword = preprocess(user_input)
        cursor.execute("SELECT holiday, date FROM holiday_calendar")
        holidays = cursor.fetchall()
        filtered = [str(h) + " on " + str(d) for h, d in holidays if keyword in preprocess(h)]
        if filtered:
            return "\n".join(filtered)
        elif holidays:
            return "\n".join(str(h) + " on " + str(d) for h, d in holidays)
        return "No holiday data found."
    except Exception as e:
        return "Database error: " + str(e)
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_holiday_homes(user_input):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        keyword = preprocess(user_input)
        cursor.execute("SELECT holiday_home_name, location FROM holiday_homes")
        homes = cursor.fetchall()
        filtered = [str(name) + " - " + str(loc) for name, loc in homes if keyword in preprocess(name) or keyword in preprocess(loc)]
        if filtered:
            return "\n".join(filtered)
        elif homes:
            return "\n".join(str(name) + " - " + str(loc) for name, loc in homes)
        return "No holiday homes found."
    except Exception as e:
        return "Database error: " + str(e)
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_booking_procedure():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT step_number, instructions FROM booking_procedure ORDER BY step_number")
        steps = cursor.fetchall()
        if not steps:
            return "No booking steps found."
        return "\n".join("Step " + str(num) + ": " + str(instr) for num, instr in steps)
    except Exception as e:
        return "Database error: " + str(e)
    finally:
        if conn:
            cursor.close()
            conn.close()

def list_all_faqs():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT question, answer FROM faqs")
        faqs = cursor.fetchall()
        if not faqs:
            return "No FAQs found."
        response = "Here are all FAQs:\n\n"
        for i, (q, a) in enumerate(faqs, start=1):
            response += str(i) + ". " + str(q) + "\n   " + str(a) + "\n\n"
        return response.strip()
    except Exception as e:
        return "Database error: " + str(e)
    finally:
        if conn:
            cursor.close()
            conn.close()