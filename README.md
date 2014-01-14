NAME
====
`imapdu` - prints a per folder summary of disk usage on an IMAP server.

SYNOPSIS
========
`imapdu [options] server`

OPTIONS
=======
`-h, --help`   show help message and exit  
`--tls`        Use a secure connection (SSL)  
`--port PORT`  Port to connect to (default: 143 or 993)  
`--user USER`  IMAP username  
`--csv`        Produce CSV output
`--human-readable`  Print sizes in human readable format
`--no-human-readable`

INSTALLATION
============

Unix/Linux:

    sudo python setup.py install


Unix/Linux (single user):

    python setup.py install --user --install-scripts ~/bin


Other:

    python setup.py install

