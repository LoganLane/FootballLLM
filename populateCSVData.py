import duckdb

conn = duckdb.connect('my_database.duckdb')
path = 'Your path to NFL Big Data Bowl 2025 CSV folder here...'
conn.sql(f"CREATE TABLE players AS SELECT * FROM read_csv_auto('{path}/players.csv')")
conn.sql(f"CREATE TABLE games AS SELECT * FROM read_csv_auto('{path}/games.csv')")
conn.sql(f"CREATE TABLE plays AS SELECT * FROM read_csv_auto('{path}/plays.csv')")
conn.sql(f"CREATE TABLE player_play AS SELECT * FROM read_csv_auto('{path}/player_play.csv')")
conn.sql(f"CREATE TABLE tracking_data AS SELECT * FROM read_csv_auto('{path}/Tracking/*.csv')")
conn.close()
