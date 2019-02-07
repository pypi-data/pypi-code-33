import os
import sys

from dotenv import load_dotenv, find_dotenv
import MySQLdb

def get_db_creds():
    load_dotenv(find_dotenv())

    creds = {}
    creds['DB_HOST'] = os.getenv('DB_HOST')
    creds['DB_USER'] = os.getenv('DB_USER')
    creds['DB_PASS'] = os.getenv('DB_PASS')
    creds['DB_NAME'] = os.getenv('DB_NAME')

    return creds

def conn():
    creds = get_db_creds()
    return MySQLdb.connect(
        host=creds['DB_HOST'],
        user=creds['DB_USER'],
        passwd=creds['DB_PASS'],
        db=creds['DB_NAME']
    )

def get_time_of_last_track_play(username):
    col_name = 'time_of_last_track_played'

    con = conn()
    cur = MySQLdb.cursors.DictCursor(con)
    query = f'SELECT {col_name} from users where username="{username}"'
    cur.execute(query)
    result = cur.fetchone()
    con.close()

    if not result:
        print('finding time of last track play, did not find user in db, exiting')
        sys.exit(1)
    else:
        return result[col_name]

def update_time_of_last_track_play(username, seconds_since_epoch):
    col_name = 'time_of_last_track_played'
    query = f'UPDATE users SET {col_name}="{seconds_since_epoch}" where username="{username}"'

    con = conn()
    cur = MySQLdb.cursors.DictCursor(con)
    cur.execute(query)
    con.commit()
    con.close()

def save_track_if_not_exists(track):
    '''
    track - dict, keys: name, uri, id, duration_ms
    '''
    con = conn()
    cur = MySQLdb.cursors.DictCursor(con)

    # Does track exist?
    query = f"select * from tracks where spotify_uri='{track['uri']}'"
    cur.execute(query)
    result = cur.fetchone()
    if result:
        return

    query = f'''
        INSERT IGNORE INTO tracks 
            (name, spotify_uri, spotify_id, duration_ms)
        VALUES
            (%s, %s, %s, %s)
    '''

    values = (track['name'], track['uri'], track['id'], track['duration_ms'])
    cur.execute(query, values)
    con.commit()
    con.close()

def get_all_users():
    query = f'''
    SELECT username from users
    '''

    con = conn()
    cur = MySQLdb.cursors.DictCursor(con)
    cur.execute(query)
    results = cur.fetchall()
    con.close()

    return_value = []
    for x in results:
        return_value.append(x['username'])

    return return_value

def save_played_song(username, track_uri, played_at):
    ''' Save played track into songs_played table
    Convert track_uri to the pk auto inc track_id from mysql
    '''
    user_id = get_user_id_for_username(username)
    track_id = get_track_id_for_track_uri(track_uri)

    query = f'''
        INSERT INTO songs_played
            (track_id, user_id, played_at)
        VALUES
                (%s, %s, %s)
    '''

    values = (track_id, user_id, played_at)
    con = conn()
    cur = MySQLdb.cursors.DictCursor(con)
    cur.execute(query, values)
    con.commit()
    con.close()

def get_track_id_for_track_uri(track_uri):
    col_name = 'id'
    query = f'SELECT {col_name} from tracks where spotify_uri ="{track_uri}"'

    con = conn()
    cur = MySQLdb.cursors.DictCursor(con)
    cur.execute(query)
    result = cur.fetchone()
    con.close()

    if not result:
        print(f'did not find track by track_uri {track_uri} in db, exiting')
        sys.exit(1)
    else:
        return result[col_name]

def get_user_id_for_username(username):
    col_name = 'id'
    query = f'SELECT {col_name} from users where username="{username}"'

    con = conn()
    cur = MySQLdb.cursors.DictCursor(con)
    cur.execute(query)
    result = cur.fetchone()
    con.close()

    if not result:
        print('did not find user in db, exiting')
        sys.exit(1)
    else:
        return result[col_name]

'''
  TODO: use release_start, release_end
  TODO it would be nice to have an abstraction to build a query
    so that I'm not building a string :) -- see https://github.com/kayak/pypika

  Some work would be necessary here if I ever implement another 'agby' or aggregate by field 
  other than 'track_id' in recently-played-playlists-parser. I don't have plans for that at this time.
  One useful example is aggregate by 'album_id' to find most played albums.
'''
def map_playlist_params_to_query(filter_args):
    ''' Turn filter_args into a SQL query.
    '''
    user_id = get_user_id_for_username(filter_args['username'])

    # TODO avoid sql injection here. formatting params via execute only
    # works for values in WHERE clause according to the docs
    # however! punt for now, since the mysql user doesn't have drop or delete grants :)
    query = """
    SELECT spotify_id FROM
        (
            SELECT
                COUNT(*) as num_plays,
                track_id as id
            FROM songs_played
                WHERE
                    user_id={user_id}
                    AND played_at > {time_begin}
                    AND played_at < {time_end}
                GROUP BY {agby}
        ) t1
        INNER JOIN tracks using (id)
    """.format(
        user_id=user_id,
        time_begin=filter_args['time_begin'],
        time_end=filter_args['time_end'],
        agby=filter_args['agby'],
    )

    # If comparator and count are set, add them to the query.
    if filter_args['comparator'] != -1 and filter_args['count'] != -1:
        order_by = get_order_by(filter_args['comparator'])
        comparator = str_of_comparator(filter_args['comparator'])
        query += f" WHERE num_plays {comparator} {filter_args['count']} ORDER BY num_plays {order_by}"
    # If limit is set, add it to the query.
    if filter_args['limit'] != -1:
        query += f" LIMIT {filter_args['limit']}"

    return query

def get_order_by(comparator):
    '''
    Set the ORDER BY value for the query so that it makes sense
    with the comparator in combination with a LIMIT clause.
    comparator values:
        0: <
        1: <=
        2: >
        3: >=

    Example:
        100 tracks with >= 10 plays, we want to order by DESC and LIMIT 100
    '''
    if comparator == 0 or comparator == 1:
        return 'ASC'
    elif comparator == 2 or comparator == 3:
        return 'DESC'
    else:
        raise Exception('Bad value for comparator')

def str_of_comparator(comparator):
    if comparator == 0:
        return "<"
    elif comparator == 1:
        return "<="
    elif comparator == 2:
        return ">"
    elif comparator == 3:
        return ">="
    else:
        raise Exception('Bad value for comparator')

def exec_process_playlist_query(query):
    con = conn()
    cur = MySQLdb.cursors.DictCursor(con)
    cur.execute(query)
    results = cur.fetchall()
    con.close()

    return_value = []
    for x in results:
        return_value.append(x['spotify_id'])

    return return_value
    
