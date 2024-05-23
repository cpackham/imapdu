#!/usr/bin/env python
#
# imapdu - Disk usage for IMAP
# Copyright (C) 2014 Chris Packham
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Disk usage calculator for IMAP accounts
"""
import argparse
import imaplib
import getpass
import re


def folders(client):
    """return a list of IMAP folders"""
    status, result = client.list()
    if status != "OK":
        return []
    else:
        return [x.split(' "/" ')[1] for x in result]


def folder_size(client, folder):
    """
    return the number, size and maximum of all the
    messages in an IMAP folder
    """
    status, result = client.select(folder, readonly=True)
    if status != "OK":
        return None

    nmsg = int(result[0])
    if nmsg > 0:
        status, result = client.search(None, 'ALL')
        if status != "OK":
            return None

        msg_ids = [int(i) for i in result[0].split()]
        msg_ids.sort()
        message_set = "%d:%d" % (msg_ids[0], msg_ids[-1])

        status, result = client.fetch(message_set, "(RFC822.SIZE)")
        if status != "OK":
            return None

        exp = re.compile(r'\d+ \(RFC822.SIZE (\d+)\)')
        sizes = [int(exp.search(x).group(1)) for x in result]

        return nmsg, sum(sizes), max(sizes)


def to_size(num):
    """format a number as a size in bytes"""
    for x in ['B', 'K', 'M', 'G']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'T')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tls', action='store_true', default=False,
                        help='Use a secure connection (SSL)')
    parser.add_argument('--port', type=int,
                        help='Port to connect to (default: 143 or 993)')
    parser.add_argument('--user', type=str, default=getpass.getuser(),
                        help='IMAP username (default: %(default)s)')
    parser.add_argument('--csv', action='store_true', default=False,
                        help='Produce CSV output')
    parser.add_argument('--human-readable', action='store_true', default=True,
                        help='Print sizes in human readable format')
    parser.add_argument('--no-human-readable', action='store_false',
                        dest='human_readable')
    parser.add_argument('server', type=str,
                        help='IMAP server')
    args = parser.parse_args()

    port = 993 if args.tls else 143
    if args.port:
        port = args.port

    password = getpass.getpass()

    if args.tls:
        client = imaplib.IMAP4_SSL(args.server, port)
    else:
        client = imaplib.IMAP4(args.server, port)

    report_human = "{count} Messages in {folder} taking up {size} biggest message {biggest}"
    report_csv = "{count},{folder},{size},{biggest}"
    report = report_csv if args.csv else report_human

    client.login(args.user, password)
    for folder in folders(client):
        ret = folder_size(client, folder)
        if ret is None:
            continue
        nmsg, size, max_ = ret
        if args.human_readable:
            size = to_size(size)
            max_ = to_size(max_)
        print(report.format(count=nmsg, folder=folder, size=size, biggest=max_))

    client.close()
    client.logout()


if __name__ == "__main__":
    main()
