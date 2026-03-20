import duckdb

conn = duckdb.connect('my_database.duckdb')

def get_schema():

    DB_structure = conn.sql(
        "SELECT info.table_name, info.column_name, info.data_type, column_descriptions.column_description "
        "FROM information_schema.columns AS info "
        "INNER JOIN column_descriptions ON info.column_name=column_descriptions.column_name "
        "WHERE info.table_name != 'column_descriptions'")

    rows = DB_structure.fetchall()
    db_schema = {"tables": {}}

    for row in rows:
        inner_info = {"column_name": {}, "data_type": {}, "column_description": {}}
        db_schema['tables'].setdefault(row[0], [])
        inner_info["column_name"] = row[1]
        inner_info["data_type"] = row[2]
        inner_info["column_description"] = row[3]
        db_schema['tables'][row[0]].append(inner_info)

    return db_schema

def sql_query(sql_string: str):
    try:
        query = conn.execute(sql_string)
        query_result = query.df().to_string()
        return query_result
    except duckdb.Error as e:
        raise ValueError(f"SQL execution failed: {str(e)}")


