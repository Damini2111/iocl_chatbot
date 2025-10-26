import spacy

nlp = spacy.load("en_core_web_sm")

def get_intent(user_input):
    user_input = user_input.lower()
    
    if "holiday" in user_input and ("calendar" in user_input or "list" in user_input):
        return "holiday_calendar"
    elif "holiday home" in user_input or "book" in user_input:
        return "holiday_home_info"
    elif "faq" in user_input or "question" in user_input:
        return "holiday_faq"
    else:
        return "unknown"
