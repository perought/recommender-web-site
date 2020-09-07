import csv

from django.core.management.base import BaseCommand

import pandas as pd


class Command(BaseCommand):
    help = 'Create sql scripts'

    def handle(self, *args, **options):
        datasets = [
            ["books_dataset", "bookdatabase"],
            ["books_ratings", "bookratings"],
            ["movies_dataset_ascii", "moviedatabase"],
            ["movies_ratings", "movieratings"]
        ]
        for dataset in datasets:
            with open('rcsystem/static/' + dataset[0] + '.csv', 'r') as f:
                csv_file = csv.reader(f)
                header = next(csv_file)
                headers = map((lambda x: '`' + x + '`'), header)
                insert = 'INSERT INTO rcsystem_' + dataset[1] + '(' + ", ".join(headers) + ") VALUES "
                sql = []
                for row in csv_file:
                    values = map((lambda x: '"' + x + '"'), row)
                    content = insert + "(" + ", ".join(values) + ");"
                    sql.append(content)

            with open(dataset[0] + '.sql', 'w') as f:
                for item in sql:
                    f.write("%s\n" % item)
