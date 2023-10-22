import sys
import os
import json
import subprocess
import csv
import time
from pythonping import ping
import logging


with open('config/testConfig.json', 'r') as file:
    defaultParams = json.load(file)

version = open('VERSION.txt', 'r').read()

usage = '''
Usage: 
-f [File Name]* 
-h [Iperf Server IP Address]* 
-b [TCP bandwidth(Mb/s)] 
-u [UDP bandwidth(Mb/s)] 
-t [time of test (sec)] 
-p [Port for Iperf]
-n [No. of Tests]
-c [Comment of location]

Example:
networktest.exe -f levelX -h 127.0.0.1 -b 10000 -u 10000 -t 5 -p 8069 -n 1 -c 'at stockpile'
'''

testParams = {}
testParams["version"] = version

if("-v" in sys.argv):
    print('Version: {}'.format(version))
    sys.exit(0)

if("-f" in sys.argv):
    testParams["projectFile"] = 'results/{}'.format(
        sys.argv[sys.argv.index("-f") + 1])
    logFile = 'log/{}.log'.format(sys.argv[sys.argv.index("-f") + 1])
else:
    print(usage)
    print("Specify output file.")
    sys.exit(0)
if("-b" in sys.argv):
    testParams["bandTCP"] = sys.argv[sys.argv.index("-b") + 1]
else:
    testParams["bandTCP"] = defaultParams["TCPbandwidth"]
if("-u" in sys.argv):
    testParams["bandUDP"] = sys.argv[sys.argv.index("-u") + 1]
else:
    testParams["bandUDP"] = defaultParams["UDPbandwidth"]
if("-h" in sys.argv):
    iperfHost = sys.argv[sys.argv.index("-h") + 1]
else:
    print(usage)
    print("Specify a host of iperf server.")
    sys.exit(0)
if("-p" in sys.argv):
    testParams["iperfPort"] = sys.argv[sys.argv.index("-p") + 1]
else:
    testParams["iperfPort"] = defaultParams["port"]
if("-t" in sys.argv):
    testParams["time"] = sys.argv[sys.argv.index("-t") + 1]
else:
    testParams["time"] = defaultParams["time"]
if("-n" in sys.argv):
    testParams["numTests"] = sys.argv[sys.argv.index("-n") + 1]
else:
    testParams["numTests"] = defaultParams["numTests"]
if("-c" in sys.argv):
    testParams["locationComment"] = sys.argv[sys.argv.index("-c") + 1]
else:
    testParams["locationComment"] = ''

print(testParams)

# Setup logging.
logging.basicConfig(filename=logFile, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())


# Provide test settings info for user.
testSettings = '''
Settings for test:
File Name: {},
TCP bandwidth(Mb/s): {},
UDP bandwidth(Mb/s): {},
Iperf Server IP Address: {},
Iperf Server port: {},
time of test (sec): {},
No. of Tests: {},
Version of networktest: {}
'''.format(testParams["projectFile"], testParams["bandTCP"], testParams["bandUDP"], iperfHost, testParams["iperfPort"], testParams["time"], testParams["numTests"], version)

logging.info('Test settings at {}: {}'.format(
    time.strftime("%d/%m/%Y %X"), testSettings))


def toCSV(resultsDict):
    # Grab dictionary and put into CSV
    # print(resultsDict)
    headerOfCSV = list(resultsDict.keys())
    csvFileOut = '{}.csv'.format(testParams["projectFile"])
    # Look for file - If it doesn't exist, write header.
    # If file not found, append results.
    # This is still not opening in Excel properly..

    if os.path.isfile(csvFileOut) == False:
        logging.info('No Header.  Adding header to {}'.format(csvFileOut))
        with open(csvFileOut, 'w', newline='') as outFile:
            writer = csv.DictWriter(
                outFile, fieldnames=headerOfCSV, dialect='excel')
            writer.writeheader()
            writer.writerow(resultsDict)
    else:
        with open(csvFileOut, 'a', newline='') as outFile:
            writer = csv.DictWriter(
                outFile, fieldnames=headerOfCSV, dialect='excel')
            writer.writerow(resultsDict)


def stressTest(jsonData, testNumber=1):
    iperfSaveFileTCP = 'results/TCP-{}.json'.format(testNumber)
    iperfSaveFileUDP = 'results/UDP-{}.json'.format(testNumber)

    iperfCommandTCP = ('iperf3.exe -c {} -J -b {} -t {} -p {} > {}'.format(
        iperfHost, int(testParams["bandTCP"])*1000000, testParams["time"], testParams["iperfPort"], iperfSaveFileTCP))

    unlimited_iperfCommandUDP = ('iperf3.exe -c {} -u -J -b {} -t {} -p {} > {}'.format(
        iperfHost, int(testParams["bandUDP"])*1000000, testParams["time"], testParams["iperfPort"], iperfSaveFileUDP))

    try:
        subprocess.call(str(iperfCommandTCP), shell=True,
                        timeout=int(testParams["time"]) + 2)
    except subprocess.TimeoutExpired as errorMessage:
        logging.info(errorMessage)
        resultsDict = 0
        return resultsDict
    try:
        subprocess.call(str(unlimited_iperfCommandUDP),
                        shell=True, timeout=int(testParams["time"]) + 2)
    except subprocess.TimeoutExpired as errorMessage:
        logging.info(errorMessage)
        resultsDict = 0
        return resultsDict

    with open(iperfSaveFileTCP, 'r') as raw:
        rawTCP = json.load(raw)
    # I am assuming that if the test doesn't run correct, we'll always get a KeyError here.
    # Will have to add extra tests so we can return better error messages.
    try:
        results = rawTCP['end']['streams'][0]['sender']
    except KeyError:
        results = {}
        logging.info('Error - Did not successfully run TCP test')
        logging.info('\nCheck iperf server is running and reachable\n')
        resultsDict = 0

    with open(iperfSaveFileUDP, 'r') as raw:
        rawUDP = json.load(raw)
    try:
        resultsUDP = rawUDP['end']['streams'][0]['udp']
    except KeyError:
        resultsUDP = {}
        logging.info('Error - Did not successfully run UDP test')
        logging.info('\nCheck iperf server is running and reachable\n')
        resultsDict = 0

    try:
        resultsCPU = rawTCP['end']['cpu_utilization_percent']
        generalResults = rawTCP['start']['connected'][0]
    except KeyError:
        logging.info('Test did not run - Cannot get CPU results')
        resultsCPU = 'NA'
        generalResults = 'NA'

    timeNow = time.strftime("%d/%m/%Y %X")
    try:
        bandwidth = round(results['bits_per_second'] * (1e-6), 2)
        timeOfTest = round(results['seconds'], 1) + \
            round(resultsUDP['seconds'], 1)
        totalBytes = results['bytes']
        hostCPU = round(resultsCPU['host_total'], 1)
        remoteCPU = round(resultsCPU['remote_total'], 1)
        localIP = generalResults['local_host']
        localPort = generalResults['local_port']
        logging.info("TCP Bandwidth = {} Mb/s".format(bandwidth))
    except KeyError:
        logging.info('Test did not run correctly.  Setting NA values.')
        bandwidth = 'NA'
        timeOfTest = 'NA'
        totalBytes = 'NA'
        hostCPU = 'NA'
        remoteCPU = 'NA'
        localIP = 'NA'
        localPort = 'NA'

    try:
        udpResults = {
            'UDP Bandwidth (Mb/s)': round(resultsUDP['bits_per_second'] * (1e-6), 2),
            'Jitter (ms)': resultsUDP['jitter_ms'],
            'Total UDP Packets': resultsUDP['packets'],
            'Lost Packets': resultsUDP['lost_packets'],
            'Lost Packets (%)': resultsUDP['lost_percent'],
            'Packets Out of Order': resultsUDP['out_of_order']
        }
        logging.info('UDP Bandwidth: {} Mb/s'.format(
            round(resultsUDP['bits_per_second'] * (1e-6), 2)))
        logging.info('Lost Packets (%): {}'.format(
            resultsUDP['lost_percent'])),
        logging.info('Jitter (ms): {}'.format(resultsUDP['jitter_ms']))
    except KeyError:
        udpResults = {
            'UDP Bandwidth (Mb/s)': 'NA',
            'Jitter (ms)': 'NA',
            'Total UDP Packets': 'NA',
            'Lost Packets': 'NA',
            'Lost Packets (%)': 'NA',
            'Packets Out of Order': 'NA'
        }

    # RTT doesn't work on my Windows PC...
    try:
        RTT_ms = results['max_rtt'] * (1e-3)
    except:
        # logging.info('RTT Error.')
        RTT_ms = 'NA'
    try:
        pingResults = ping(iperfHost, size=40, count=10)
        latencyAvg = pingResults.rtt_avg_ms
    except:
        latencyAvg = 'NA'

        # # Additional testing parameters.
        # ws['O2'] = '{} seconds for each test.'.format(testParams["time"])
        # ws['O3'] = '{} Mb/s'.format(int(testParams["bandTCP"])/1000)
        # ws['O4'] = '{} Mb/s'.format(int(testParams["bandUDP"])/1000)
        # ws['O5'] = '{}'.format(testParams["iperfPort"])

    resultsDict = {
        'Local IP Address': localIP,
        'Server Address': iperfHost,
        'Local Port': localPort,
        'Server Port': testParams["iperfPort"],
        'Time': timeNow,
        'Bandwidth (Mb/s)': bandwidth,
        'RTT (ms)': RTT_ms,
        'UDP Bandwidth (Mb/s)': udpResults['UDP Bandwidth (Mb/s)'],
        'Jitter (ms)': udpResults['Jitter (ms)'],
        'Total UDP Packets': udpResults['Total UDP Packets'],
        'Lost Packets': udpResults['Lost Packets'],
        'Lost Packets (%)': udpResults['Lost Packets (%)'],
        'Packets Out of Order': udpResults['Packets Out of Order'],
        'Test Duration (sec)': timeOfTest,
        'Total Bytes': totalBytes,
        'Host CPU Utilisation (%)': hostCPU,
        'Remote CPU Utilisation (%)': remoteCPU,
        'Latency (ms)': latencyAvg,
        'Comment': testParams["locationComment"],
        'Test Seconds (s)': testParams["time"],
        'Test TCP Bandwidth (Mb/s)': int(testParams["bandTCP"]),
        'Test UDP Bandwidth (Mb/s)': int(testParams["bandUDP"]),
        'Test iperf port': testParams["iperfPort"]
    }
    return resultsDict


x = int(testParams["numTests"])
while x >= 1:
    print('---------------------------')
    print('Running the following test:')
    print('{} Mb/s TCP and {} Mb/s UDP to {}:{} for {} seconds'.format(
        int(testParams["bandTCP"])/1000, int(testParams["bandUDP"])/1000, iperfHost, testParams["iperfPort"], testParams["time"]))
    print('---------------------------')
    resultsDict = stressTest(defaultParams)
    toCSV(resultsDict)
    print('---------------------------')
    logging.info('''
    To run report on these results, run the following:
                 
    report.exe -f {}
    '''.format(sys.argv[sys.argv.index("-f") + 1]))
    time.sleep(2)
    x = x - 1
