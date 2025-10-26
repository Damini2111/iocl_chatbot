import mysql.connector
from dotenv import load_dotenv
import os
import re
from rapidfuzz import fuzz, process

# Load environment variables
load_dotenv()

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv('DB_PASSWORD', 'NewPassword123'),  # Fallback to hardcoded if not in .env
    "database": "holiday_db",
    "port": 3306
}

# === Text Processing Functions ===
def clean(text):
    """Normalize and clean text for better matching"""
    return re.sub(r"[^\w\s]", "", text.lower().strip())

# === Intent Detection Function ===
def detect_intent(user_input):
    """Improved intent detection with prioritized matching"""
    text = clean(user_input)
    
    # Intent patterns with priority order
    intent_patterns = [
        # Booking procedure (highest priority)
        {
            'intent': 'procedure',
            'patterns': [
                'booking procedure', 'booking steps', 'booking process',
                'how to book', 'steps to book', 'procedure for booking',
                'how do i book', 'booking instructions', 'what is the process'
            ]
        },
        # Holiday calendar
        {
            'intent': 'holiday_calendar',
            'patterns': [
                'holiday calendar', 'when is', 'festival date',
                'dates for', 'upcoming holidays', 'public holidays',
                'holiday schedule', 'holiday list'
            ]
        },
        # Holiday homes
        {
            'intent': 'holiday_home',
            'patterns': [
                'holiday home', 'vacation home', 'available homes',
                'home list', 'show homes', 'list homes',
                'properties in', 'homes in', 'locations',
                'goa', 'udaipur', 'properties available'
            ]
        },
        # FAQs (lowest priority)
        {
            'intent': 'faq',
            'patterns': [
                'faq', 'question', 'cancel', 'policy',
                'availability', 'confirmation', 'login',
                'print', 'who', 'what', 'how', 'can i',
                'is there', 'do you have', 'tell me about'
            ]
        }
    ]

    # Check for each intent in priority order
    for intent_data in intent_patterns:
        for pattern in intent_data['patterns']:
            if pattern in text:
                return intent_data['intent']
    
    # Fallback partial matching
    if 'book' in text and ('how' in text or 'step' in text):
        return 'procedure'
    if 'holiday' in text and ('date' in text or 'when' in text):
        return 'holiday_calendar'
    if 'home' in text or 'property' in text:
        return 'holiday_home'
    
    return 'unknown'

# === Database Query Functions ===

def get_faq_answer(user_input, cursor):
    """Find and return the best matching FAQ answer"""
    try:
        cursor.execute("SELECT question, answer FROM faqs")
        faqs = cursor.fetchall()
        
        if not faqs:
            return "No FAQs found in the database."
        
        # Find best match using fuzzy string matching
        questions = [clean(q[0]) for q in faqs]
        best_match = process.extractOne(clean(user_input), questions, scorer=fuzz.token_sort_ratio)
        
        if best_match and best_match[1] >= 50:  # 50% match threshold
            match_index = questions.index(best_match[0])
            return f"💡 {faqs[match_index][1]}"
        
        return "🤖 I couldn't find a close match in FAQs. Try rephrasing your question."
    
    except Exception as e:
        return f"Error retrieving FAQ: {str(e)}"

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


def get_holiday_home(user_input, cursor):
    """Get holiday home information with filtering"""
    try:
        user_words = clean(user_input)
        query = "SELECT holiday_home_name, location FROM holiday_homes"
        
        # Check for location filter
        if 'goa' in user_words:
            query += " WHERE location = 'Goa'"
        elif 'udaipur' in user_words:
            query += " WHERE location = 'Udaipur'"
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if not results:
            return "No holiday homes available at the moment."
        
        response = "🏡 **Available Holiday Homes:**\n"
        for name, loc, capacity, price in results:
            response += f"• {name} in {loc} ({capacity} people) - ₹{price}/night\n"
        return response
    
    except Exception as e:
        return f"Error retrieving holiday homes: {str(e)}"

def get_booking_procedure(cursor):
    """Get detailed booking procedure"""
    try:
        cursor.execute("""
            SELECT step_number, instructions 
            FROM booking_procedure 
            ORDER BY step_number
        """)
        steps = cursor.fetchall()
        
        if not steps:
            return "Booking procedure information is not available."
        
        response = "📋 **Booking Procedure:**\n"
        for step_num, title, instructions in steps:
            response += f"\n🔹 Step {step_num}:  {instructions}\n"
        return response
    
    except Exception as e:
        return f"Error retrieving booking procedure: {str(e)}"

# === Main Query Handler ===
def answer_query(user_input):
    """Process user input and return appropriate response"""
    if not user_input or not user_input.strip():
        return "Please ask me something about holiday bookings!"
    
    # Detect intent
    intent = detect_intent(user_input)
    
    # Connect to database
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Route to appropriate handler
        if intent == "procedure":
            return get_booking_procedure(cursor)
        elif intent == "holiday_home":
            return get_holiday_home(user_input, cursor)
        elif intent == "holiday_calendar":
            return get_holidays(user_input, cursor)
        elif intent == "faq":
            return get_faq_answer(user_input, cursor)
        else:
            return ("I couldn't understand your question. Here's what I can help with:\n"
                   "1. Booking procedure and steps\n"
                   "2. Available holiday homes in Goa/Udaipur\n"
                   "3. Holiday calendar dates\n"
                   "4. FAQs about bookings\n\n"
                   "Try asking something like:\n"
                   "- 'How do I book a holiday home?'\n"
                   "- 'Show me homes in Goa'\n"
                   "- 'When is Diwali?'")
    
    except mysql.connector.Error as db_error:
        return f"Database connection error: {str(db_error)}"
    except Exception as e:
        return f"Error processing your request: {str(e)}"
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()

# === Command Line Interface ===
def run_chatbot():
    """Run the chatbot in interactive mode"""
    print("\n🌴 Holiday Booking Assistant 🌴")
    print("I can help with:")
    print("- Booking procedures\n- Holiday homes\n- Calendar dates\n- FAQs")
    print("Type 'exit' to quit\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ("exit", "quit", "bye"):
                print("Goodbye! Have a great day!")
                break
            
            response = answer_query(user_input)
            print("\nAssistant:", response, "\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print("Error:", str(e))

if __name__ == "__main__":
    run_chatbot()

    










