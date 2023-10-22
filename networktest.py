import sys
import os
import json
import subprocess
import csv
from time import strftime
import time
from pythonping import ping
import logging


with open('config/testConfig.json', 'r') as file:
    jsonData = json.load(file)

version = open('VERSION.txt', 'r').read()

usage = '''
Usage: 
-f [File Name]* 
-h [Iperf Server IP Address]* 
-b [TCP bandwidth(kb/s)] 
-u [UDP bandwidth(kb/s)] 
-t [time of test (sec)] 
-p [Port for Iperf]
-n [No. of Tests]
-c [Comment of location]

Example:
networktest.exe -f levelX -h 127.0.0.1 -b 10000 -u 10000 -t 5 -p 8069 -n 1 -c 'at stockpile'
'''

if("-v" in sys.argv):
    print('Version: {}'.format(version))
    sys.exit(0)

if("-f" in sys.argv):
    projectFile = 'results/{}'.format(
        sys.argv[sys.argv.index("-f") + 1])
    logFile = 'log/{}.log'.format(sys.argv[sys.argv.index("-f") + 1])
else:
    print(usage)
    print("Specify output file.")
    sys.exit(0)
if("-b" in sys.argv):
    bandTCP = sys.argv[sys.argv.index("-b") + 1]
else:
    bandTCP = 10
if("-u" in sys.argv):
    bandUDP = sys.argv[sys.argv.index("-u") + 1]
else:
    bandUDP = 1
if("-h" in sys.argv):
    iperfHost = sys.argv[sys.argv.index("-h") + 1]
else:
    print(usage)
    logging.info("Specify a host of iperf server.")
    sys.exit(0)
if("-p" in sys.argv):
    iperfPort = sys.argv[sys.argv.index("-p") + 1]
else:
    iperfPort = 5021
    print("Setting iperf port to 5201")
if("-t" in sys.argv):
    iperfTime = sys.argv[sys.argv.index("-t") + 1]
else:
    print(usage)
    sys.exit(0)
if("-n" in sys.argv):
    numTests = sys.argv[sys.argv.index("-n") + 1]
else:
    print(usage)
    sys.exit(0)
if("-c" in sys.argv):
    locationComment = sys.argv[sys.argv.index("-c") + 1]
else:
    locationComment = ''

# Setup logging.
logging.basicConfig(filename=logFile, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())


# Provide test settings info for user.
testSettings = '''
Settings for test:
File Name: {},
TCP bandwidth(kb/s): {},
UDP bandwidth(kb/s): {},
Iperf Server IP Address: {},
Iperf Server port: {},
time of test (sec): {},
No. of Tests: {},
Version of networktest: {}
'''.format(projectFile, bandTCP, bandUDP, iperfHost, iperfPort, iperfTime, numTests, version)

# print(testSettings)
logging.info('Test settings at {}: {}'.format(
    time.strftime("%d/%m/%Y %X"), testSettings))


def toCSV(resultsDict):
    # Grab dictionary and put into CSV
    # print(resultsDict)
    headerOfCSV = list(resultsDict.keys())
    csvFileOut = '{}.csv'.format(projectFile)
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
        iperfHost, int(bandTCP)*1000, iperfTime, iperfPort, iperfSaveFileTCP))

    unlimited_iperfCommandUDP = ('iperf3.exe -c {} -u -J -b {} -t {} -p {} > {}'.format(
        iperfHost, int(bandUDP)*1000, iperfTime, iperfPort, iperfSaveFileUDP))

    try:
        subprocess.call(str(iperfCommandTCP), shell=True,
                        timeout=int(iperfTime) + 2)
    except subprocess.TimeoutExpired as errorMessage:
        logging.info(errorMessage)
        resultsDict = 0
        return resultsDict
    try:
        subprocess.call(str(unlimited_iperfCommandUDP),
                        shell=True, timeout=int(iperfTime) + 2)
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
        logging.info('UDP Bandwidth: {}'.format(
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
        # ws['O2'] = '{} seconds for each test.'.format(iperfTime)
        # ws['O3'] = '{} Mb/s'.format(int(bandTCP)/1000)
        # ws['O4'] = '{} Mb/s'.format(int(bandUDP)/1000)
        # ws['O5'] = '{}'.format(iperfPort)

    resultsDict = {
        'Local IP Address': localIP,
        'Server Address': iperfHost,
        'Local Port': localPort,
        'Server Port': iperfPort,
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
        'Comment': locationComment,
        'Test Seconds (s)': iperfTime,
        'Test TCP Bandwidth (Mb/s)': int(bandTCP)/1000,
        'Test UDP Bandwidth (Mb/s)': int(bandUDP)/1000,
        'Test iperf port': iperfPort
    }
    return resultsDict


x = int(numTests)
while x >= 1:
    print('---------------------------')
    print('Running the following test:')
    print('{} kb/s TCP and {} kb/s UDP to {} for {} seconds'.format(
        bandTCP, bandUDP, iperfHost, iperfTime))
    print('---------------------------')
    resultsDict = stressTest(jsonData)
    toCSV(resultsDict)
    print('---------------------------')
    logging.info('''
    To run report on these results, run the following:
                 
    report.exe -f {}
    '''.format(sys.argv[sys.argv.index("-f") + 1]))
    time.sleep(2)
    x = x - 1
