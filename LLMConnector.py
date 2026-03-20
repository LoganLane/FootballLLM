import os
import time

from openai import OpenAI
from database import get_schema, sql_query
from dotenv import load_dotenv
import json



load_dotenv()
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
print(API_KEY)
#client = OpenAI(base_url="http://localhost:8000/v1", api_key="null")

client = OpenAI(base_url=API_URL, api_key=API_KEY)
model = "Kimi-K2.5"

def return_question_sql(question):
    developer_prompt = '''
    You are an expert American football analyst. You are answering questions from the head coach of a professional football team. 
    To answer their question, you will reference a database filled with football analytics data by looking at the schema for each column to find relevant information.
    You will return only an SQL statement that can be used to query the database for the relevant information. Do not return any additional text outside of SQL.
    Any SQL returned by you should run without having to make any edits. Do not return a multiline string, only return one large string.
    Rules:
    * Position constraints - When a coach mentions passing, you should only look at QBs unless otherwise specified. For rushing, you should look at RBs and FBs. For receiving, look at WRs and TEs. To do this, join the players table and use a where clause on the position column to properly filter for the appropriate player group. 
    * `week` lives in the `games` table and must be joined via `gameId` — never filter on `week` directly from `plays` or `player_play`
    * Coordinate system `x` runs 0-120 yards including both end zones, `y` runs 0-53.3 yards sideline to sideline. One thing to pay close attention to is that playDirection can have an effect on the actual position of a player. For example, depending on the playDirection, a player on the 20 yard line might have x = 20 or x = 100. When play direction is 'left', x increases toward the left end zone. When play direction is 'right', x increases toward the right end zone. Use playDirection from the tracking_data table to correctly interpret x coordinates."
    * If nflId is NULL, that represents the position of the ball for a given play. Be sure to filter for where nflId is not null when looking for specific player positions. You can also find the position of the ball in the tracking data table with the displayName, 'football.'
    * You may not always have the answer to a question directly in a column in the database. It is your job to use what data you do have available to compute the requested stats.
    * If a query is vague where there could be multiple answers, you should provide multiple answers with reasoning as to why you picked the answers that you did.  
    Here is the schema for the database: 
    ''' + format_database_schema()
    request = client.chat.completions.create(
        model="Kimi-K2.5",
        messages=[
            {"role": "system", "content": f"{developer_prompt}"},
            {
                "role": "user",
                "content": f"{question}",
             },
        ],
    )
    sql_statement = request.choices[0].message.content
    token_usage = request.usage.completion_tokens
    return sql_statement, token_usage


def format_database_schema():
    db_schema = get_schema()
    schema_formatted = json.dumps(db_schema['tables'], indent=2)
    return schema_formatted

def return_sql_query_results(sql_statement):
    results = sql_query(sql_statement)
    return results

def return_results_english(question, sql_statement, sql_results):
    request = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": f"{question_answer_prompt}"},
            {
                "role": "user",
                "content": f"Question: {question}, SQL Statement: {sql_statement}, SQL Results: {sql_results}",
            },
        ],
    )
    response = request.choices[0].message.content
    token_usage = request.usage.completion_tokens
    return response, token_usage

def respond_to_api(question_text: str):
    start_time = time.time()

    sql_string, question_sql_token_usage = return_question_sql(question_text)


    answer, answer_token_usage = return_results_english(question_text, sql_string, return_sql_query_results(sql_string))
    end_time = time.time()
    return question_text, answer, sql_string, question_sql_token_usage, answer_token_usage, (end_time - start_time) * 1000, model


question_answer_prompt = '''
You are an expert American football analyst. The head coach has asked you a question. You will be given the question along with the SQL statement and the SQL statement results.
It is your job to form a simple sentence in English to answer the coach's question. 
'''