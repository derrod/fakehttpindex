# Fake HTTP Directory Listing for rclone

Little project that helps copying/backing up data from HTTP sources to any kind of destination supported by rclone.

The basic idea is to fake a directory listing similar to nginx' that rclone can used as a http remote.
When a file is requested by rclone the response will be a 301 redirect to the real location of the file.

The directory listing will be created from the files specified in the input file, there are several options that can
be used to customize the resulting directory index. This includes the ability to use different filenames and paths
than what is present in the original URL. This is possible since rclone will use the name and path of the link
rather than what it gets redirected to.

**Dependencies:**
* Python 3 (written in a 3.6 env, not tested with anything below)
* Flask

### Usage

Command line options
```bash
$ python3 app.py -h
usage: app.py [-h] [-f FILE] [-i HOST] [-p PORT] [-k]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Input file with JSON list of files to include in fake
                        index. (Default: files.json)
  -i HOST, --host HOST  Host to listen to, e.g. if rclone is run on a
                        different machine (default: 127.0.0.1)
  -p PORT, --port PORT  Port to listen on (default: 8000)
  -k, --keep-path       Keep path in filename if only url is supplied
                        (default: false)
```

Run flask app using python
```bash
$ python3 app.py
```

In order to add it as a remote to rclone you can now use `rclone config` and create a new http remote,
alternatively you can edit your `rclone.conf` directly.

Example `rclone.conf` entry:
```
[http]
type = http
url = http://127.0.0.1:8000
```

Now you can list the files in the remote using rclone:
```bash
$ rclone ls http:
104857600 0.1GB.bin
104857600 100MB.bin
 10485760 10Mio.dat
 10485760 files/10Mio.dat
104857600 tester/test2/0.1GB.bin
104857600 test/0.1GB.bin
104857600 test/filename w_ slash.bin
104857600 test/test/0.1GB.bin
```

Note that rclone will make a HEAD request for any item in the directory,
if you have a lot of files this might take some time depending on how fast the origin server responds.

### `files.json` format
The basic format is a JSON array where each item represents a file in the listing.

Each item can have the following properties:
* `url` (required)
* `keep_path`
* `filename`
* `directory`

When only `url` is set and `keep_path` or the cli parameter `--keep-path` are not `true`/used only the last part of the
URL (i.e. everything after the final `/`) will be used as the filename and the file will be in the root.
Otherwise the path in the URL will be replicated in the fake index as well.

`filename` overrides the filename that will be used in the listing and subsequently in the rclone target,
if it contains slashes those will be used for the file's path in the listing. It should not contain any path when used
together with the `directory` property.

`directory` specifies the path to the file that should be used. Note that if the filename already contains a path
(or any `/`) it will be replaced with underscores and the result used as filename instead.

Example:
```json
[
  {
    "url": "https://speed.hetzner.de/100MB.bin"
  },
  {
    "url": "http://www.ovh.net/files/10Mio.dat"
  },
  {
    "url": "http://www.ovh.net/files/10Mio.dat",
    "keep_path": true
  },
  {
    "url": "https://speed.hetzner.de/100MB.bin",
    "filename": "0.1GB.bin"
  },
  {
    "url": "https://speed.hetzner.de/100MB.bin",
    "filename": "test/0.1GB.bin"
  },
  {
    "url": "https://speed.hetzner.de/100MB.bin",
    "filename": "test/test/0.1GB.bin"
  },
  {
    "url": "https://speed.hetzner.de/100MB.bin",
    "filename": "tester/test2/0.1GB.bin"
  },
  {
    "url": "https://speed.hetzner.de/100MB.bin",
    "filename": "filename w/ slash.bin",
    "directory": "test"
  }
]
```


