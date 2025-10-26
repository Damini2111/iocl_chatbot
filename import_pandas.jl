import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
import joblib

# Sample data (or load from CSV)
training_data = [
    # FAQ intent
    ("How to book?", "faq"),
    ("Who can book a holiday home?", "faq"),
    ("Can I cancel my booking?", "faq"),
    ("How to print the booking confirmation?", "faq"),
    ("How long does it take to confirm booking?", "faq"),
    ("Is cancellation possible after payment?", "faq"),
    ("What is the process to cancel bookings?", "faq"),
    ("How to check availability?", "faq"),
    ("How to log in to the portal", "faq"),
    ("Is cancellation possible after the payment", "faq"),
    ("Can a non Indian Oil employee book for a holiday home?","faq")
    ("Can i stay for more than 5 nights?", "faq"),

    # Holiday calendar intent
    ("When is Diwali","holiday_calendar"),
    ("List all upcoming holidays", "holiday_calendar"),
    ("Show me the holiday calendar", "holiday_calendar"),
    ("What holidays are there in August?", "holiday_calendar"),
    ("Tell me the date for Holi", "holiday_calendar"),
    ("Is there a holiday on 15 August?", "holiday_calendar"),
    ("When is Christmas holiday?", "holiday_calendar"),
    ("Tell me the date for Republi Day.","holiday_calendar"),
    ("List all the holidays this year.", "holiday_calendar"),



    # Holiday home intent
    ("Show me holiday homes in Udaipur", "holiday_home"),
    ("List all holiday homes", "holiday_home"),
    ("Where are the guest houses located?", "holiday_home"),
    ("Is there a holiday home in Goa?", "holiday_home"),
    ("Can I stay in Manali?", "holiday_home"),
    ("Which locations have holiday homes?", "holiday_home"),
    ("Are there homes available in Mussoorie?", "holiday_home"),
    ("List all the guest houses available.","holiday_homes"),
    ("Can i stay in Puri?","holiday_homes"),


    # Booking procedure intent
    ("What is the booking procedure?", "booking_procedure"),
    ("How do I book a holiday home?", "booking_procedure"),
    ("Tell me the steps to book", "booking_procedure"),
    ("Guide me through booking", "booking_procedure"),
    ("Steps to make a reservation", "booking_procedure"),
    ("Instruction to book a room", "booking_procedure"),
    ("How to reserve a guest house?", "booking_procedure").
    ("HOw to book a holiday home?","booking_procedure")
]


# Convert to DataFrame
df = pd.DataFrame(training_data, columns=["query", "intent"])

# Train model
model = make_pipeline(TfidfVectorizer(), LogisticRegression())
model.fit(df["query"], df["intent"])

# Save model
joblib.dump(model, "intent_model.pkl")

print("✅ Intent model trained and saved as intent_model.pkl")
