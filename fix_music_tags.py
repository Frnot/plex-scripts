# v1.1

import os
import re
from time import time


test = False
dry_run = True
errors = []

regex_list = [
    re.compile(r"\s*[({\[]explicit[)}\]]", re.IGNORECASE),  # explicit
    re.compile(r"\s*[({\[]\s*\d*\s*re[-]*master[ed]*\s*\d*\s*[)}\]]", re.IGNORECASE),  # remastered
    re.compile(r"\s*[({\[]\s*album\s+version\s*[)}\]]", re.IGNORECASE)  # "album version"
]

if test:
    import music_tag

def main():
    autoinstall("music_tag")

    path = r""

    filetagcount = 0
    filenamecount = 0
    dircount = 0
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
            if title := clean(title):
                ftag['title'] = title
                save_tags = True

            # Check Album tag
            album = ftag['album'].value
            if album := clean(album):
                ftag['album'] = album
                save_tags = True

            if save_tags:
                print(f"Old title: \"{original_title}\" ||| New title: \"{title}\"")
                print(filepath)
                filetagcount += 1
                if not dry_run:
                    ftag.save()
                

            # Check filename
            old_filename = filename = file
            if filename := clean(filename):
                print(f"Old filename: \"{old_filename}\" ||| New filename: \"{filename}\"")
                filenamecount += 1
                if not dry_run:
                    new_filepath = os.path.join(root, filename)
                    os.rename(filepath, new_filepath)

        
        # Check directory names
        for dir in d_names:
            old_dirpath = os.path.join(root, dir)
            print(f"Directory '{old_dirpath}' recursed")
            old_dirname = dirname = dir
            
            if dirname := clean(dirname):
                print(f"Old directory name: \"{old_dirname}\" ||| New directory name: \"{dirname}\"")
                dircount += 1
                if not dry_run:
                    old_dirpath = os.path.join(root, dir)
                    new_dirpath = os.path.join(root, dirname)
                    os.rename(old_dirpath, new_dirpath)

    end = time()

    print("Files that produced errors:")
    for error in errors:
        print(error)

    print(f"Done. took {end - start} seconds")
    print(f"Directories renamed: {dircount}")
    print(f"Files renamed: {filenamecount}")
    print(f"Filetag edits: {filetagcount}")

    input('Press any key to continue')


def clean(string):
    hits = 0
    for regex in regex_list:
        string, hit = regex.subn("", string)
        hits += hit

    return string.strip() if hits else None


def autoinstall(package):
    import importlib
    try:
        globals()[package] = importlib.import_module(package)
    except ModuleNotFoundError as missing_pkg:
        inp = input(f"Package '{missing_pkg.name}' required. Install it now? (y/N): ")
        if "y" in inp.lower():
            import sys, subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", missing_pkg.name])
            print("\n")
            globals()[package] = importlib.import_module(package)
        else:
            quit()


def test_regex():
    from unittest import TestCase
    tc = TestCase()

    tc.assertEqual(clean("Tattoo You (2009 Re-Mastered)"), "Tattoo You")
    tc.assertEqual(clean("Test (explicit)"), "Test")
    tc.assertEqual(clean("14 - If I Should Die Before I Wake (feat. Black Rob, Ice Cube, & Beanie Sigel) [2005 Remaster].flac"), "14 - If I Should Die Before I Wake (feat. Black Rob, Ice Cube, & Beanie Sigel).flac")
    tc.assertEqual(clean("Test (2005 Remaster)"), "Test")
    tc.assertEqual(clean("Test (Remastered 2011)"), "Test")
    tc.assertEqual(clean("Test (album version) [Explicit]"), "Test")


if test:
    test_regex()
else:
    main()
