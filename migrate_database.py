from app import app, db
from sqlalchemy import inspect, text


# New columns required for the Ticket table
NEW_COLUMNS = {
    "caller": "VARCHAR(100)",
    "requested_for": "VARCHAR(100)",
    "location": "VARCHAR(200)",
    "contact_type": "VARCHAR(100)",
    "subcategory": "VARCHAR(100)",
    "assignment_group": "VARCHAR(100)",
    "configuration_item": "VARCHAR(200)",
    "assigned_to": "VARCHAR(100)",
    "impact": "VARCHAR(50)",
    "urgency": "VARCHAR(50)",
    "service": "VARCHAR(100)",
    "additional_comments": "TEXT",
    "work_notes": "TEXT",
}


with app.app_context():

    # Make sure existing tables are available
    db.create_all()

    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    # Ticket model normally uses the table name "ticket"
    if "ticket" not in tables:
        print("Ticket table does not exist. Creating database tables...")
        db.create_all()
        print("Database tables created successfully.")

    else:
        existing_columns = {
            column["name"]
            for column in inspector.get_columns("ticket")
        }

        with db.engine.begin() as connection:

            for column_name, column_type in NEW_COLUMNS.items():

                if column_name not in existing_columns:

                    sql = f'ALTER TABLE ticket ADD COLUMN "{column_name}" {column_type}'

                    connection.execute(text(sql))

                    print(f"Added column: {column_name}")

                else:
                    print(f"Already exists: {column_name}")

    print()
    print("====================================")
    print("DATABASE MIGRATION COMPLETED")
    print("====================================")