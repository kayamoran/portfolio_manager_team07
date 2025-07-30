#STEPS TO SET UP

1. python -m venv venv
# Then activate:
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate


#install dependencies

2. pip install -r requirements.txt

# create .env file and add
DATABASE_URL=sqlite:///./portfolio.db


#run the app
uvicorn app.main:app --reload

http://127.0.0.1:8000/docs
