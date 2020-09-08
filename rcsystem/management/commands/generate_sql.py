import csv

from django.core.management.base import BaseCommand

import pandas as pd


class Command(BaseCommand):
    help = 'Create sql scripts'

    def handle(self, *args, **options):
        datasets = [
            ["books_dataset", "rcsystem_bookdatabase"],
            ["books_ratings", "rcsystem_bookratings"],
            ["movies_dataset_ascii", "rcsystem_moviedatabase"],
            ["movies_ratings", "rcsystem_movieratings"],
            ["users_script", "auth_user"]  # password: djangouser1
        ]
        for dataset in datasets:
            with open('rcsystem/static/' + dataset[0] + '.csv', 'r') as f:
                csv_file = csv.reader(f)
                header = next(csv_file)
                headers = map((lambda x: '`' + x + '`'), header)
                insert = 'INSERT INTO ' + dataset[1] + '(' + ", ".join(headers) + ") VALUES "
                sql = []
                for row in csv_file:
                    values = map((lambda x: '"' + x + '"'), row)
                    content = insert + "(" + ", ".join(values) + ");"
                    sql.append(content)

            with open(dataset[0] + '.sql', 'w') as f:
                for item in sql:
                    f.write("%s\n" % item)
