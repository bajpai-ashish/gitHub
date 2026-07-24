import duckdb
from tabulate import tabulate

DB_PATH = "C:/data/my_warehouse.duckdb"
VIEW_NAMES = ["Sale_Invoice", "Purchases_Invoices"]


def execute_query(sql):
    """Executes the generated SQL query against DuckDB and displays a formatted table with grid lines."""
    print(f"\n⚡ Executing Query against {DB_PATH}...")
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        df_results = con.execute(sql).fetchdf()
        con.close()

        print("\n--- QUERY RESULT SET ---")
        if df_results.empty:
            print("Query executed successfully, but returned 0 rows.")
        else:
            # Display formatted table with grid headers and borders
            print(
                tabulate(
                    df_results,
                    headers="keys",
                    tablefmt="grid",
                    showindex=False,
                )
            )
            print(f"\n(Total Rows Returned: {len(df_results)})")
    except Exception as e:
        print(f"\n❌ Error executing SQL on DuckDB:\n{e}")