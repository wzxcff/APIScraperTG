from psycopg2.extras import execute_values


def insert_group_info(group_info, conn):
    entry = (
        group_info["id"],
        group_info["title"],
        group_info["username"],
        group_info["about"]
    )

    print(f"INSERT GROUP ID: {entry[0]}")

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

    geo_values = []
    geo_ids = {}

    for el in batch:
        if el["sender"]["user_id"]:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO users (user_id, first_name, last_name, username, avatar, is_bot)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO NOTHING
                    RETURNING user_id;
                    """, (el["sender"]["user_id"], el["sender"]["first_name"], el["sender"]["last_name"], el["sender"]["username"], el["sender"]["avatar"], el["sender"]["is_bot"])
                )

        geo = el.get("geo")
        if geo:
            lat, lon = geo.get("latitude"), geo.get("longitude")
            if (lat, lon) not in geo_ids:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO geo_locations (latitude, longitude)
                        VALUES (%s, %s)
                        RETURNING id;
                        """, (lat, lon)
                    )
                    geo_id = cursor.fetchone()[0]
                    geo_ids[(lat, lon)] = geo_id
        else:
            geo_ids[(lat, lon)] = None

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

    print(f"GROUP ID IN MESSAGE: {group_id}")

    query = """
        INSERT INTO messages 
        (m_id, text, date, changed_at, sender_id, group_id, media, geo_id) 
        VALUES %s
        ON CONFLICT (id) DO NOTHING;
    """

    with conn.cursor() as cursor:
        execute_values(cursor, query, values)
        conn.commit()

