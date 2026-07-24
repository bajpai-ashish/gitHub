import duckdb

DB_PATH = "C:/data/my_warehouse.duckdb"
VIEW_NAME = "Sale_Invoice"

def get_view_schema():
    """Dynamically fetches column names and data types for the Sale_Invoice view."""
    print(f"Connecting to DuckDB and reading schema for '{VIEW_NAME}'...")
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        schema_info = con.execute(f"DESCRIBE SELECT * FROM {VIEW_NAME}").fetchall()
        con.close()
        
        # Format the columns into clean text for Ollama
        columns_str = "\n".join([f'    "{col[0]}" {col[1]}' for col in schema_info])
        return columns_str
    except Exception as e:
        print(f"\n❌ Error connecting to DuckDB or reading view '{VIEW_NAME}':")
        print(e)
        return None

def execute_query(sql):
    """Executes the generated SQL query against DuckDB and prints formatted output."""
    print(f"\n⚡ Executing Query against {DB_PATH}...")
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        df_results = con.execute(sql).fetchdf()
        con.close()

        print("\n--- QUERY RESULT SET ---")
        if df_results.empty:
            print("Query executed successfully, but returned 0 rows.")
        else:
            print(df_results.to_string(index=False))
            print(f"\n(Total Rows Returned: {len(df_results)})")
    except Exception as e:
        print(f"\n❌ Error executing SQL on DuckDB:\n{e}")