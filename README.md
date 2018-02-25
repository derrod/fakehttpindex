# rclone HTTP fakeindex

Little project that helps copying/backing up data from HTTP sources to any kind of destination supported by rclone.

The basic idea is to fake a directory listing similar to nginx' that rclone can used as a http remote.
When a file is requested by rclone the response will be a 301 redirect to the real location of the file.

The files present in the listing will be read from a JSON file,
the destination file name can be controlled to be different from whatever is in the URL.

There is support for directories, they are either created from the filename or can be specified directly.
Filenames should not contain '/' though that will be filtered in case you are specifying a directory manually.

**Dependencies:**
* Python 3 (written in a 3.6 env, not tested with anything below)
* Flask

### Usage
Start flask app
```bash
$ python3 app.py
```
List files using rclone in some other shell
```bash
$ rclone ls http:
104857600 0.1GB.bin
104857600 100MB.bin
104857600 tester/test2/0.1GB.bin
104857600 test/0.1GB.bin
104857600 test/filename w_ slash.bin
104857600 test/test/0.1GB.bin
```

### Config format
`files.json` format
```json
[
  {
    "url": "https://speed.hetzner.de/100MB.bin"
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

`rclone.conf` entry
```
[http]
type = http
url = http://127.0.0.1:8000
```

