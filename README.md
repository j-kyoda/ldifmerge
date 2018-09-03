ldifmerge
==========

Merge ldif files

Required
--------

* python3.6.x

How to use
----------

* This program do merge ldif file and dump it stdout.

	ldifmerge.py LDIF_FILE1 LDIF_FILE2

example operation
-----------------

	$ python ldifmerge.py contacts.ldif from_thunderbird.ldif > merged.ldif
	$ ldapadd -x -D uid=account,ou=People,dc=example,dc=com -W -f merged.ldif
