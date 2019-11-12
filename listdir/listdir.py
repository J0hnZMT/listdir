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
import json
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import getpass
from configparser import ConfigParser
import pika


# setup the logger
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
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=default_level)
    else:
        logging.basicConfig(level=default_level, filename='logs.log',
                            format="%(asctime)s:%(name)s:%(levelname)s:%(message)s")
        print('Failed to load configuration file. Using default configs')


""" start the logging function """
path = "logging.yaml"
level = logging.INFO
env = 'LOG_CFG'
setup_logging(path, level, env)
logger = logging.getLogger(__name__)
logger.info("logger set..")


# access the config file
def config_open(filename, section):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


config_file = 'setup.ini'
section = 'database'


# database
def db_check(dir_name, db_pw):
    conn = None
    try:
        global config_file, section
        params = config_open(config_file, section)
        conn = psycopg2.connect(**params, password=db_pw)
        conn.autocommit = True
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        # checking if database exist
        cur.execute("select exists(SELECT datname FROM pg_catalog.pg_database WHERE datname = 'listdirdb');")
        if cur.fetchone()[0]:
            logger.info("Database exist... continue with data insertion.")
            # looking if table exist
            table_check(dir_name, db_pw)
        else:
            logger.info("Creating Database listdirdb....")
            database = """CREATE DATABASE listdirdb;"""
            cur.execute(database)
            cur.close()
            conn.close()
            table_check(dir_name, db_pw)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.exception(error)
    finally:
        if conn is not None:
            conn.close()


def db_insert(dir_name, db_pw):
    conn = None
    try:
        global config_file, section
        params = config_open(config_file, section)
        conn = psycopg2.connect(**params,
                                password=db_pw,
                                database='listdirdb')
        conn.autocommit = True
        cur = conn.cursor()
        insert_query = """INSERT INTO result(parent_name, file_name, file_size, md5, sha1) VALUES (%s, %s, %s, %s, %s);"""
        for dir_path, dir_names, file_names in os.walk(dir_name):
            for file_name in file_names:
                file_with_path = "{}{}{}".format(dir_path, os.sep, file_name)
                file_size = os.path.getsize(file_with_path)
                # get the hashes of the files
                md5_file_hash = md5_hash(file_with_path)
                sha1_file_hash = sha1_hash(file_with_path)
                # store the data in a dictionary
                report = (os.path.abspath(dir_path), file_name, file_size, md5_file_hash, sha1_file_hash)
                cur.execute(insert_query, report)
        cur.close()
        conn.close()
        logger.info("Data inserted successfully.")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.exception(error)
    finally:
        if conn is not None:
            conn.close()


def table_check(dir_name, db_pw):
    conn = None
    try:
        global config_file, section
        params = config_open(config_file, section)
        conn = psycopg2.connect(**params,
                                password=db_pw,
                                database='listdirdb')
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT to_regclass('result');")
        if cur.fetchone()[0]:
            logger.info("Table exist... continue with data insertion.")
            cur.close()
            db_insert(dir_name, db_pw)
        else:
            logger.info("Creating table result....")
            table = """CREATE TABLE result(
                    id SERIAL NOT NULL PRIMARY KEY,
                    parent_name varchar NOT NULL,
                    file_name varchar NOT NULL,
                    file_size integer NOT NULL,
                    md5 varchar(32) NOT NULL,
                    sha1 varchar(40) NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW())"""
            cur.execute(table)
            cur.close()
            conn.close()
            db_insert(dir_name, db_pw)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.exception(error)
    finally:
        if conn is not None:
            conn.close()


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


# archive
def archive_file(zip_file_name, dir_path):
    # writing files to a zipfile
    zip_name = "{}.zip".format(zip_file_name)
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as file_to_zip:
        file_to_zip.write(zip_file_name)
    # deleting the csv file
    os.remove(zip_file_name)
    logger.info("{} created...".format(zip_name))
    return zip_name


def path_finder(dir_name):
    check = os.path.exists(dir_name)
    return check


# csv
def csv_add_date_time(csv_file):
    # add date and time to the output
    now = datetime.now()
    datetime_now = now.strftime("%m-%d-%y-%I-%M-%p")
    csv_filename_now = "{}-{}.csv".format(csv_file, datetime_now)
    return csv_filename_now


def csv_creator(dir_name, csv_file_name):
    # create a csv file
    csv_name = csv_add_date_time(csv_file_name)
    logger.info("{} file created...".format(csv_name))
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
    archive_file(csv_name, dir_name)


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


# json
def json_add_date_time(json_file):
    # add date and time to the output
    now = datetime.now()
    datetime_now = now.strftime("%m-%d-%y-%I-%M-%p")
    json_filename_now = "{}-{}.json".format(json_file, datetime_now)
    return json_filename_now


def json_create(path_name, file_name):
    parent_path = os.path.expanduser(path_name)
    if not path_finder(parent_path):
        logger.warning("{} path not found!".format(parent_path))
    else:
        logger.info("path exist...")
        try:
            scanned_files = []
            reports = {'Scanned': scanned_files}
            new_json_file = json_add_date_time(file_name)
            with open(new_json_file, 'a') as f:
                logger.info("{} file created...".format(new_json_file))
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
                        scanned_files.append(report)
                json.dump(reports, f, indent=2)
            archive_file(new_json_file, parent_path)
        except OSError as e:
            # catch any error and display
            logger.error("Ops, Something went wrong! {}".format(e), exc_info=True)


# producer
def producer(dir_path):
    global config_file
    rabbit = 'rabbitmq'
    params = config_open(config_file, rabbit)
    host_name = params.get('host')
    queue_name = params.get('queue')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host_name))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    for dir_path, dir_names, file_names in os.walk(dir_path):
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
            json_result = {'data': report}
            channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(json_result))
            print(json_result)
    connection.close()


def main():
    """ Main Function of the program """
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    config = configparser.ConfigParser()
    parser.add_argument("dir", nargs='?', help="The directory you want to access", type=str)
    parser.add_argument("csv_file_name", nargs='?', help="The file name you want for the csv file", type=str)
    group.add_argument("-j", "--json", help="Output a json file instead of csv file", action="store_true")
    group.add_argument("-c", "--csv", help="Output a csv file instead of json file", action="store_true")
    group.add_argument("-d", "--database", help="Insert the data to a database instead of saving to a file",
                       action="store_true")
    group.add_argument("-s", "--send", help="Insert the data to a queue instead of saving to a file",
                       action="store_true")
    args = parser.parse_args()
    # when the user put empty arguments
    if args.dir is None and args.csv_file_name is None:
        path = os.path.dirname(__file__)
        config.read(path + '/setup.ini')
        # using the default arguments from setup.ini
        list_dir(config['arguments']['file path'], config['arguments']['file name'])
    if args.json:
        json_create(args.dir, args.csv_file_name)
    elif args.csv:
        list_dir(args.dir, args.csv_file_name)
    elif args.database:
        password = getpass.getpass('Database Password: ')
        db_check(args.dir, password)
    elif args.send:
        producer(args.dir)


if __name__ == '__main__':
    main()
