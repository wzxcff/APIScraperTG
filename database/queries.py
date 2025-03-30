from psycopg2.extras import execute_values


def insert_user(element, conn):
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO users (user_id, first_name, last_name, username, avatar, is_bot)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
            RETURNING user_id;
            """, (
            element["sender"]["user_id"], element["sender"]["first_name"], element["sender"]["last_name"], element["sender"]["username"],
            element["sender"]["avatar"], element["sender"]["is_bot"])
        )


def insert_geo(el, group_id, conn, geo_ids):
    geo = el.get("geo")
    if not geo:
        return None

    lat, lon = geo.get("latitude"), geo.get("longitude")
    if (lat, lon) in geo_ids:
        return geo_ids[(lat, lon)]

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO geo_locations (m_id, group_id, sender_id, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """, (el['id'], group_id, el['sender']['user_id'], lat, lon)
        )
        geo_id = cursor.fetchone()[0]
        geo_ids[(lat, lon)] = geo_id
        return geo_id


def insert_group_info(group_info, conn):
    entry = (
        group_info["id"],
        group_info["title"],
        group_info["username"],
        group_info["about"]
    )

    with conn.cursor() as cursor:
        cursor.execute(
            """ INSERT INTO groups (group_id, title, username, about)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (group_id) DO NOTHING;
            """, entry
        )


def insert_message(batch, group_id, conn):
    if conn is None:
        print("Failed to connect to the database.")
        return

    geo_ids = {}
    values = []

    with conn.cursor() as cursor:
        for el in batch:
            if el["sender"]["user_id"]:
                insert_user(el, conn)

            geo_id = insert_geo(el, group_id, conn, geo_ids)

            values.append((
                el["id"],
                el["text"],
                el["date"],
                el["changed_at"],
                el["sender"]["user_id"],
                group_id,
                el["media"],
                geo_id
            ))

        query = """
            INSERT INTO messages 
            (m_id, text, date, changed_at, sender_id, group_id, media, geo_id) 
            VALUES %s;
        """
        execute_values(cursor, query, values)
        conn.commit()

    values = []
    for el in batch:
        geo = el.get("geo")
        geo_id = geo_ids.get((geo.get("latitude"), geo.get("longitude"))) if geo else None

        entry = (
            el["id"],
            el["text"],
            el["date"],
            el["changed_at"],
            el["sender"]["user_id"],
            group_id,
            el["media"],
            geo_id
        )
        values.append(entry)

    query = """
        INSERT INTO messages 
        (m_id, text, date, changed_at, sender_id, group_id, media, geo_id) 
        VALUES %s
        ON CONFLICT (id) DO NOTHING;
    """

    with conn.cursor() as cursor:
        execute_values(cursor, query, values)
        conn.commit()


def insert_pinned_messages(batch, group_id, conn):
    if conn is None:
        print("Failed to connect to the database.")
        return

    geo_ids = {}
    values = []

    with conn.cursor() as cursor:
        for el in batch:

            geo_id = insert_geo(el, group_id, conn, geo_ids)

            entry = (
                el["id"],
                el["text"],
                el["from_id"],
                el["date"],
                el["changed_at"],
            )

            values.append(entry)

            query = """
                INSERT INTO pinned_messages 
                (m_id, text, sender_id, date, changed_at) 
                VALUES %s;
            """
            execute_values(cursor, query, values)
            conn.commit()


