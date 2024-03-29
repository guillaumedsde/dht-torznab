"""Denormalize torrent file count and total size.

Revision ID: 0f3f9c7c9418
Revises: 597759a22daf
Create Date: 2023-09-23 19:02:34.505474

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0f3f9c7c9418"
down_revision = "597759a22daf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "torrents",
        sa.Column("total_size_in_bytes", sa.BIGINT(), nullable=True),
        schema="dht_torznab",
    )
    op.add_column(
        "torrents",
        sa.Column("file_count", sa.Integer(), nullable=True),
        schema="dht_torznab",
    )

    op.execute(
        """
        UPDATE dht_torznab.torrents
        SET total_size_in_bytes = files_stats.torrent_size,
            file_count = files_stats.file_count
        FROM (
                SELECT torrent_id,
                    SUM(size) AS torrent_size,
                    COUNT(*) AS file_count
                FROM dht_torznab.files
                GROUP BY torrent_id
            ) AS files_stats
        WHERE dht_torznab.torrents.id = files_stats.torrent_id;
    """,
    )

    op.alter_column(
        "torrents",
        "total_size_in_bytes",
        schema="dht_torznab",
        nullable=False,
    )
    op.alter_column(
        "torrents",
        "file_count",
        schema="dht_torznab",
        nullable=False,
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("torrents", "file_count", schema="dht_torznab")
    op.drop_column("torrents", "total_size_in_bytes", schema="dht_torznab")
    # ### end Alembic commands ###
