""" A program that can store Parent paths, File names and File size of the selected directory and its sub directories to
    a csv file.

    to use type in command line python listdir.py <directory path> <csv file name>
    then press enter a csv file will be saved with file name you typed

"""
import os
import argparse
import csv
import hashlib
from zipfile import ZipFile
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


def csv_archive(zip_file_name):
    # writing files to a zipfile
    os.chdir("C:\\Users\\TEU_USER\\Documents\\python-exer\\listdir")
    zip_name = "{}.zip".format(zip_file_name)
    with ZipFile(zip_name, 'w') as file_to_zip:
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
    find_path = os.path.exists(dir_name)
    if not find_path:
        print("Path not found!")
    else:
        try:
            # create a csv file
            csv_name = add_date_time(csv_file_name)
            with open(csv_name, "w+", newline='') as csv_file:
                # header for the csv file
                field_header = ['Parent Name', 'File Name', 'File Size', 'MD5', 'SHA-1']
                csv_writer = csv.DictWriter(csv_file, fieldnames=field_header)
                csv_writer.writeheader()
                os.chdir(dir_name)
                # get the parent directory path, file names and file size
                for dir_path, dir_names, file_names in os.walk(dir_name):
                    for file_name in file_names:
                        os.chdir(dir_path)
                        file_size = os.path.getsize(os.path.join(dir_path, file_name))
                        # get the hashes of the files
                        md5_file_hash = md5_hash(file_name)
                        sha1_file_hash = sha1_hash(file_name)
                        # store the data in a dictionary
                        report = {'Parent Name': str(dir_path), 'File Name': file_name, 'File Size': file_size, 'MD5': md5_file_hash, 'SHA-1': sha1_file_hash}
                        # store the data by row in the csv file
                        csv_writer.writerow(report)
            # archive the csv output file
            csv_archive(csv_name)
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
        config.read('setup.ini')
        # using the default arguments from setup.ini
        list_dir(config['arguments']['file path'], config['arguments']['file name'])
    else:
        list_dir(args.dir, args.csv_file_name)


if __name__ == '__main__':
    main()
