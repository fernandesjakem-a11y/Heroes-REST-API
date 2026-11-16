import os
import mssql_python
from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode

SERVER = "hero-api.database.windows.net"
DATABASE = "heroes-api-db-3482538"

tracer = trace.get_tracer("heroes-api.database")

def get_connection():

    # Use Managed Identity in Azure.
    # Use your personal Azure login locally.
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
    
    with tracer.start_as_current_span(
        "Azure SQL Connection",
        kind=SpanKind.CLIENT,
        attributes={
            "db.system.name": "mssql",
            "db.namespace": DATABASE,
            "server.address": SERVER
        }
    ) as span:
        try:
            return mssql_python.connect(
                connection_string,
                timeout=30
            )

        except Exception as exc:
            span.record_exception(exc)
            span.set_status(
                Status(StatusCode.ERROR, "Database connection failed")
            )
            raise
