iocl_chatbot

A smart chatbot developed for Indian Oil Corporation Ltd. to assist employees with information regarding holiday homes, holiday calendars, and other related queries.


# 🛠 IOCL Chatbot

A smart assistant developed for **Indian Oil Corporation Ltd. (IOCL)** to assist employees with:

- 🏠 Holiday home availability
- 📅 Holiday calendars
- ❓ FAQs related to employee resources

Built with **Python, Flask**, and simple **NLP/ML logic** for fast, responsive interactions.

---

## 🚀 Features

- Interactive chatbot UI
- RESTful backend with Flask
- Responds to POST requests for message handling
- Loads data from `.csv` and `.db` files
- Uses a trained model (`intent_model.pkl`) for intent classification

---

## 🧠 Project Structure

iocl_chatbot/
├── apps.py # 🔥 Main Flask app
├── final.py # 🤖 Chatbot logic
├── frontjs.html # 🖥️ Frontend UI (served from /static)
├── *.csv, *.db, *.pkl # 📊 Supporting data files
├── README.md # 📘 Project info

