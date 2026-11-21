import os
import mssql_python

from opentelemetry import trace
from opentelemetry.trace import SpanKind

# ------------------------------------------------------------
# Database configuration
# ------------------------------------------------------------

SERVER = "hero-api.database.windows.net"
DATABASE = "heroes-api-db-3482538"

tracer = trace.get_tracer("heroes-api.database")

# ------------------------------------------------------------
# Database connection
# ------------------------------------------------------------

def get_connection():

    authentication = os.getenv(
        "DB_AUTHENTICATION",
        "ActiveDirectoryDefault"
    )

    connection_string = (
        f"Server={SERVER};"
        f"Database={DATABASE};"
        f"Authentication={authentication};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )

    # Track the database connection in Application Insights.
    with tracer.start_as_current_span(
        "Azure SQL Connection",
        kind=SpanKind.CLIENT,
        attributes={
            "db.system.name": "mssql",
            "db.namespace": DATABASE,
            "server.address": SERVER
        }
    ):
        return mssql_python.connect(
            connection_string,
            timeout=30
        )