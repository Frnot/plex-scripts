import music_tag # pip install music-tag
import os
import re

dry_run = False

errors = []

regex_list = [
    re.compile(r"\s*[({\[]explicit[)}\]]\s*", re.IGNORECASE),
    re.compile(r"\s*[({\[]\s*\d*\s*remaster[ed]*\s*[)}\]]\s*", re.IGNORECASE),
    re.compile(r"\s*[({\[]\s*album\s+version\s*[)}\]]\s*", re.IGNORECASE)
]


path = r"C:\Users\Frnot\Downloads\Album"

for root,d_names,f_names in os.walk(path, topdown=False):
    # Check files
    for file in f_names:
        filepath = os.path.join(root, file)
        check_filename = False

        try:
            ftag = music_tag.load_file(filepath)
            save_tags = False
        except KeyboardInterrupt:
            print("Exiting")
            quit()
        except:
            errors.append(filepath)
            continue


        # Check title / filename
        original_title = title = ftag['title'].value
        hits = 0
        for regex in regex_list:
            title, hit = regex.subn("", title)
            hits += hit
        if hits:
            ftag['title'] = title
            save_tags = True
            check_filename = True

        
        # Check Album tag
        original_album = album = ftag['album'].value
        hits = 0
        for regex in regex_list:
            album, hit = regex.subn("", album)
            hits += hit
        if hits:
            ftag['album'] = album
            save_tags = True


        if save_tags:
            print(f"Old title: \"{original_title}\" ||| New title: \"{title}\"")
            if not dry_run:
                print(filepath)
                ftag.save()

        # if track title changed, check filename
        if check_filename:
            old_filename = filename = file

            hits = 0
            for regex in regex_list:
                filename, hit = regex.subn("", filename)
                hits += hit

            if hits:
                print(f"Old filename: \"{old_filename}\" ||| New filename: \"{filename}\"")
                if not dry_run:
                    new_filepath = os.path.join(root, filename)
                    os.rename(filepath, new_filepath)

    
    # Check directory names
    for dir in d_names:
        old_dirname = dirname = dir
        
        hits = 0
        for regex in regex_list:
            dirname, hit = regex.subn("", dirname)
            hits += hit

        if hits:
            print(f"Old directory name: \"{old_dirname}\" ||| New directory name: \"{dirname}\"")
            if not dry_run:
                old_dirpath = os.path.join(root, dir)
                new_dirpath = os.path.join(root, dirname)
                os.rename(old_dirpath, new_dirpath)




print("Files that produced errors:")
for error in errors:
    print(error)

input('Press any key to continue')