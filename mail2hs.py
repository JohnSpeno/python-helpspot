#!/usr/bin/python

import sys
import email
import MySQLdb as db

# Set these variables with the same values you've used in your HelpSpot
# install.
cDBUSERNAME = ''
cDBPASSWORD = ''
cDBNAME = ''

by_email = """
SELECT xRequest, fOpen from HS_Request where sEmail like %s
"""

def get_hsid(sender, subject):
    """

    sender - The email address of the sender.
    subject - The subject of the mail. Not used.

    Returns either a HelpSpot request id or None.

    If there is one request found, assume that is the one to use.

    If there are more than one request found, but only one is currently
    open, then use the request id of that one.

    Otherwise, return None.


    """

    conn = db.Connection(user=cDBUSERNAME, passwd=cDBPASSWORD, db=cDBNAME)
    curs = conn.cursor()
    curs.execute(by_email, (sender,))

    rows = curs.fetchall()
    if len(rows) == 1:
        return rows[0][0]

    opened = [row[0] for row in rows if row[1] == 1]
    if len(opened) == 1:
        return opened[0]

    # we don't know which request to send this to, so give up
    return None

def main():
    msg = email.message_from_file(sys.stdin)
    sender = email.Utils.parseaddr(msg['From'])[1]
    subject = msg['Subject']
    hsid = get_hsid(sender, subject)
    if hsid:
        del msg['Subject']
        msg['Subject'] = '%s {%s}' % (subject, hsid)
    print msg
    return 0

if __name__ == '__main__':
    sys.exit(main())
