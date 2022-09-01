import music_tag # pip install music-tag
import os
import re
from time import time

dry_run = False
errors = []

regex_list = [
    re.compile(r"\s*[({\[]explicit[)}\]]", re.IGNORECASE),  # explicit
    re.compile(r"\s*[({\[]\s*\d*\s*re[-]*master[ed]*\s*\d*\s*[)}\]]", re.IGNORECASE),  # remastered
    re.compile(r"\s*[({\[]\s*album\s+version\s*[)}\]]", re.IGNORECASE)  # "album version"
]


path = r""

start = time()
for root,d_names,f_names in os.walk(path, topdown=False):
    # Check files
    for file in f_names:
        filepath = os.path.join(root, file)

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
        title = title.strip()
        if hits:
            ftag['title'] = title
            save_tags = True

        
        # Check Album tag
        original_album = album = ftag['album'].value
        hits = 0
        for regex in regex_list:
            album, hit = regex.subn("", album)
            hits += hit
        album = album.strip()
        if hits:
            ftag['album'] = album
            save_tags = True


        if save_tags:
            print(f"Old title: \"{original_title}\" ||| New title: \"{title}\"")
            if not dry_run:
                print(filepath)
                ftag.save()

        # Check filename
        old_filename = filename = file

        hits = 0
        for regex in regex_list:
            filename, hit = regex.subn("", filename)
            hits += hit
        filename = filename.strip()

        if hits:
            print(f"Old filename: \"{old_filename}\" ||| New filename: \"{filename}\"")
            if not dry_run:
                new_filepath = os.path.join(root, filename)
                os.rename(filepath, new_filepath)

    
    # Check directory names
    for dir in d_names:
        old_dirpath = os.path.join(root, dir)
        print(f"Directory '{old_dirpath}' recursed")
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

end = time()


print("Files that produced errors:")
for error in errors:
    print(error)

print(f"Done. took {end - start} seconds")

input('Press any key to continue')