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


def csv_archive(zip_file_name):
    # writing files to a zipfile
    os.chdir("C:\\Users\\TEU_USER\\Documents\\python-exer\\listdir")
    zip_name = '{}.zip'.format(zip_file_name)
    with ZipFile(zip_name, 'w') as file_to_zip:
        file_to_zip.write(zip_file_name)
    # deleting the csv file
    os.remove(zip_file_name)
    print('{}.zip created...'.format(zip_file_name))


def finder(dir_name, csv_file_name):
    # find the directory of the path given
    find_path = os.path.exists(dir_name)
    # if the path is not in the list of directories
    if not find_path:
        print("Path not found!")
    else:
        try:
            block_size = 65536
            hash_md5 = hashlib.md5()
            hash_sha1 = hashlib.sha1()
            # create a csv file
            with open(csv_file_name, "w+", newline='') as csv_file:
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
                        # getting the md5 and sha1 hashes of files
                        with open(file_name, 'rb') as hash_file:
                            buf = hash_file.read(block_size)
                            while len(buf) > 0:
                                hash_md5.update(buf)
                                hash_sha1.update(buf)
                                buf= hash_file.read(block_size)
                        md5_hash = hash_md5.hexdigest()
                        sha1_hash = hash_sha1.hexdigest()
                        # store the data in a dictionary
                        report = {'Parent Name': str(dir_path), 'File Name': file_name, 'File Size': file_size, 'MD5': md5_hash, 'SHA-1': sha1_hash}
                        # store the data by row in the csv file
                        csv_writer.writerow(report)
            # archive the csv output file
            csv_archive(csv_file_name)
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
        finder(config['arguments']['file path'], config['arguments']['file name'])
    else:
        finder(args.dir, args.csv_file_name)


if __name__ == '__main__':
    main()
