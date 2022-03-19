#!/usr/bin/env python3

# Sorts playlist alphabetically first by artist name and then by track name

import sys
import sqlite3

db_path = "/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db"
conn = sqlite3.connect(db_path)
playlist_name = sys.argv[1]

cursor = conn.cursor()

tracklist = cursor.execute(f'''
select
playlist.id as id,
playlist.`order` as `order`,
track.title_sort as track,
album.title_sort as album,
artist.title_sort as artist
FROM
play_queue_generators as playlist
left outer join metadata_items as track on playlist.metadata_item_id = track.id
left outer join metadata_items as album on track.parent_id = album.id
left outer join metadata_items as artist on album.parent_id = artist.id
where playlist.playlist_id
in ( select id from metadata_items where metadata_items.metadata_type = 15 and metadata_items.title = "{playlist_name}")
order by artist.title_sort, track.title_sort
''').fetchall()

sorted = []
for index, row in enumerate(tracklist):
    l = []
    l.append(row[0])
    l.append((index + 1) * 1000)
    sorted.insert(index, l)

for row in sorted:
    playlist_id = row[0]
    order = row[1]

    cursor.execute(f'''
    UPDATE play_queue_generators SET `order` = {order} WHERE id = {playlist_id}
    ''')


conn.commit()
conn.close()
