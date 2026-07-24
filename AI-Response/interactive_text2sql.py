import os
import ollama
from db_helper import get_all_view_schemas, execute_query, VIEW_NAMES

RULES_FILE = "rules.txt"


def load_rules():
    """Reads the external rules file if it exists."""
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            return f.read()
    else:
        print(
            f"⚠️ Warning: '{RULES_FILE}' not found. Operating without custom rules."
        )
        return ""


def main():
    # 1. Load schema for all views from db_helper
    all_schemas = get_all_view_schemas()
    if not all_schemas:
        print("Exiting application due to database error.")
        return

    # 2. Load external rule book
    custom_rules = load_rules()

    # 3. Construct system prompt
    system_schema_prompt = f"""
You are an expert DuckDB SQL Developer.
Your task is to write valid, executable DuckDB SQL queries based ONLY on the following available view schemas:

{all_schemas}

CRITICAL RULES TO FOLLOW:
{custom_rules}

Rules:
- Select the appropriate view ("Sale_Invoice" or "Purchases_Invoices") based on whether the user asks about sales or purchases.
- Output ONLY raw executable DuckDB SQL without markdown backticks (no ```sql) or explanations.
"""

    print("\n" + "=" * 60)
    print("🤖 Local AI Multi-View Text-to-SQL Session Started!")
    print(f"Registered Views: {', '.join(VIEW_NAMES)}")
    print(f"Loaded rules from '{RULES_FILE}' successfully.")
    print("Type your questions below. Type 'End' or 'exit' to quit.")
    print("=" * 60 + "\n")

    # 4. Interactive loop
    while True:
        try:
            user_input = input(
                "\nEnter your question (or 'End' to quit): "
            ).strip()

            if user_input.lower() in ["end", "exit", "quit"]:
                print("\nEnding AI session. Goodbye!")
                break

            if not user_input:
                continue

            print("\nThinking...")

            # Call Ollama local model
            response = ollama.chat(
                model="qwen2.5-coder",
                messages=[
                    {"role": "system", "content": system_schema_prompt},
                    {"role": "user", "content": user_input},
                ],
            )

            # Clean generated SQL text
            generated_sql = response["message"]["content"].strip()
            for prefix in ["```sql", "```"]:
                if generated_sql.startswith(prefix):
                    generated_sql = generated_sql[len(prefix) :]
            if generated_sql.endswith("```"):
                generated_sql = generated_sql[:-3]
            generated_sql = generated_sql.strip()

            print("\n--- Generated DuckDB SQL Query ---")
            print(generated_sql)

            # Execute query and display results
            execute_query(generated_sql)

        except KeyboardInterrupt:
            print("\nSession interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()