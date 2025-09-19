from app import app, db
from sqlalchemy import text

with app.app_context():
    # Make columns generous to avoid future truncation issues
    db.session.execute(text("ALTER TABLE question ALTER COLUMN topic TYPE VARCHAR(255);"))
    db.session.execute(text("ALTER TABLE question ALTER COLUMN exam_year TYPE VARCHAR(255);"))
    db.session.execute(text("ALTER TABLE question ALTER COLUMN correct_option TYPE VARCHAR(10);"))
    db.session.commit()
print("✅ Columns altered: topic=VARCHAR(255), exam_year=VARCHAR(255), correct_option=VARCHAR(10).")
