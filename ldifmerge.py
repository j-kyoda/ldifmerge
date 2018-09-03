#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Merge ldif file
"""
import argparse
import copy


class LdifMergeError(Exception):
    """Ldif Merge Error
    """
    def __init__(self, mes):
        self.mes = mes

    def __str__(self):
        return self.mes


def gen_entry_from_file(file_obj):
    """Generate entry from file

    Arguments:
        file_obj -- file object

    Returns:
        yield entry object
    """
    entry = {'objectclass': []}
    for line in file_obj:
        line = line.replace('\r', '').replace('\n', '')
        if line == '':
            if len(entry['objectclass']):
                yield entry
            entry = {'objectclass': []}
            continue
        if ': ' in line:
            (tag, val) = line.split(': ', maxsplit=1)
            if tag == 'objectclass':
                entry['objectclass'].append(val)
                continue
            entry[tag] = val
            continue
        raise LdifMergeError
    return None


def read_entries(file_obj):
    """Get entry list from file

    Arguments:
        file_obj -- file object

    Returns:
        Return entry object dictionary
    """
    entries = {}
    for entry in gen_entry_from_file(file_obj):
        dn = entry['dn']
        entries[dn] = entry
    return entries


def dump_entry(entry, ret='\n'):
    """Dump entry object

    Arguments:
        entry -- entry object
        ret   -- return code

    Returns:
        Return entry string.
    """
    lines = []
    queue = ['dn', 'objectclass']
    tags = [key for key in entry.keys()
            if key != 'dn' and key != 'objectclass']
    tags.sort()
    lines.append(': '.join(['dn', entry['dn']]))
    for oc in entry['objectclass']:
        lines.append(': '.join(['objectclass', oc]))
    for tag in tags:
        lines.append(': '.join([tag, entry[tag]]))
    lines.append('')

    return ret.join(lines)


def dump_entries(entries, ret='\n'):
    """Dump entry objects

    Arguments:
        entries -- entry objects
        ret     -- return code

    Returns:
        Return string
    """
    dumps = []
    for (dn, entry) in entries.items():
        dump = dump_entry(entry, ret)
        dumps.append(dump)
    return ret.join(dumps)


def merged(lhs, rhs):
    """Crate merged entry list

    Arguments:
        lhs -- entries A
        rhs -- entries B

    Returns:
        Return entries C(= A + B).
    """
    work = copy.deepcopy(lhs)
    for dn in rhs.keys():
        if dn not in work:
            # append
            work[dn] = rhs[dn]
            continue
        # merge
        work_oc = work[dn].pop('objectclass')
        rhs_oc = rhs[dn].pop('objectclass')
        work[dn].update(rhs[dn])
        for oc in rhs_oc:
            if oc in work_oc:
                continue
            work_oc.append(oc)
        work[dn]['objectclass'] = work_oc

    return work


def main():
    """Main routine

    Parse arguments and call subroutine
    """
    parser = argparse.ArgumentParser(description='Merge ldif file')
    parser.add_argument('files', metavar='LDIF_FILE',
                        type=argparse.FileType(),
                        nargs=2, help='ldif file for merge')

    args = parser.parse_args()

    # read
    lhs = read_entries(args.files[0])
    rhs = read_entries(args.files[1])

    # merge
    entries = merged(lhs, rhs)

    # dump
    dump = dump_entries(entries)
    print(dump, end='')


if __name__ == '__main__':
    main()
