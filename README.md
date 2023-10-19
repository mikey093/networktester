# Network Tester

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
```
networktest.exe -b 10000 -u 10000 -h 127.0.0.1 -t 5 -p 8069 -n 1 -f levelY -c 'Next to Something'
```
## Network parameters of test:
 - h: host address of iperf server to point to.
 - p: iperf server's port.  i.e. on the iperf server you would run something like:
 - b: TCP bandwidth used in the iperf test.
 - u: UDP bandwidth used in the iperf test.
 - t: Time that each test will run for.  So, total test time will be double this (1 test for UDP and 1 for TCP)
 - n: Number of times to run tests at a location.  More tests you run, the more accurate the network's true performance can be measured.  But it takes longer.


### Output and location parameters of test:
 - f: File name that CSV results are saved to.  This is useful to categorise tests.  i.e. Testing that occurred on a particular level on a particular day.
 - c: Comment of the single test.  Change this each time a test is run so that it can be identified.  More descriptive the better.

Running the example seen above will save the results of tests into the results folder in a csv file named in the script -f paramter.
This file is appended to each time the script is run with that file name.
Similarly, log file regarding that file name is saved in the log folder.
A report can be run on the contents of this csv file with the report script outlined below.

# Report


The script for the report can be run with:

 - f: File name to run the report on.  This report will run on whatever flag was set in the networktest script following -f.  So for the example above, you could run the example below:

```
report.exe -f levelY
```

Report is saved in the results folder with .xlsx extension and can be opened in Excel.
Thresholds of each parameter can be set in the config folder, thresholds.json file.

# Server
An iperf server must be setup for the network tester to test against.  The server must be on the same VLAN of the network to be tested.  Suggest pinging the server to verify connectivity before doing a network test.  
Ensure the port in the network tester command is the same as the server's port, -p setting.

```
iperf3.exe -s -p 8069
```
Download iperf from here: https://iperf.fr/download/windows/iperf-3.1.3-win64.zip
 - Use this iperf for both server and client.
