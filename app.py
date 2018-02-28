#!/usr/bin/env python3

import argparse
from flask import Flask, json, redirect
from urllib.parse import quote

app = Flask(__name__)

index_template = """<html>
<head><title>Index of /</title></head>
<body bgcolor="white">
<h1>Index of /</h1><hr><pre><a href="../">../</a>
{body}
</pre><hr></body>
</html>"""


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def get_redirect(path):
    # For some reason rclone prepends './' for some files but not for others, just remove it in these cases.
    if path.startswith('./'):
        path = path[2:]

    # path is directory with trailing / missing
    if path and path in file_map:
        return redirect(path + '/', code=301)

    directory, _, filename = path.rpartition('/')

    # invalid directory
    if directory not in file_map:
        return '', 404

    if filename:
        if filename in file_map[directory]:
            return redirect(file_map[directory][filename]['url'], code=301)
        else:
            return '', 404
    else:
        # Get filenames in current directory and remove their path
        files_filtered = [f['filename'].rpartition('/')[2] for f in file_map[directory].values()]

        # God this is hacky.
        links = []
        for subdirectory in file_map.keys():
            # ignore root and current directory
            if not subdirectory or subdirectory == directory:
                continue
            # if we're not in root, append / to directory
            if directory and not directory.endswith('/'):
                directory += '/'
            # If the directory starts with the current directory list it in there
            if subdirectory.startswith(directory):
                # remove current directory and deeper directories from name
                subdirectory = subdirectory[len(directory):]
                subdir_link = subdirectory.split('/', 1)[0]
                link_html = '<a href="{}/">{}/</a> 01-Jan-1970 00:00 -'.format(subdir_link, subdir_link)
                if link_html not in links:
                    links.append(link_html)

        # date/size are ignored by rclone, it just looks for links.
        # The filename in the listing is for human readability only.
        links.extend(['<a href="{}">{}</a> 01-Jan-1970 00:00 1024'
                     .format(quote(f), f) for f in files_filtered])

        links_html = '\n'.join(links)
        return index_template.format(body=links_html)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', '--file', default='files.json',
                           help='Input file with JSON list of files to include '
                                'in fake index. (Default: files.json)')
    argparser.add_argument('-i', '--host', default='127.0.0.1',
                           help='Host to listen to, e.g. if rclone is '
                                'run on a different machine (default: 127.0.0.1)')
    argparser.add_argument('-p', '--port', default=8000, type=int,
                           help='Port to listen on (default: 8000)')
    argparser.add_argument('-k', '--keep-path', action='store_true',
                           help='Keep path in filename if only url is supplied (default: false)')
    argparser.add_argument('-l', '--limit', type=int,
                           help='Maximum number of items to show in index (for testing)')
    argparser.add_argument('-o', '--offset', type=int,
                           help='Offset for items to show in index (for testing)')
    args = argparser.parse_args()

    files = json.load(open(args.file))
    file_map = {}

    if args.offset:
        files = files[args.offset:]
    if args.limit:
        files = files[:args.limit]

    # Create lookup table for redirector
    for file in files:
        if 'url' not in file:
            continue

        # If no filename is given create one from URL, optionally keep path
        if 'filename' not in file:
            if file.get('keep_path', False) or args.keep_path:
                file['filename'] = file['url'].split('/', 3)[3].split('?')[0]
            else:
                file['filename'] = file['url'].split('/')[-1].split('?')[0]

        # if directory is given also make sure filename does not include /
        if 'directory' in file:
            file['filename'] = file['filename'].replace('/', '_')
            directory = file['directory'].strip('/')
        # if only filename is present get directory from there.
        else:
            directory, _, filename = file['filename'].rpartition('/')
            file['filename'] = filename

        # Make sure the directory of the current file an all directories in its path exist in the map
        if directory not in file_map:
            dirs = directory.split('/')
            for i in range(len(dirs) + 1):
                sub_dir = '/'.join(dirs[0:i])
                if sub_dir not in file_map:
                    file_map[sub_dir] = dict()

        file_map[directory][file['filename']] = file

    app.run(host=args.host, port=args.port)
