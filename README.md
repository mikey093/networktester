# WoC-FAT
Code used for the WoC FAT.

## Usage
```
stress.py [Options]
Options:
-f [File Name]
-b [TCP bandwidth(kb/s)]
-u [UDP bandwidth(kb/s)]
-t [time of test (sec)]
-p [Port for Iperf]
-n [No. of Tests]
-c [Comment of location]
```

Example:

With Python
```
python stress.py -f latest -b 50000 -u 50000 -h 127.0.0.1 -t 10 -p 8071 -n 1
```
With .exe
```
-b 10000 -u 10000 -h 127.0.0.1 -t 5 -p 8069 -n 1 -f levelY -c 'Next to Something
```