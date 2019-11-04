import listdir
from datetime import datetime
import os
import pytest

test_file = "testfile"
test_empty_file = "empty.txt"
test_zip_file = "sample.test"
test_relative_path = "."
test_absolute_path = os.path.abspath("..")
test_given_path = "C:\\Users"
md5_empty = "8274425de767b30b2fff1124ab54abb5"
sha1_empty = "2201589aa3ed709b3665e4ff979e10c6ad5137fc"


def test_add_date_time():
    datetime_now = datetime.now().strftime("%m-%d-%y %I-%M-%p")
    assert listdir.add_date_time(test_file) == "{} {}.csv".format(test_file, datetime_now)
    assert listdir.csv_archive(test_empty_file, test_relative_path) == "{}.zip".format(test_zip_file)


def test_path_finder():
    assert listdir.path_finder(test_relative_path) is True
    assert listdir.path_finder(test_absolute_path) is True
    assert listdir.path_finder(test_given_path) is True


def test_md5_hash():
    assert listdir.md5_hash(test_empty_file) == md5_empty


def test_sha1_hash():
    assert listdir.sha1_hash(test_empty_file) == sha1_empty


def test_csv_archive():
    assert listdir.csv_archive(test_empty_file, test_relative_path) == "{}.zip".format(test_zip_file)


if __name__ == '__main__':
    pytest.main()
