## Readme
`file_match_file.py` allows you to sort a set of files according to a given .torrent file.
The sorting will be done in a way that you can resume seeding the files in a torrent client.

Unfortunately, due to the structure of .torrent files, small files are not processed by this program and will need to be re-downloaded. Additionally, if some files are missing, the torrent client may consider that there is no beginning or end of an existing file.

## Usage
### Command line
#### Clone repository
```bash
git clone https://github.com/parshikov/file_match_finder.py.git
```

#### Install dependencies
```bash
pip install -r requirements.txt
```

#### Run
```bash
./file_match_file.py -t <torrent_file> -s <directory_with_files> -d <destination_directory>
```

### Docker

#### Build image (optionally)
```bash
docker build -f Dockerfile -t parshikov/file_match_file .
```

#### Run
```bash
# Torrent file is considered to be in the /torrents directory   
docker run -it --rm -v <directory_with_files>:/source -v <destination_directory>:/destination parshikov/file_match_file -t <torrent_file>
```

## Copyrights & License
This code is licensed under MIT

Copyright © 2023, Grigory Parshikov