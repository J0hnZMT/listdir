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


def md5_hash(file_to_hash):
    block_size = 65536
    hash_md5 = hashlib.md5()
    # getting the md5 hashes of files
    with open(file_to_hash, 'rb') as hash_file:
        buf = hash_file.read(block_size)
        while len(buf) > 0:
            hash_md5.update(buf)
            buf = hash_file.read(block_size)
    return hash_md5.hexdigest()


def sha1_hash(file):
    block_size = 65536
    hash_sha1 = hashlib.sha1()
    # getting the sha1 hashes of files
    with open(file, 'rb') as hash_file:
        buf = hash_file.read(block_size)
        while len(buf) > 0:
            hash_sha1.update(buf)
            buf = hash_file.read(block_size)
    return hash_sha1.hexdigest()


def csv_archive(zip_file_name, dir_path):
    # writing files to a zipfile
    os.chdir(dir_path)
    zip_name = "{}.zip".format(zip_file_name)
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as file_to_zip:
        file_to_zip.write(zip_file_name)
    # deleting the csv file
    os.remove(zip_file_name)
    print('{}.zip created...'.format(zip_file_name))


def add_date_time(csv_file):
    # add date and time to the output
    now = datetime.now()
    datetime_now = now.strftime("%m-%d-%y %I-%M-%p")
    csv_filename_now = "{} {}.csv".format(csv_file, datetime_now)
    return csv_filename_now


def list_dir(dir_name, csv_file_name):
    dir_name_path = r"{}".format(dir_name)
    file = r"{}".format(csv_file_name)
    if not os.path.exists(dir_name_path):
        print("Path not found!")
    else:
        try:
            # create a csv file
            csv_name = add_date_time(file)
            os.chdir(dir_name_path)
            with open(csv_name, "w+", newline='', encoding='utf-8') as csv_file:
                # header for the csv file
                field_header = ['Parent Name', 'File Name', 'File Size', 'MD5', 'SHA-1']
                csv_writer = csv.DictWriter(csv_file, fieldnames=field_header)
                csv_writer.writeheader()
                os.chdir(dir_name)
                # get the parent directory path, file names and file size
                for dir_path, dir_names, file_names in os.walk(dir_name):
                    full_path = os.path.abspath(dir_path)
                    for file_name in file_names:
                        file_with_path = os.path.join(dir_path, file_name)
                        file_size = os.path.getsize(file_with_path)
                        # get the hashes of the files
                        md5_file_hash = md5_hash(file_with_path)
                        sha1_file_hash = sha1_hash(file_with_path)
                        # store the data in a dictionary
                        report = {'Parent Name': full_path, 'File Name': file_name, 'File Size': file_size, 'MD5': md5_file_hash, 'SHA-1': sha1_file_hash}
                        # store the data by row in the csv file
                        csv_writer.writerow(report)
            # archive the csv output file
            csv_archive(csv_name, dir_name)
        except OSError as e:
            # catch any error and display
            print("Ops, Something went wrong! {}".format(e))


def main():
    """ Main Function of the program """
    parser = argparse.ArgumentParser()
    config = configparser.ConfigParser()
    parser.add_argument("dir", nargs='?', help="The directory you want to access", type=str)
    parser.add_argument("csv_file_name", nargs='?', help="The file name you want for the csv file", type=str)
    args = parser.parse_args()
    # when the user put empty arguments
    if args.dir is None and args.csv_file_name is None:
        path = os.path.dirname(__file__)
        config.read(path + '/setup.ini')
        # using the default arguments from setup.ini
        list_dir(config['arguments']['file path'], config['arguments']['file name'])
    else:
        list_dir(args.dir, args.csv_file_name)


if __name__ == '__main__':
    main()
