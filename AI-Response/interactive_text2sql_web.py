"""Web API version of interactive_text2sql.py.

Run this file, then open the accompanying AI Response.html page.  The original
interactive_text2sql.py remains unchanged and can still be used in the terminal.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import duckdb
import ollama

from db_helper import DB_PATH, VIEW_NAMES, get_all_view_schemas


BASE_DIR = Path(__file__).resolve().parent
RULES_FILE = BASE_DIR / "rules.txt"
HOST = "127.0.0.1"
PORT = 8000


class QueryExecutionError(Exception):
    """Keeps the generated SQL available when DuckDB rejects that SQL."""

    def __init__(self, sql, original_error):
        super().__init__(str(original_error))
        self.sql = sql


def load_rules():
    """Read the existing rule book from this script's directory."""
    if RULES_FILE.exists():
        return RULES_FILE.read_text(encoding="utf-8")
    return ""


def clean_sql(sql):
    sql = sql.strip()
    for prefix in ("```sql", "```"):
        if sql.startswith(prefix):
            sql = sql[len(prefix):]
    if sql.endswith("```"):
        sql = sql[:-3]
    return sql.strip()


def generate_and_run_question(question):
    """Handle one independent question from rules loading through query results."""
    # Each browser request starts fresh: no earlier question or prompt state is reused.
    # Load the latest rules before opening any DuckDB connection.
    custom_rules = load_rules()

    # Open and close a read-only connection while loading the current view schemas.
    schemas = get_all_view_schemas()
    if not schemas:
        raise RuntimeError("Could not read the DuckDB view schemas.")

    system_prompt = f"""
You are an expert DuckDB SQL Developer.
Your task is to write valid, executable DuckDB SQL queries based ONLY on the following available view schemas:

{schemas}

CRITICAL RULES TO FOLLOW:
{custom_rules}

Rules:
- Select the appropriate view ("Sale_Invoice" or "Purchases_Invoices") based on whether the user asks about sales or purchases.
- Output ONLY raw executable DuckDB SQL without markdown backticks (no ```sql) or explanations.
"""

    response = ollama.chat(
        model="qwen2.5-coder",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )
    sql = clean_sql(response["message"]["content"])

    # Open a new read-only connection just for executing this generated query.
    try:
        with duckdb.connect(DB_PATH, read_only=True) as connection:
            dataframe = connection.execute(sql).fetchdf()
    except Exception as error:
        raise QueryExecutionError(sql, error) from error

    # to_json produces JSON-safe values for timestamps, decimals, and nulls.
    rows = json.loads(dataframe.to_json(orient="records", date_format="iso"))
    return {
        "sql": sql,
        "columns": list(dataframe.columns),
        "rows": rows,
        "row_count": len(dataframe),
    }


class TextToSqlHandler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/query":
            self.send_json(404, {"error": "Not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            question = str(payload.get("question", "")).strip()
            if not question:
                self.send_json(400, {"error": "Enter a question first."})
                return
            self.send_json(200, generate_and_run_question(question))
        except QueryExecutionError as error:
            self.send_json(500, {"error": str(error), "sql": error.sql})
        except Exception as error:
            self.send_json(500, {"error": str(error)})

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    print(f"Local Text-to-SQL web API started at http://{HOST}:{PORT}")
    print(f"Registered Views: {', '.join(VIEW_NAMES)}")
    ThreadingHTTPServer((HOST, PORT), TextToSqlHandler).serve_forever()


if __name__ == "__main__":
    main()
