"""
Database Initialization Script for SahAI-Coop
Executed to initialize the MySQL database schema and populate seed data.
"""

import os
import sys
import argparse
from pathlib import Path
from urllib.parse import urlparse

# Ensure parent directory is in path so we can import app modules if needed
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    import pymysql
except ImportError:
    print("Error: PyMySQL is not installed. Run 'pip install pymysql cryptography'.")
    sys.exit(1)

from dotenv import load_dotenv

# Load environment variables from backend/.env or root .env
backend_env = BASE_DIR / "backend" / ".env"
root_env = BASE_DIR / ".env"
if backend_env.exists():
    load_dotenv(backend_env)
elif root_env.exists():
    load_dotenv(root_env)
else:
    load_dotenv()


def parse_db_url(db_url: str):
    """
    Parses a connection URL like:
    mysql+pymysql://username:password@localhost:3306/sahai_coop_db
    or mysql://username:password@localhost:3306/sahai_coop_db
    """
    # Normalize scheme
    if db_url.startswith("mysql+pymysql://"):
        db_url = db_url.replace("mysql+pymysql://", "mysql://", 1)
    
    parsed = urlparse(db_url)
    user = parsed.username or "root"
    password = parsed.password or ""
    host = parsed.hostname or "localhost"
    port = parsed.port or 3306
    db_name = parsed.path.lstrip("/") or "sahai_coop_db"
    
    return {
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "database": db_name,
    }


def execute_sql_file(connection, file_path: Path):
    """Executes a multi-statement SQL script file safely."""
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split by semicolon while ignoring comments and semicolons within string literals
    statements = []
    current_stmt = []
    in_string = False
    quote_char = None
    
    for line in sql_content.splitlines():
        trimmed = line.strip()
        if not in_string and (trimmed.startswith("--") or trimmed.startswith("/*")):
            continue
            
        i = 0
        while i < len(line):
            c = line[i]
            if c in ("'", '"', '`'):
                if not in_string:
                    in_string = True
                    quote_char = c
                elif quote_char == c:
                    # check for escape
                    if i > 0 and line[i - 1] == '\\':
                        pass
                    else:
                        in_string = False
                        quote_char = None
            elif c == ';' and not in_string:
                current_stmt.append(line[:i])
                stmt_str = "\n".join(current_stmt).strip()
                if stmt_str:
                    statements.append(stmt_str)
                current_stmt = []
                line = line[i + 1:]
                i = -1
            i += 1
        if line:
            current_stmt.append(line)
            
    if current_stmt:
        stmt_str = "\n".join(current_stmt).strip()
        if stmt_str:
            statements.append(stmt_str)

    cursor = connection.cursor()
    executed_count = 0
    try:
        for stmt in statements:
            stmt_clean = stmt.strip()
            if stmt_clean:
                cursor.execute(stmt_clean)
                executed_count += 1
        connection.commit()
        print(f"Successfully executed {executed_count} statements from {file_path.name}")
        return True
    except Exception as e:
        connection.rollback()
        print(f"Error executing SQL in {file_path.name}: {e}")
        return False
    finally:
        cursor.close()


def init_database(seed: bool = True, drop_existing: bool = False):
    """Initializes the database schema and seeds."""
    db_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/sahai_coop_db")
    config = parse_db_url(db_url)
    
    print("=" * 60)
    print("SahAI-Coop Database Initializer")
    print(f"Host:     {config['host']}:{config['port']}")
    print(f"User:     {config['user']}")
    print(f"Database: {config['database']}")
    print("=" * 60)

    # 1. Connect to MySQL server (without specifying DB to allow creating it)
    try:
        server_conn = pymysql.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            charset="utf8mb4",
            autocommit=True
        )
        print("Connected to MySQL server.")
    except Exception as e:
        print(f"Failed to connect to MySQL server at {config['host']}:{config['port']}.")
        print(f"Details: {e}")
        print("\nPlease check that MySQL is running and credentials in your .env are correct.")
        return False

    with server_conn.cursor() as cur:
        if drop_existing:
            print(f"Dropping database `{config['database']}` if exists...")
            cur.execute(f"DROP DATABASE IF EXISTS `{config['database']}`;")
            
        print(f"Ensuring database `{config['database']}` exists...")
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{config['database']}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
    server_conn.close()

    # 2. Connect to the specific database
    try:
        db_conn = pymysql.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            charset="utf8mb4",
            autocommit=False
        )
    except Exception as e:
        print(f"Failed to connect to `{config['database']}`: {e}")
        return False

    # 3. Apply Schema
    schema_path = BASE_DIR / "database" / "schemas" / "schema.sql"
    print(f"Applying schema from {schema_path}...")
    success = execute_sql_file(db_conn, schema_path)
    if not success:
        db_conn.close()
        return False

    # 4. Apply Seed Data if requested
    if seed:
        seed_path = BASE_DIR / "database" / "seeds" / "seed_data.sql"
        print(f"Applying seed data from {seed_path}...")
        execute_sql_file(db_conn, seed_path)

    db_conn.close()
    print("\nDatabase initialization completed successfully!")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize SahAI-Coop MySQL Database")
    parser.add_argument("--seed", action="store_true", default=True, help="Populate seed data (default: True)")
    parser.add_argument("--no-seed", dest="seed", action="store_false", help="Skip seed data population")
    parser.add_argument("--drop", action="store_true", default=False, help="Drop existing database before creating")
    
    args = parser.parse_args()
    success = init_database(seed=args.seed, drop_existing=args.drop)
    sys.exit(0 if success else 1)
