# listdir
Machine Problem 2

A program that can store Parent paths, File names and File size of the selected directory and its sub directories to a csv file.

## How to Use
-type in the command line python listdir.py <directory path> <csv file name> <command>
  
**using the -c or --csv argument**

-eg. python listdir.py C:\Users result.csv -c

**using the -j or --json argument**

-eg. python listdir.py ~\Documents result.csv -j

-then press enter, a csv file will be saved with csv file name you typed with all the data about (parent path, file name, file size) directory and sub-directories you typed on the command line.

## Optional Arguments

 -h, --help     show this help message and exit

-j, --json     Output a json file instead of csv file

-c, --csv      Output a csv file instead of json file


## How to install

pip install listdir

**To use as a module, simply do:**

import listdir

listdir.list_dir(path,filename)

**To use in terminal, simply do:**

$ listdir <path> <file name>

**in command line in windows:**

-C:\Users\user\Documents\>listdir <path> <file name>


## Author
**Johnzel Tuddao** - *Initial work* - [J0hnZMT](https://github.com/J0hnZMT)

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

