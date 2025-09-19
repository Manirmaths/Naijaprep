from app import app, db
from sqlalchemy import text

with app.app_context():
    db.session.execute(text("ALTER TABLE question ALTER COLUMN topic TYPE VARCHAR(100);"))
    db.session.execute(text("ALTER TABLE question ALTER COLUMN exam_year TYPE VARCHAR(50);"))
    db.session.execute(text("ALTER TABLE question ALTER COLUMN correct_option TYPE VARCHAR(10);"))
    db.session.commit()
print("✅ Columns altered to topic=VARCHAR(100), exam_year=VARCHAR(50), correct_option=VARCHAR(10).")
