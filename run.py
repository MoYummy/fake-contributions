#!/usr/bin/env python

import argparse
import commands
import datetime
import os
import os.path
import shutil
import sys


class FakeContribute:
    def __init__(self, author, start_date, days):
        self.author = author
        self.start_date = datetime.datetime.strptime(
            start_date, '%Y-%m-%d'
        )
        self.days = days
        self.tmp_dir = '.tmp'
        self.tmp_file = os.path.join(self.tmp_dir, 'tmp.txt')
        self.one_day = datetime.timedelta(days=1)

    def run(self):
        self.restore()

        for i in range(self.days):
            self.create_commit(
                self.tmp_file,
                times=1,
                author=self.author,
                date=(self.start_date + i * self.one_day).strftime(
                    '%Y-%m-%dT%H:%M:%SZ'
                )
            )

        self.cleanup()

    def create_commit(self, path, times=1, author='bot', date=None):
        for i in range(1, times + 1):
            with open(path, 'w+') as f:
                f.write("{rand}".format(
                    rand=datetime.datetime.utcnow().microsecond
                ))
            self.commit(
                path=path,
                author=author,
                message="{i}/{times}".format(i=i, times=times),
                date=date
            )

    def restore(self):
        self.reset_to_first()
        self.commit(path=__file__, author=self.author, message=__file__)
        self.rm_rf(self.tmp_dir)
        self.mkdir(self.tmp_dir)

    def cleanup(self):
        self.rm_rf(self.tmp_dir)
        self.commit(path=self.tmp_dir, author=self.author)

    def reset_to_first(self):
        return self.getoutput("git reset {commit}".format(
            commit=self.first_commit()
        ))

    def first_commit(self):
        return self.getoutput('git rev-list --max-parents=0 HEAD')

    def rm_rf(self, path):
        if os.path.exists(path):
            shutil.rmtree(path)

    def mkdir(self, path):
        os.mkdir(path)

    def commit(self, path, author, message=None, date=None):
        if date is None:
            date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        if message is None:
            message = "{date}".format(date=date)

        self.getoutput("git add {path}".format(path=path))
        self.getoutput(
            "git commit -m '{message}' --author='{author}' --date={date}"
            .format(
                message=message,
                author=author,
                date=date
            )
        )

    def getoutput(self, cmd):
        print(cmd)
        return commands.getoutput(cmd)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a',
        '--author',
        required=True,
        help='Author: YourName <your@email.address>'
    )
    parser.add_argument(
        '-s',
        '--start',
        required=True,
        help='Start Date: 1970-01-01'
    )
    parser.add_argument(
        '-d',
        '--days',
        required=True,
        type=int,
        help='Days: 100'
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    FakeContribute(
        author=args.author,
        start_date=args.start,
        days=args.days
    ).run()
    sys.exit(0)
