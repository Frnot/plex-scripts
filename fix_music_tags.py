import music_tag # pip install music-tag
import os

dry_run = False
phrases_to_delete = [" (Explicit)", " [Explicit]", " (Album Version)"]
errors = []

path = "V:\\media\\audio\\Music"

for root,d_names,f_names in os.walk(path):
    for file in f_names:
        #filename = root + "\\" + file
        filepath = os.path.join(root, file)

        try:
            f = music_tag.load_file(filepath)
        except KeyboardInterrupt:
            print("Exiting")
            quit()
        except:
            errors.append(filepath)
            continue

        save = False

        # artists
        artist_items = f['artist'].values

        if len(artist_items) > 1:
            new_artist_string = ", ".join(artist_items)

            print(f"New artist string: \"{new_artist_string}\"")

            if not dry_run:
                f['artist'] = new_artist_string
                save = True


        # title
        old_title = title = f['title'].value

        check_filename = False
        for phrase in phrases_to_delete:
            if phrase in title:
                title = title.replace(phrase, "")
                check_filename = True

        if title != old_title:
            print(f"Old title: \"{old_title}\" ||| New title: \"{title}\"")
            if not dry_run:
                f['title'] = title
                save = True


        # save
        if save:
            print(filepath)
            f.save()


        # filename
        if check_filename:
            old_filename = new_filename = file

            for phrase in phrases_to_delete:
                if phrase in new_filename:
                    new_filename = new_filename.replace(phrase, "")

            if new_filename != old_filename:
                print(f"Old filename: \"{old_filename}\" ||| New filename: \"{new_filename}\"")
                if not dry_run:
                    new_filepath = os.path.join(root, new_filename)
                    os.rename(filepath, new_filepath)

print("Files that produced errors:")
for error in errors:
    print(error)