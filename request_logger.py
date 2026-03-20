import sqlite3

conn = sqlite3.connect('logging.db', check_same_thread=False)
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS logs (
    timestamp TIMESTAMP NOT NULL,
    question VARCHAR NOT NULL,
    answer VARCHAR NULL,
    model VARCHAR NOT NULL,
    sql_statement VARCHAR NULL,
    sql_generation_completion_tokens INT NULL,
    summary_completion_tokens INT NULL,
    latency_ms FLOAT NULL,
    success BOOLEAN NOT NULL,
    error_message VARCHAR NULL
    )''')

def add_log_to_db(timestamp: str, question_text: str, answer: str, sql: str, question_sql_token_usage: int, answer_token_usage: int, latency_ms: float, model_used: str, success: bool, error_message: str):
    cur.execute('''INSERT INTO logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                [timestamp, question_text, answer, model_used, sql,
                 question_sql_token_usage, answer_token_usage,
                 latency_ms, success, error_message])
    conn.commit()
