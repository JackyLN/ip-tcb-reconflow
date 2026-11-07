"""PostgreSQL mutation guard for the audit table; owner can still disable triggers."""

from alembic import op

revision = "0002"
down_revision = "0001"


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("""CREATE FUNCTION reconflow_reject_audit_mutation() RETURNS trigger
        LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'audit events are append-only'; END; $$""")
        op.execute("""CREATE TRIGGER audit_append_only BEFORE UPDATE OR DELETE ON audit_events
        FOR EACH ROW EXECUTE FUNCTION reconflow_reject_audit_mutation()""")


def downgrade() -> None:
    raise RuntimeError("Destructive downgrade disabled")
