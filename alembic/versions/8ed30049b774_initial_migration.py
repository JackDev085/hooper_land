"""initial_migration

Revision ID: 8ed30049b774
Revises: 
Create Date: 2026-07-13 14:59:37.449519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '8ed30049b774'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # 1. Drop old tables if they exist
    if 'order_items' in tables:
        op.drop_table('order_items')
    if 'orders' in tables:
        op.drop_table('orders')

    # 2. Alter exercises columns if table exists
    if 'exercises' in tables:
        columns = {c['name']: c for c in inspector.get_columns('exercises')}
        with op.batch_alter_table('exercises') as batch_op:
            if 'desc' in columns:
                batch_op.alter_column('desc',
                           existing_type=sa.VARCHAR(),
                           nullable=True)
            if 'created_at' in columns:
                batch_op.alter_column('created_at',
                           existing_type=sa.VARCHAR(),
                           nullable=True)
            if 'updated_at' in columns:
                batch_op.alter_column('updated_at',
                           existing_type=sa.VARCHAR(),
                           nullable=True)
        
        # Drop constraint if it exists
        try:
            op.drop_constraint('exercises_workouts_fk', 'exercises', type_='foreignkey')
        except Exception:
            pass

    # 3. Alter games updated_at if table exists
    if 'games' in tables:
        columns = {c['name']: c for c in inspector.get_columns('games')}
        if 'updated_at' in columns:
            try:
                with op.batch_alter_table('games') as batch_op:
                    batch_op.alter_column('updated_at',
                               existing_type=postgresql.TIMESTAMP() if conn.dialect.name == 'postgresql' else sa.DATETIME(),
                               type_=sqlmodel.sql.sqltypes.AutoString(),
                               existing_nullable=True)
            except Exception:
                pass

    # 4. Add columns to users table
    if 'users' in tables:
        columns = {c['name']: c for c in inspector.get_columns('users')}
        
        # Add new columns if not present
        if 'sex' not in columns:
            op.add_column('users', sa.Column('sex', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        if 'position' not in columns:
            op.add_column('users', sa.Column('position', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        if 'birth_date' not in columns:
            op.add_column('users', sa.Column('birth_date', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        if 'phone' not in columns:
            op.add_column('users', sa.Column('phone', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        if 'weigth' not in columns:
            op.add_column('users', sa.Column('weigth', sa.Float(), nullable=True))
        if 'heigth' not in columns:
            op.add_column('users', sa.Column('heigth', sa.Float(), nullable=True))

        with op.batch_alter_table('users') as batch_op:
            if 'name' in columns:
                batch_op.alter_column('name',
                           existing_type=sa.VARCHAR(),
                           nullable=False)
            if 'role' in columns:
                batch_op.alter_column('role',
                           existing_type=sa.TEXT(),
                           type_=sqlmodel.sql.sqltypes.AutoString(),
                           existing_nullable=False)
            if 'instagram' in columns:
                batch_op.alter_column('instagram',
                           existing_type=sa.TEXT(),
                           type_=sqlmodel.sql.sqltypes.AutoString(),
                           existing_nullable=True)
            if 'description' in columns:
                batch_op.alter_column('description',
                           existing_type=sa.TEXT(),
                           type_=sqlmodel.sql.sqltypes.AutoString(),
                           existing_nullable=True)
            if 'streak_count' in columns:
                batch_op.alter_column('streak_count',
                           existing_type=sa.INTEGER(),
                           nullable=False)

        # Alter index / constraints
        indexes = [idx['name'] for idx in inspector.get_indexes('users')]
        if 'ix_users_usuario' in indexes:
            op.drop_index('ix_users_usuario', table_name='users')
        if 'ix_users_username' not in indexes:
            op.create_index('ix_users_username', 'users', ['username'], unique=True)
            
        try:
            op.create_unique_constraint(None, 'users', ['email'])
        except Exception:
            pass

    # 5. Alter workouts table if it exists
    if 'workouts' in tables:
        columns = {c['name']: c for c in inspector.get_columns('workouts')}
        with op.batch_alter_table('workouts') as batch_op:
            if 'slug' in columns:
                batch_op.alter_column('slug',
                           existing_type=sa.VARCHAR(),
                           nullable=True)
            if 'created_at' in columns:
                batch_op.alter_column('created_at',
                           existing_type=sa.VARCHAR(),
                           nullable=True)
            if 'updated_at' in columns:
                batch_op.alter_column('updated_at',
                           existing_type=sa.VARCHAR(),
                           nullable=True)

        indexes = [idx['name'] for idx in inspector.get_indexes('workouts')]
        if 'ix_treinos_slug' in indexes:
            op.drop_index('ix_treinos_slug', table_name='workouts')
        if 'ix_workouts_slug' not in indexes:
            op.create_index('ix_workouts_slug', 'workouts', ['slug'], unique=False)

    # 6. Create athlete evolution tables if they don't exist
    if 'daily_journals' not in tables:
        op.create_table('daily_journals',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('date', sa.String(), nullable=False),
            sa.Column('sleep_hours', sa.Float(), nullable=False),
            sa.Column('water_liters', sa.Float(), nullable=False),
            sa.Column('stretched', sa.Boolean(), nullable=False),
            sa.Column('mobility', sa.Boolean(), nullable=False),
            sa.Column('trained_basketball', sa.Boolean(), nullable=False),
            sa.Column('gym', sa.Boolean(), nullable=False),
            sa.Column('cardio', sa.Boolean(), nullable=False),
            sa.Column('energy', sa.Integer(), nullable=False),
            sa.Column('muscle_pain', sa.Integer(), nullable=False),
            sa.Column('motivation', sa.Integer(), nullable=False),
            sa.Column('confidence', sa.Integer(), nullable=False),
            sa.Column('notes', sa.String(), nullable=True)
        )
        op.create_index('ix_daily_journals_user_id', 'daily_journals', ['user_id'])
        op.create_index('ix_daily_journals_date', 'daily_journals', ['date'])

    if 'game_stats' not in tables:
        op.create_table('game_stats',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('date', sa.String(), nullable=False),
            sa.Column('opponent', sa.String(), nullable=False),
            sa.Column('result', sa.String(), nullable=False),
            sa.Column('points', sa.Integer(), nullable=False),
            sa.Column('ft_made', sa.Integer(), nullable=False),
            sa.Column('ft_attempted', sa.Integer(), nullable=False),
            sa.Column('fg2_made', sa.Integer(), nullable=False),
            sa.Column('fg2_attempted', sa.Integer(), nullable=False),
            sa.Column('fg3_made', sa.Integer(), nullable=False),
            sa.Column('fg3_attempted', sa.Integer(), nullable=False),
            sa.Column('assists', sa.Integer(), nullable=False),
            sa.Column('turnovers', sa.Integer(), nullable=False),
            sa.Column('offensive_rebounds', sa.Integer(), nullable=False),
            sa.Column('defensive_rebounds', sa.Integer(), nullable=False),
            sa.Column('steals', sa.Integer(), nullable=False),
            sa.Column('blocks', sa.Integer(), nullable=False),
            sa.Column('fouls_committed', sa.Integer(), nullable=False),
            sa.Column('fouls_drawn', sa.Integer(), nullable=False)
        )
        op.create_index('ix_game_stats_user_id', 'game_stats', ['user_id'])
        op.create_index('ix_game_stats_date', 'game_stats', ['date'])

    if 'goals' not in tables:
        op.create_table('goals',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('goal_type', sa.String(), nullable=False),
            sa.Column('metric', sa.String(), nullable=False),
            sa.Column('target_value', sa.Float(), nullable=False),
            sa.Column('start_date', sa.String(), nullable=False),
            sa.Column('end_date', sa.String(), nullable=False),
            sa.Column('completed', sa.Boolean(), nullable=False, default=False)
        )
        op.create_index('ix_goals_user_id', 'goals', ['user_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('goals')
    op.drop_table('game_stats')
    op.drop_table('daily_journals')
