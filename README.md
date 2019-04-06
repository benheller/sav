# รคש

Tested on python v3.6.4

## Setup
```
git clone git@github.com:benheller/sav.git
cd sav && pip install -r requirements.txt
```

## Help
```
python sav.py -h
usage: sav.py [-h] -k API_KEY [-u USER] [-c] [--debug] topic

positional arguments:
  topic

optional arguments:
  -h, --help            show this help message and exit
  -k API_KEY, --api-key API_KEY
  -u USER, --user USER
  -c, --chaos
  --debug
```

## Usage
```
python sav.py -k foo -u sav 123
````