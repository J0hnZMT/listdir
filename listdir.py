""" A program that can store Parent paths, File names and File size of the selected directory and its sub directories to
    a csv file.

    to use type in command line python listdir.py <directory path> <csv file name>
    then press enter a csv file will be saved with file name you typed

"""
import os
import argparse
import csv


def finder(dir_name, csv_file_name):
    # find the directory of the path given
    find_path = os.path.exists(dir_name)
    # if the path is not in the list of directories
    if not find_path:
        print("Path not found!")
    else:
        try:
            # create a csv file
            with open(csv_file_name, "w+") as csv_file:
                # header for the csv file
                field_header = ['Parent Name', 'File Name', 'File Size']
                csv_writer = csv.DictWriter(csv_file, fieldnames=field_header)
                csv_writer.writeheader()
                os.chdir(dir_name)
                # get the parent directory path, file names and file size
                for dir_path, dir_names, file_names in os.walk(dir_name):
                    os.chdir(dir_path)
                    for file_name in file_names:
                        file_size = os.stat(file_name).st_size
                        # store the data in a dictionary
                        report = {'Parent Name': str(dir_path), 'File Name': file_name, 'File Size': file_size}
                        # store the data by row in the csv file
                        csv_writer.writerow(report)
        except OSError as e:
            # catch any error and display
            print("Ops, Something went wrong! {}".format(e))


def main():
    """ Main Function of the program """
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="The directory you want to access", type=str)
    parser.add_argument("csv_file_name", help="The file name you want for the csv file", type=str)
    args = parser.parse_args()
    finder(args.dir, args.csv_file_name)


if __name__ == '__main__':
    main()
