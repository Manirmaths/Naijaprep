NaijaPrep is a web application built with Flask that helps students in Nigeria prepare for exams like WAEC, JAMB, NECO, and Post-UTME.
It provides multiple-choice quizzes, user authentication, and an easy-to-use dashboard so learners can track progress and practice effectively.

✨ Features

🔑 User Authentication — Register, login, password reset via email.

📚 MCQ Practice — Quizzes powered by a database of exam-style questions.

📊 Progress Tracking — Track attempts and view quiz history.

🔒 Secure — Password hashing with Flask-Bcrypt.

📬 Email Support — Flask-Mail integration for account recovery.

🛠 Database — SQLite for development, PostgreSQL for production.

🚀 Deployment Ready — Configured for Heroku or Render.

🗂 Project Structure
NaijaPrep/
├── app/                  # Main application package
│   ├── __init__.py       # App factory
│   ├── models.py         # Database models
│   ├── routes/           # Blueprints (auth, quiz, etc.)
│   ├── templates/        # HTML templates
│   └── static/           # CSS, JS, images
├── data/                 # Question CSVs
├── create_tables.py      # Initialize database tables
├── seed_questions.py     # Load questions from CSV
├── check_db.py           # Debug DB connection
├── config.py             # Config (dev/prod)
├── run.py                # App entrypoint
├── requirements.txt      # Python dependencies
├── Procfile              # Deployment entry (Heroku/Render)
└── README.md

⚡ Getting Started (Local Development)
1. Clone the repository
git clone https://github.com/Manirmaths/Naijaprep.git
cd Naijaprep

2. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Set environment variables

Create a .env file in the project root:

SECRET_KEY=dev-secret-key
DATABASE_URL=sqlite:///app.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_password

5. Initialize the database
python create_tables.py
python seed_questions.py

6. Run the app
flask --app run.py --debug run


App will be available at:
👉 http://127.0.0.1:5000

🚀 Deployment
Heroku

Install Heroku CLI and login:

heroku login


Create app + Postgres:

heroku create maths-exam-prep
heroku addons:create heroku-postgresql:hobby-dev


Push to Heroku:

git push heroku main


Open app:

heroku open

Render

Already includes render_start.sh and Procfile.

Create a Web Service → Connect repo → set build/start commands.

Add environment variables under Settings → Environment.

🧰 Tech Stack

Backend: Flask, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt, Flask-Mail

Database: SQLite (dev), PostgreSQL (prod)

Frontend: Jinja2 templates, Bootstrap

Deployment: Heroku / Render

Language: Python 3.11+

🧑🏽‍💻 Contributing

Contributions are welcome!

Fork the repo

Create a new branch (feature/quiz-timer)

Commit changes and push

Open a Pull Request

📜 License

This project is licensed under the MIT License
.

🌍 Roadmap

 Add subject/topic filtering for quizzes

 Add timed exam mode

 Add leaderboard for competitive learning

 Add analytics dashboard

🙌 Acknowledgements

Inspired by the vision to help Nigerian students succeed in WAEC/JAMB/NECO.

Built with ❤️ using Flask and Python