import listdir
from datetime import datetime
import os

test_file = "testfile"
test_empty_file = "empty.txt"
test_relative_path = "."
test_absolute_path = os.path.abspath("..")
test_given_path = "C:\\Users"
wrong_path = "C:\\Doc"
md5_empty = "d41d8cd98f00b204e9800998ecf8427e"
sha1_empty = "da39a3ee5e6b4b0d3255bfef95601890afd80709"


def test_add_date_time():
    datetime_now = datetime.now().strftime("%m-%d-%y %I-%M-%p")
    assert listdir.add_date_time(test_file) == "{} {}.csv".format(test_file, datetime_now)


def test_path_finder():
    assert listdir.path_finder(test_relative_path) is True
    assert listdir.path_finder(test_absolute_path) is True
    assert listdir.path_finder(test_given_path) is True


def test_md5_hash():
    assert listdir.md5_hash(test_empty_file) == md5_empty


def test_sha1_hash():
    assert listdir.sha1_hash(test_empty_file) == sha1_empty


def test_csv_archive():
    assert listdir.csv_archive(test_empty_file, test_relative_path) == "{}.zip".format(test_empty_file)


def test_list_dir():
    with pytest.raises(OSError) as exc_info:
        listdir.list_dir(wrong_path, test_file)

    exception_raised = exc_info.value
    assert e.message == "Ops, Something went wrong! {}".format(OSError)