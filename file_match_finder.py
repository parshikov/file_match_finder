#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import hashlib
import os
import shutil
from pathlib import PurePath

from torf import Torrent


def define_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='find files from torrent in directory')
    parser.add_argument("-f", "--file", help="filename of .torrent file", type=str, required=True)
    parser.add_argument("-s", "--source", help="source directory with files", type=str, required=True)
    parser.add_argument(
        "-d",
        "--destination",
        help="destination directory to put found files into",
        type=str,
        required=True
    )
    parser.add_argument(
        "-m",
        "--mode",
        help="access mode for created folder",
        type=lambda x: int('0o' + x, 8),
        default=0o755,
        required=False,
    )
    parser.add_argument(
        "-a",
        "--action",
        help="way how to transfer found file",
        type=str,
        choices=['move', 'copy', 'link'],
        default='move',
        required=False,
    )

    return parser


def get_file_list(directory) -> list:
    """
    :param directory: directory to search files in
    :return: list of absolute paths to files in directory
    Recursive search of files in a directory
    """
    all_files = os.walk(directory)
    result = []
    for directory, _, filenames in all_files:
        for filename in filenames:
            result.append(os.path.join(directory, filename))
    return list(map(lambda x: os.path.abspath(x), result))


def get_offset_data(files) -> dict:
    """
    :param files: list of files from torrent
    :return: tuple with file and offset for each file in torrent
    """
    result = {}
    offset = 0
    for tor_file in files:
        result[tor_file] = offset
        offset += tor_file.size
    return result


def search_in_torrent_files(source: str, metadata, min_file_size):
    """
    :param source: file on disk to search in torrent
    :param metadata: list of files from torrent
    :param min_file_size: minimal size of file to search
    """
    (_, extension) = os.path.splitext(source)
    for filename in metadata:
        if os.path.getsize(source) < min_file_size:
            continue
        if filename.suffix and os.path.getsize(source) == filename.size:
            return filename
    return None


def check_hash(filename: str, offset: int, piece_size: int, hash_string: str) -> bool:
    """
    :param filename: file to check hash
    :param offset: offset in file to read chunk
    :param piece_size: size of chunk to read
    :param hash_string: hash to compare with
    """
    with open(filename, 'rb') as checking_file:
        checking_file.seek(offset)
        data = checking_file.read(piece_size)
    return hashlib.sha1(data).digest() == hash_string


def get_hash_position(offset, seek, piece_size) -> tuple:
    """
    :param offset: offset in file to calculate hash position
    :param seek: seek size in file to calculate hash position
    :param piece_size: size of chunk to read
    :return: tuple with begin of chunk and position of hash in torrent file
    """
    if seek == 0:
        chunk_number = offset // piece_size
        begin = offset
    else:
        chunk_number = offset // piece_size + 1
        begin = chunk_number * piece_size - offset
    return begin, chunk_number


args = define_argument_parser().parse_args()

if not os.path.exists(args.file):
    print(f'File not found in path {args.file}')
    exit(1)

torrent = Torrent.read(args.file)
search_dir = PurePath(args.source)
move_dir = PurePath(args.destination)
dir_mode = args.mode
transfer_mode = args.action

file_list = get_file_list(search_dir)
file_offsets = get_offset_data(torrent.files)

for file in file_list:
    found_file = search_in_torrent_files(file, torrent.files, 2 * torrent.piece_size - 1)
    if not found_file:
        continue

    file_offset = file_offsets[found_file]
    seek_bytes = file_offset % torrent.piece_size
    start_position, hash_chunk_index = get_hash_position(file_offset, seek_bytes, torrent.piece_size)

    if not check_hash(file, start_position, torrent.piece_size, torrent.hashes[hash_chunk_index]):
        continue

    os.makedirs(move_dir / found_file.parent, exist_ok=True, mode=dir_mode)
    target_filename = move_dir / found_file.joinpath()

    if transfer_mode == 'move':
        shutil.move(file, target_filename)
    elif transfer_mode == 'copy':
        shutil.copy(file, target_filename)
    elif transfer_mode == 'link':
        if not os.path.exists(target_filename):
            os.symlink(file, target_filename)
    else:
        raise ValueError('Unknown transfer mode')

print('Done')
