# SPDX-License-Identifier: MIT

import argparse
import hashlib
import os

from pathlib import Path


parser = argparse.ArgumentParser(description="ddif")

parser.add_argument("path1", help="Path 1", type=str)
parser.add_argument("path2", help="Path 2", type=str)
parser.add_argument("pattern", help="File Pattern", nargs="?", default="*.txt", type=str)
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("-s", "--swap", help="Swap path1 and path2", action="store_true")
parser.add_argument("-f", "--hash", help="Use file hash instead of name", action="store_true")
parser.add_argument("-a", "--algorithm", help="File hash algorithm", choices=list(hashlib.algorithms_guaranteed), default="md5")
parser.add_argument("-m", "--match", help="Find files in path1 that exist in path2", action="store_true")
parser.add_argument("-r", "--recursive", help="Include files of sub directories", action="store_true")

args = parser.parse_args()

p1 = os.path.abspath(args.path1)
p2 = os.path.abspath(args.path2)
file_pattern = args.pattern
verbose = args.verbose
swap_path = args.swap
compare_hashes = args.hash
hash_algo = args.algorithm
match_file = args.match
recursive_search = args.recursive

if swap_path:
    p1, p2 = p2, p1

if not os.path.exists(p1):
    print(f"Error {p1} does not exist")
    exit()
if not os.path.isdir(p1):
    print(f"Error {p1} is not a directory")
if not os.path.exists(p2):
    print(f"Error {p2} does not exist")
    exit()
if not os.path.isdir(p2):
    print(f"Error {p2} is not a directory")

if recursive_search:
    file_list1 = list(Path(p1).rglob(file_pattern))
    file_list2 = list(Path(p2).rglob(file_pattern))
else:
    file_list1 = list(Path(p1).glob(file_pattern))
    file_list2 = list(Path(p2).glob(file_pattern))

if compare_hashes:
    # TODO: this fails if user does not have permissions to open and read the file
    # TODO: Add to tests a dir with different perms
    # TODO: Skip files without perms. and, if verbose, print that the file was inaccessable due to perms
    hash_to_files1 = {hashlib.file_digest(open(f, "rb"), hash_algo).hexdigest():f for f in file_list1}
    hash_to_files2 = {hashlib.file_digest(open(f, "rb"), hash_algo).hexdigest():f for f in file_list2}

    hash_set1 = set(k for k,_ in hash_to_files1.items())
    hash_set2 = set(k for k,_ in hash_to_files2.items())

    if match_file:
        ret_hashs = hash_set1 & hash_set2
    else:
        ret_hashs = hash_set1 - hash_set2

    if len(ret_hashs) == 0:
        print(f"No files in {p1} found in {p2}" if match_file else f"All files in {p1} are in {p2}")
    else:
        print(f"{len(ret_hashs)} file(s) in {p1} in {p2}" if match_file else f"{len(ret_hashs)} file(s) in {p1} not in {p2}")
        if verbose:
            for h,f in hash_to_files1.items():
                if match_file:
                    print(f"{h}    {f}    ->    {hash_to_files2[h]}" if (h in ret_hashs) else f"{h}    {f}")
                else:
                    print(f"{h}    {f}")
        else:
            for h in ret_hashs:
                print(f"{h}    {hash_to_files1[h]}    {hash_to_files2[h]}" if match_file else f"{h}    {hash_to_files1[h]}")

else: # compare file names
    name_to_paths1 = {f.name:f for f in file_list1}
    name_to_paths2 = {f.name:f for f in file_list2}

    names1 = set(f.name for f in file_list1)
    names2 = set(f.name for f in file_list2)

    if match_file:
        ret_names = names1 & names2
    else:
        ret_names = names1 - names2

    if len(ret_names) == 0:
        print(f"No files in {p1} found in {p2}" if match_file else f"All files in {p1} are in {p2}")
    else:
        print(f"{len(ret_names)} file(s) in {p1} in {p2}" if match_file else f"{len(ret_names)} file(s) in {p1} not in {p2}")
        if verbose:
            for n,f in name_to_paths1.items():
                if match_file:
                    print(f"{n}    {f}    ->    {name_to_paths2[n]}" if (n in ret_names) else f"{n}    {f}")
                else:
                    print(f"{n}    {f}")
        else:
            for n in ret_names:
                print(f"{n}    {name_to_paths1[n]}    {name_to_paths2[n]}" if match_file else f"{n}    {name_to_paths1[n]}")


