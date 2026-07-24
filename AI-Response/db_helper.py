import duckdb
import pandas as pd
from tabulate import tabulate

DB_PATH = "C:/data/my_warehouse.duckdb"
VIEW_NAMES = ["Sale_Invoice", "Purchases_Invoices"]

# Format large floating-point numbers to standard decimals instead of scientific notation
pd.options.display.float_format = "{:,.2f}".format


def get_all_view_schemas():
    """Dynamically fetches column metadata for all registered views in DuckDB."""
    all_schemas = []
    print(
        f"Connecting to DuckDB and reading schemas for: {', '.join(VIEW_NAMES)}..."
    )

    try:
        con = duckdb.connect(DB_PATH, read_only=True)

        for view in VIEW_NAMES:
            schema_info = con.execute(
                f"DESCRIBE SELECT * FROM {view}"
            ).fetchall()
            columns_str = "\n".join(
                [f'    "{col[0]}" {col[1]}' for col in schema_info]
            )
            view_schema = f'VIEW "{view}" (\n{columns_str}\n);'
            all_schemas.append(view_schema)

        con.close()
        return "\n\n".join(all_schemas)

    except Exception as e:
        print(f"\n❌ Error reading schemas from DuckDB:\n{e}")
        return None


def execute_query(sql):
    """Executes the generated SQL query against DuckDB and displays a formatted grid table."""
    print(f"\n⚡ Executing Query against {DB_PATH}...")
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        df_results = con.execute(sql).fetchdf()
        con.close()

        print("\n--- QUERY RESULT SET ---")
        if df_results.empty:
            print("Query executed successfully, but returned 0 rows.")
        else:
            # Display formatted table with grid lines and commas for numbers
            print(
                tabulate(
                    df_results,
                    headers="keys",
                    tablefmt="grid",
                    showindex=False,
                    floatfmt=",",
                )
            )
            print(f"\n(Total Rows Returned: {len(df_results)})")
    except Exception as e:
        print(f"\n❌ Error executing SQL on DuckDB:\n{e}")