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

 - f: File name that CSV results are saved to.  This is useful to categorise tests.  i.e. Testing that occurred on a particular level on a particular day.
 - c: Comment of the single test.  Change this each time a test is run so that it can be identified.  More descriptive the better.
 - b: TCP bandwidth used in the iperf test.
 - u: UDP bandwidth used in the iperf test.
 - t: Time that each test will run for.  So, total test time will be double this (1 test for UDP and 1 for TCP)
 - n: Number of times to run tests at a location.  More tests you run, the more accurate the network's true performance can be measured.  But it takes longer.
 - p: iperf server's port.  i.e. on the iperf server you would run something like:

```
iperf3.exe -s -p 8069
```
