import duckdb

DB_PATH = "C:/data/my_warehouse.duckdb"

# Pass your views as a list/array
VIEW_NAMES = ["Sale_Invoice", "Purchases_Invoices"]


def get_all_view_schemas():
    """Dynamically fetches column metadata for all registered views in DuckDB."""
    all_schemas = []
    print(
        f"Connecting to DuckDB and reading schemas for: {', '.join(VIEW_NAMES)}..."
    )

    try:
        con = duckdb.connect(DB_PATH, read_only=True)

        for view in VIEW_NAMES:
            # Query DuckDB metadata for each view
            schema_info = con.execute(
                f"DESCRIBE SELECT * FROM {view}"
            ).fetchall()

            # Format columns into clean text
            columns_str = "\n".join(
                [f'    "{col[0]}" {col[1]}' for col in schema_info]
            )
            view_schema = f'VIEW "{view}" (\n{columns_str}\n);'

            all_schemas.append(view_schema)

        con.close()

        # Combine all view schemas into a single string separated by newlines
        return "\n\n".join(all_schemas)

    except Exception as e:
        print(f"\n❌ Error reading schemas from DuckDB:\n{e}")
        return None


def execute_query(sql):
    """Executes the generated SQL query against DuckDB and prints the formatted table."""
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