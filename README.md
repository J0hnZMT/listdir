# listdir
Machine Problem 2

A program that can store Parent paths, File names and File size of the selected directory and its sub directories to a csv file.

## How to Use
-type in the command line 
```
python listdir.py <directory path> <file name> <command>
```
**using the -c or --csv argument**

```
python listdir.py C:\Users result -c
```
**using the -j or --json argument**

```
python listdir.py ~\Documents result -j
```
**using the -d or --database argument**

No need for file name to pass in the arguments
```
python listdir.py ~\Documents -d
2019-11-04 16:32:11,841:__main__:INFO:logger set..
Database Password:
```

## Optional Arguments

 -h, --help     show this help message and exit

-j, --json     Output a json file instead of csv file

-c, --csv      Output a csv file instead of json file

-d, --database      Insert the data to a database instead of saving to a file

## How to install
```
pip install listdir
```
**To use as a module, simply do:**
```
import listdir

listdir.list_dir(path,filename)
```
**To use in terminal, simply do:**
```
$ listdir <path> <file name>
```
**in command line in windows:**
```
-C:\Users\user\Documents\>listdir <path> <file name>
```

## Author
**Johnzel Tuddao** - *Initial work* - [J0hnZMT](https://github.com/J0hnZMT)

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

