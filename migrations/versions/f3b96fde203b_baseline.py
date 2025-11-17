"""baseline

Revision ID: f3b96fde203b
Revises: 
Create Date: 2025-11-16 20:25:46.669937

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f3b96fde203b'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Use batch mode so SQLite will recreate the table under the hood
    with op.batch_alter_table('question', schema=None) as batch_op:
        # If you ONLY need to widen strings, note: SQLite ignores varchar length anyway,
        # but this keeps metadata consistent with other DBs.
        batch_op.alter_column(
            'topic',
            existing_type=sa.VARCHAR(length=100),
            type_=sa.String(length=255),
            existing_nullable=False
        )
        batch_op.alter_column(
            'exam_year',
            existing_type=sa.VARCHAR(length=50),
            type_=sa.String(length=255),
            existing_nullable=True
        )

    # If autogen added op.drop_index(...) for removed indexes and you *want* to keep them dropped,
    # leave them. If you want to keep indexes, delete those drop calls.
    # Example (commented out):
    # op.drop_index('idx_question_subject', table_name='question')
    # op.drop_index('idx_question_subject_topic', table_name='question')
    # op.drop_index('idx_question_topic', table_name='question')
    # op.drop_index('idx_userresponse_user_question', table_name='user_response')

def downgrade():
    with op.batch_alter_table('question', schema=None) as batch_op:
        batch_op.alter_column(
            'topic',
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(length=100),
            existing_nullable=False
        )
        batch_op.alter_column(
            'exam_year',
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(length=50),
            existing_nullable=True
        )

