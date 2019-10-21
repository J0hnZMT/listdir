""" A program that can store Parent paths, File names, File size and MD5 and SHA-1 hashes of the selected directory and
    its sub directories to a csv file.

    to use type in command line python listdir.py <directory path> <csv file name>
    then press enter a csv file will be saved with file name you typed

"""
import os
import argparse
import csv
import hashlib
import zipfile
import configparser
from datetime import datetime
import yaml
import logging.config
import logging
import coloredlogs
import json


def setup_logging(default_path, default_level, env_key):
    """ Setup logging configuration """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
                coloredlogs.install()
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=default_level)
                coloredlogs.install(level=default_level)
    else:
        logging.basicConfig(level=default_level, filename='logs.log',
                            format="%(asctime)s:%(name)s:%(levelname)s:%(message)s")
        coloredlogs.install(level=default_level)
        print('Failed to load configuration file. Using default configs')


""" start the logging function """
path = "logging.yaml"
level = logging.DEBUG
env = 'LOG_CFG'
setup_logging(path, level, env)
logger = logging.getLogger(__name__)
logger.info("logger set..")


def md5_hash(file_to_hash):
    try:
        block_size = 65536
        hash_md5 = hashlib.md5()
        # getting the md5 hashes of files
        with open(file_to_hash, 'rb') as hash_file:
            buf = hash_file.read(block_size)
            while len(buf) > 0:
                hash_md5.update(buf)
                buf = hash_file.read(block_size)
        return hash_md5.hexdigest()
    except FileNotFoundError as e:
        logger.exception(e)


def sha1_hash(file):
    try:
        block_size = 65536
        hash_sha1 = hashlib.sha1()
        # getting the sha1 hashes of files
        with open(file, 'rb') as hash_file:
            buf = hash_file.read(block_size)
            while len(buf) > 0:
                hash_sha1.update(buf)
                buf = hash_file.read(block_size)
        return hash_sha1.hexdigest()
    except FileNotFoundError as e:
        logger.exception(e)


def csv_archive(zip_file_name, dir_path):
    # writing files to a zipfile
    os.chdir(dir_path)
    zip_name = "{}.zip".format(zip_file_name)
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as file_to_zip:
        file_to_zip.write(zip_file_name)
    # deleting the csv file
    os.remove(zip_file_name)
    return zip_name


def csv_add_date_time(csv_file):
    # add date and time to the output
    now = datetime.now()
    datetime_now = now.strftime("%m-%d-%y %I-%M-%p")
    csv_filename_now = "{} {}.csv".format(csv_file, datetime_now)
    return csv_filename_now


def json_add_date_time(json_file):
    # add date and time to the output
    now = datetime.now()
    datetime_now = now.strftime("%m-%d-%y %I-%M-%p")
    json_filename_now = "{} {}.json".format(json_file, datetime_now)
    return json_filename_now


def path_finder(dir_name):
    check = os.path.exists(dir_name)
    return check


def csv_creator(dir_name, csv_file_name):
    # create a csv file
    csv_name = csv_add_date_time(csv_file_name)
    logger.info("{} file created...".format(csv_name))
    os.chdir(dir_name)
    with open(csv_name, "w+", newline='', encoding='utf-8') as csv_file:
        # header for the csv file
        field_header = ['Parent Name', 'File Name', 'File Size', 'MD5', 'SHA-1']
        csv_writer = csv.DictWriter(csv_file, fieldnames=field_header)
        csv_writer.writeheader()
        # get the parent directory path, file names and file size
        for dir_path, dir_names, file_names in os.walk(dir_name):
            for file_name in file_names:
                file_with_path = "{}{}{}".format(dir_path, os.sep, file_name)
                file_size = os.path.getsize(file_with_path)
                # get the hashes of the files
                md5_file_hash = md5_hash(file_with_path)
                sha1_file_hash = sha1_hash(file_with_path)
                # store the data in a dictionary
                report = {'Parent Name': os.path.abspath(dir_path), 'File Name': file_name, 'File Size': file_size,
                           'MD5': md5_file_hash, 'SHA-1': sha1_file_hash}
                # store the data by row in the csv file
                csv_writer.writerow(report)
    # archive the csv output file
    logger.info("{} created...".format(csv_archive(csv_name, dir_name)))


def list_dir(dir_name, csv_file_name):
    parent_path = os.path.expanduser(dir_name)
    if not path_finder(parent_path):
        logger.warning("{} path not found!".format(parent_path))
    else:
        logger.info("path exist...")
        try:
            csv_creator(parent_path, csv_file_name)
        except OSError as e:
            # catch any error and display
            logger.error("Ops, Something went wrong! {}".format(e), exc_info=True)


def json_create(path_name, file_name):
    parent_path = os.path.expanduser(path_name)
    if not path_finder(parent_path):
        logger.warning("{} path not found!".format(parent_path))
    else:
        logger.info("path exist...")
        try:
            new_json_file = json_add_date_time(file_name)
            with open(new_json_file, 'a') as f:
                for dir_path, dir_names, file_names in os.walk(parent_path):
                    for file_name in file_names:
                        file_with_path = "{}{}{}".format(dir_path, os.sep, file_name)
                        file_size = os.path.getsize(file_with_path)
                        # get the hashes of the files
                        md5_file_hash = md5_hash(file_with_path)
                        sha1_file_hash = sha1_hash(file_with_path)
                        # store the data in a dictionary
                        report = {'Parent Name': os.path.realpath(dir_path), 'File Name': file_name,
                                  'File Size': file_size,
                                  'MD5': md5_file_hash, 'SHA-1': sha1_file_hash}
                        json.dump(report, f, indent=2)
            logger.info("{} created...".format(csv_archive(new_json_file, parent_path)))
        except OSError as e:
            # catch any error and display
            logger.error("Ops, Something went wrong! {}".format(e), exc_info=True)


def main():
    """ Main Function of the program """
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    config = configparser.ConfigParser()
    parser.add_argument("dir", nargs='?', help="The directory you want to access", type=str)
    parser.add_argument("csv_file_name", nargs='?', help="The file name you want for the csv file", type=str)
    group.add_argument("-j", "--json", help="Output a json file instead of csv file", action="store_true")
    args = parser.parse_args()
    # when the user put empty arguments
    if args.dir is None and args.csv_file_name is None:
        path = os.path.dirname(__file__)
        config.read(path + '/setup.ini')
        # using the default arguments from setup.ini
        list_dir(config['arguments']['file path'], config['arguments']['file name'])
    elif args.json:
        json_create(args.dir, args.csv_file_name)
    else:
        list_dir(args.dir, args.csv_file_name)


if __name__ == '__main__':
    main()
