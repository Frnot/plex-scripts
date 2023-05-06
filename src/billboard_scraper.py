import datetime
import shelve
from time import perf_counter as time

import billboard


def group_by_artist(tracks) -> dict:
    track_dict = {}
    for track, artist in tracks:
        if artist in track_dict:
            track_dict[artist].append(track)
        else:
            track_dict[artist] = [track]

    return track_dict


def top_40_no_country() -> list[tuple]:
    ignored_artists = [
        "Morgan Wallen",
        "Luke Combs",
    ]
    trim_phrases =[
        "Featuring",
        ",",
        "&",
        "With",
    ]

    chart = iter(billboard.ChartData("hot-100").entries)

    chart_entries = []
    while len(chart_entries) < 40:
        entry = next(chart)
        artist = entry.artist
        for ignored in ignored_artists:
            if ignored in artist:
                break
        else:
            for phrase in trim_phrases: # Normalize to first artist listed
                artist = artist.split(phrase)[0]
            artist = artist.strip()
            chart_entries.append((entry.title, artist))

    return chart_entries



def pop_airplay_2k():
    filename = "billboard_top40"
    chart_name = "pop-songs"
    stop = datetime.date(2000, 1, 1)
    date = datetime.date.today()

    tracks = set()

    with shelve.open(filename) as db:
        try:
            date = db["date"]
            tracks = db["tracks"]
        except KeyError:
            pass

    while date >= stop:
        start_time = time()

        date_string = date.strftime("%Y-%m-%d")
        print(f"\nGetting date {date_string}")

        chart = billboard.ChartData(chart_name, date=date_string)

        new_entries = [(e.title, e.artist) for e in chart.entries if (e.title, e.artist) not in tracks]
        tracks.update(new_entries)

        for entry in new_entries:
            print(entry)
        print(f"total length: {len(tracks)}", end="")

        with shelve.open(filename) as db:
            db["date"] = date
            db["tracks"] = tracks
        
        end_time = time()
        print(f" | {end_time - start_time}")
        date -= datetime.timedelta(days=7)


if __name__ == "__main__":
    top_40_no_country()