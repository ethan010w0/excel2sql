import sys
import getopt
import argparse
import os


def parse_args(args):
    if not args:
        print 'No excel file path'
        sys.exit()
    return args[0]


def parse_opts(opts):
    db = str()
    schema = str()
    for o, a in opts:
        if o in ("-h", "--help"):
            help()
            sys.exit()
        elif o in ("-d", "--db"):
            db = a
        elif o in ("-s", "--schema"):
            schema = a
        elif o == "--hib":
            print a
        else:
            assert False, "unhandled option"
    return db, schema


def parse_schema(excel):
    return os.path.splitext(excel)[0]


def help():
    parser = argparse.ArgumentParser(
        description='Export excel to sql script for creating database schema.')
    parser.add_argument('excel', help='excel file path')
    parser.add_argument('-d', '--db', action='store_true',
                        help='database type')
    parser.add_argument('-s', '--schema', action='store_true',
                        help='database schema name')
    parser.add_argument('--hib', action='store_true',
                        help='export to hibernate entity')
    args = parser.parse_args()
    print args.accumulate(args.integers)


def main():
    options = "hd:s:"
    long_options = ["help", "db=", "schema=", "hib="]
    try:
        opts, args = getopt.getopt(sys.argv[1:], options, long_options)
    except getopt.GetoptError as err:
        help()
        sys.exit()

    excel = parse_args(args)
    db, schema = parse_opts(opts)

    if not db:
        db = 'mysql'
    if not schema:
        schema = parse_schema(excel) 

    print excel, db, schema


if __name__ == "__main__":
    main()
