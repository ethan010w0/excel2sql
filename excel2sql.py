import argparse
import os
import sys


from sql_exporter.sql_exporter_factory import SQLExporterFactory


# Get the schema name from excel file name
def parse_schema(excel):
    return os.path.splitext(excel)[0]


def main():
    parser = argparse.ArgumentParser(
        description='Export excel to sql script for creating database schema.')
    parser.add_argument('excel', help='excel file path')
    parser.add_argument('-d', '--db',
                        default='mysql',
                        help='database type')
    parser.add_argument('-s', '--schema',
                        help='database schema name')
    parser.add_argument('--hib',
                        action='store_true',
                        help='export to hibernate entity')
    args = parser.parse_args()

    schema = args.schema
    if not schema:
        schema = parse_schema(args.excel)

    # Export sql script.
    try:
        s_exp_fac = SQLExporterFactory(args.db, schema)
        s_exp = s_exp_fac.create_exporter()
        s_exp.export(args.excel)
    except Exception as err:
        print(err)
        sys.exit()


if __name__ == "__main__":
    main()
