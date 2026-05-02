"""rename user role to barber

Revision ID: 7b9f2f8d9c2a
Revises: c93d634672a6
Create Date: 2026-05-02 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7b9f2f8d9c2a"
down_revision: Union[str, Sequence[str], None] = "c93d634672a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("role_tmp", sa.String(), nullable=True))

    op.execute(
        sa.text(
            "UPDATE users "
            "SET role_tmp = CASE WHEN role = 'user' THEN 'barber' ELSE role END"
        )
    )

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("role")
        batch_op.add_column(
            sa.Column(
                "role",
                sa.Enum("admin", "barber", name="userrole", native_enum=False),
                nullable=True,
            )
        )

    op.execute(sa.text("UPDATE users SET role = role_tmp"))

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "role",
            existing_type=sa.Enum("admin", "barber", name="userrole", native_enum=False),
            nullable=False,
        )
        batch_op.drop_column("role_tmp")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("role_tmp", sa.String(), nullable=True))

    op.execute(
        sa.text(
            "UPDATE users "
            "SET role_tmp = CASE WHEN role = 'barber' THEN 'user' ELSE role END"
        )
    )

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("role")
        batch_op.add_column(
            sa.Column(
                "role",
                sa.Enum("admin", "user", name="userrole", native_enum=False),
                nullable=True,
            )
        )

    op.execute(sa.text("UPDATE users SET role = role_tmp"))

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "role",
            existing_type=sa.Enum("admin", "user", name="userrole", native_enum=False),
            nullable=False,
        )
        batch_op.drop_column("role_tmp")
