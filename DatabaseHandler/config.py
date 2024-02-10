database_name = "local.db"
documents_table = "documents"
unverified_document_table = "unverified_documents"
user_table = "users"

document_table_creation_script = f"""
CREATE TABLE IF NOT EXISTS {documents_table} (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_name TEXT NOT NULL,
    document_summary JSON,
    document_tags JSON,
    document_raw JSON
);
"""

unverified_document_table_creation_script = f""" 
CREATE TABLE IF NOT EXISTS {unverified_document_table} (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_name TEXT NOT NULL,
    upload_date TEXT NOT NULL,
    document_category TEXT NOT NULL,
    document_source_url TEXT NOT NULL,
    document_url TEXT NOT NULL,
    upload_user_id TEXT,
    document_verified CHECK (document_verified IN (0, 1, -1)) DEFAULT 0,
    verified_count INTEGER DEFAULT 0,
    verified_user_id TEXT,
    upload_remark TEXT,
    verify_date TEXT,
    verify_remark TEXT
    );
"""

user_table_script = f"""
CREATE TABLE IF NOT EXISTS {user_table} (
    user_id TEXT PRIMARY KEY,
    user_name TEXT NOT NULL,
    user_email TEXT NOT NULL,
    user_points INTEGER DEFAULT 0
);
"""
