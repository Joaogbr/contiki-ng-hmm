#!/usr/bin/env python3

import os
import sys
import argparse
import csv
import numpy as np
import matplotlib.pyplot as pl
from scipy import stats
from collections import defaultdict

###########################################

# If set to true, all nodes are plotted, even those with no valid data
PLOT_ALL_NODES = True

###########################################

SELF_PATH = os.path.dirname(os.path.abspath(__file__))
SIM_PATH = SELF_PATH
LOG_FILE = 'COOJA.testlog'

COORDINATOR_ID = 1

# for charge calculations
CC2650_MHZ = 48
CC2650_RADIO_TX_CURRENT_MA          = 9.100 # at 5 dBm, from CC2650 datasheet
CC2650_RADIO_RX_CURRENT_MA          = 5.900 # from CC2650 datasheet
CC2650_RADIO_CPU_ON_CURRENT         = 0.061 * CC2650_MHZ # from CC2650 datasheet
CC2650_RADIO_CPU_SLEEP_CURRENT      = 1.335 # empirical
CC2650_RADIO_CPU_DEEP_SLEEP_CURRENT = 0.010 # empirical

TAU = 180

###########################################

# for testbed: mapping between the node ID (Contiki_NG) and device ID (testbed)
node_id_to_device_id = {}

###########################################

output_stream = []

class NeighborStats:
    def __init__(self, nbr_id):
        self.id = nbr_id
        self.rssi = []
        self.rssi_ts = []

class NodeStats:
    def __init__(self, id):
        self.id = id

        self.from_nbr = defaultdict(lambda: None)

        # intermediate metrics
        self.is_valid = False
        self.has_joined = False
        self.tsch_join_time_sec = None
        self.rpl_join_time_msec = None
        self.rpl_time_joined_msec = 0
        self.rpl_parent = None
        self.rpl_parent_lladdr = None
        self.seqnums_received_on_root = [[],[]]
        self.seqnums_sent = [[],[]]
        self.e2e_delay = []
        self.parent_packets_tx = 0
        self.parent_packets_ack = 0
        self.parent_packets_queue_dropped = 0
        self.energest_cpu_on = 0
        self.energest_cpu_sleep = 0
        self.energest_cpu_deep_sleep = 0
        self.energest_radio_tx = 0
        self.energest_radio_rx = 0
        self.energest_radio_rx_joined = 0
        self.energest_total = 0
        self.energest_total_joined = 0
        self.energest_ticks_per_second = 1
        self.energest_joined = False
        self.energest_period_seconds = 60

        # final metrics (uninitialized)
        self.pdr = 0.0
        self.rpl_parent_changes = 0
        self.par = 0.0
        self.rdc = None
        self.rdc_joined = None
        self.charge = None
        self.avg_e2e_delay = np.nan
        self.jitter = np.nan

    def add_rssi(self, sender_id, rssi, rssi_ts):
        if self.from_nbr[sender_id] is None:
            self.from_nbr[sender_id] = NeighborStats(sender_id)
        nbr = self.from_nbr[sender_id]
        nbr.rssi.append(rssi)
        nbr.rssi_ts.append(max(0, rssi_ts))

    def log_observations(self, log_dir):
        output_dir = os.path.join(log_dir, str(self.id))
        os.makedirs(output_dir, exist_ok=True)
        for nbr_id, nbr in self.from_nbr.items():
            output_file = os.path.join(output_dir, str(nbr.id)+".csv")

            if len(nbr.rssi) != len(nbr.rssi_ts):
                print(f"Warning: Mismatched data lengths for neighbor {nbr_id}")
                continue

            if os.path.isfile(output_file):
                os.remove(output_file)
            with open(output_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["sender_id", "receiver_id", "rssi", "timestamp", "delta_t", "ssv"])
                for i in range(len(nbr.rssi)):
                    if i == 0:
                        delta_t = 0
                        ssv = 0
                        prev_ssv = ssv
                    elif i == 1:
                        delta_t = nbr.rssi_ts[i] - nbr.rssi_ts[i-1]
                        ssv = (nbr.rssi[i] - nbr.rssi[i-1]) / (nbr.rssi_ts[i] - nbr.rssi_ts[i-1])
                        prev_ssv = ssv
                    else:
                        delta_t = nbr.rssi_ts[i] - nbr.rssi_ts[i-1]
                        alpha = np.exp(-delta_t/TAU)
                        ssv = (1 - alpha) * ((nbr.rssi[i] - nbr.rssi[i-1]) / delta_t) + alpha * prev_ssv
                        prev_ssv = ssv
                    writer.writerow([self.id, nbr_id, nbr.rssi[i], nbr.rssi_ts[i], delta_t, ssv])


###########################################

def extract_macaddr(s):
    if "NULL" in s:
        return None
    return s

def extract_ipaddr(s):
    if "NULL" in s:
        return None
    return s

# (NULL IP addr) -> fe80::244:44:44:44
def extract_ipaddr_pair(fields):
    s = " ".join(fields)
    fields = s.split(" -> ")
    return extract_ipaddr(fields[0]), extract_ipaddr(fields[1])

def macaddr_to_id(addr):
    return int(addr.split(".")[-1], 16)

def ipaddr_to_id(addr):
    return int(addr.split(":")[-1], 16)

###########################################
# Parse a log file

def analyze_results(filename, log_dir, is_testbed):
    nodes = {}

    in_initialization = True

    start_ts_unix = None

    sim_time_ms = None

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if is_testbed:
                fields1 = line.split(";")
                fields2 = fields1[2].split()
                fields = fields1[:2] + fields2
            else:
                fields = line.split()

            try:
                # in milliseconds
                if is_testbed:
                    ts_unix = float(fields[0])
                    if start_ts_unix is None:
                        start_ts_unix = ts_unix
                    ts_unix -= start_ts_unix
                    ts = int(float(ts_unix) * 1000)
                    node = int(fields[1][3:])
                else:
                    ts = int(fields[0]) // 1000 # convert to ms
                    node = int(fields[1])
            except:
                # failed to extract timestamp
                # Test ended at simulation time: 3600000000
                if "Test ended" in line:
                    sim_time_ms = int(fields[5]) / 1000
                continue

            if node not in nodes:
                nodes[node] = NodeStats(node)

            # 551542547 1 [DBG : Link Stats] From: c10c.0000.0000.0007 -> RSSI pos 0: -95 at timestamp pos 0: 70578
            if "-> RSSI pos 0" in line:
                rssi = float(fields[12])
                rssi_ts = int(fields[17]) * (1000 / 128) # convert to ms
                sender_id = macaddr_to_id(extract_macaddr(fields[7]))
                nodes[node].add_rssi(sender_id, rssi, rssi_ts)

            if "association done" in line:
                # has_assoc.add(node)
                #nodes[node].seqnums = set()
                if nodes[node].tsch_join_time_sec is None:
                    nodes[node].tsch_join_time_sec = ts / 1000
                nodes[node].has_joined = True
                continue

            if "leaving the network" in line:
                nodes[node].has_joined = False
                nodes[node].energest_joined = False
                continue

            # 536000 2 [INFO: TSCH Queue] update time source: (NULL LL addr) -> 0001.0001.0001.0001
            if "update time source" in line:
                nodes[node].rpl_parent_lladdr = extract_macaddr(line.split(" -> ")[1]) #tsch_time_source
                continue

            # 2799582 3 [INFO: CSMA      ] sending to 0000.0000.0000.0000, len 10, seqno 128, queue length 1, free packets %zu
            if "sending to" in line:
                continue

            # 2799582 3 [INFO: TSCH      ] send packet to 0000.0000.0000.0000 with seqno 128, queue 1, len 1
            if "send packet to" in line:
                continue

            # 30194781 3 [INFO: CSMA      ] received packet from c10c.0000.0000.0002, seqno 19, len 10
            if "received packet from" in line:
                continue

            # 30194781 3 [INFO: TSCH      ] received from c10c.0000.0000.0002 with seqno 19
            if "received from" in line:
                continue

            # 4358536 15 [INFO: RPL       ] rpl_set_preferred_parent: used to be NULL, now is fe80::c30c:0:0:1
            if "rpl_set_preferred_parent" in line:
                nodes[node].rpl_parent_changes += 1
                nodes[node].rpl_parent = extract_ipaddr(fields[12])
                if nodes[node].rpl_parent is not None:
                    output_stream.append("Node {} joined RPL DAG through parent".format(nodes[node].id) + " {}".format(nodes[node].rpl_parent) + " at {} seconds".format(ts / 1000))
                    if nodes[node].rpl_join_time_msec is None:
                        nodes[node].rpl_join_time_msec = ts
                    nodes[node].has_joined = True
                else:
                    output_stream.append("Node {} switched to NULL parent".format(nodes[node].id) + " at {} seconds".format(ts / 1000))
                    nodes[node].has_joined = False
                    nodes[node].rpl_time_joined_msec += (ts - nodes[node].rpl_join_time_msec)
                    nodes[node].rpl_join_time_msec = None
                    nodes[node].energest_joined = False
                continue

            # 377018480 76 [INFO: RPL       ] parent switch: (NULL IP addr) -> fe80::244:44:44:44
            if " parent switch: " in line:
                nodes[node].rpl_parent_changes += 1
                nodes[node].rpl_parent = extract_ipaddr_pair(fields[7:])[1]
                if nodes[node].rpl_parent is not None:
                    output_stream.append("Node {} joined RPL DAG through parent".format(nodes[node].id) + " {}".format(nodes[node].rpl_parent) + " at {} seconds".format(ts / 1000))
                    if nodes[node].rpl_join_time_msec is None:
                        nodes[node].rpl_join_time_msec = ts
                    nodes[node].has_joined = True
                else:
                    output_stream.append("Node {} switched to NULL parent".format(nodes[node].id) + " at {} seconds".format(ts / 1000))
                    nodes[node].has_joined = False
                    nodes[node].rpl_time_joined_msec += (ts - nodes[node].rpl_join_time_msec)
                    nodes[node].rpl_join_time_msec = None
                    nodes[node].energest_joined = False
                continue

            # 4363361 15 [INFO: RPL       ] new parent lladdr -> c10c.0000.0000.0001
            if "new parent lladdr" in line:
                nodes[node].rpl_parent_lladdr = extract_macaddr(line.split(" -> ")[1])
                continue

            # 4753976 19 [INFO: RPL       ] node has left the network
            # if "node has left the network" in line:
            #     output_stream.append("Node {} has left the network".format(nodes[node].id) + " at {} seconds".format(ts / 1000))
            #     nodes[node].has_joined = False
            #     nodes[node].rpl_time_joined_msec += (ts - nodes[node].rpl_join_time_msec)
            #     nodes[node].rpl_join_time_msec = None
            #     nodes[node].energest_joined = False
            #     continue

            # 120904000 4 [INFO: App       ] app generate packet seqnum=1
            if "app generate packet" in line:
                seqnum = int(fields[8].split("=")[1])
                if is_testbed:
                    node_id = int(fields[9].split("=")[1])
                    node_id_to_device_id[node_id] = node
                if seqnum in nodes[node].seqnums_sent[0]:
                    # Could be a duplicate!
                    output_stream.append("WARNING: Application message with seqnum = {}".format(seqnum) + " already sent. Might be duplicate")
                    #if seqnum not in nodes[node].seqnums_received_on_root[0]: # This is not failproof, maybe never update ts at all?
                        #ind_s = nodes[node].seqnums_sent[0].index(seqnum)
                        #nodes[node].seqnums_sent[1][ind_s] = ts
                else:
                    nodes[node].seqnums_sent[0].append(seqnum)
                    nodes[node].seqnums_sent[1].append(ts)
                continue

            # 123047424 1 [INFO: App       ] app receive packet seqnum=1 from=fd00::208:8:8:8
            if "app receive packet" in line:
                seqnum = int(fields[8].split("=")[1])
                fromaddr = fields[9].split("=")[1]
                from_node = ipaddr_to_id(fromaddr)
                if is_testbed:
                    from_node = node_id_to_device_id.get(from_node, 0)
                if from_node not in nodes:
                    nodes[from_node] = NodeStats(from_node)
                if seqnum in nodes[from_node].seqnums_received_on_root[0]:
                    # Duplicates should be dropped by link layer, so this condition should never be met
                    output_stream.append("WARNING: Application message with seqnum = {}".format(seqnum) + " already received. Must be duplicate")
                    #ind_r = nodes[from_node].seqnums_received_on_root[0].index(seqnum)
                    #nodes[from_node].seqnums_received_on_root[1][ind_r] = ts
                else:
                    try:
                        ind_s = nodes[from_node].seqnums_sent[0].index(seqnum)
                        nodes[from_node].seqnums_received_on_root[0].append(seqnum)
                        nodes[from_node].seqnums_received_on_root[1].append(ts)
                        ind_r = len(nodes[from_node].seqnums_received_on_root[0]) - 1
                        nodes[from_node].e2e_delay.append(nodes[from_node].seqnums_received_on_root[1][ind_r] - nodes[from_node].seqnums_sent[1][ind_s])
                    except:
                        output_stream.append("WARNING: Received seqnum = {}".format(seqnum) + " not in sent index")
                        continue
                continue

            # 600142000 28 [INFO: Link Stats] num packets: tx=0 ack=0 rx=0 queue_drops=0 to=0014.0014.0014.0014
            if "num packets" in line:
                tx = int(fields[7].split("=")[1])
                ack = int(fields[8].split("=")[1])
                rx = int(fields[9].split("=")[1])
                queue_drops = int(fields[10].split("=")[1])
                to_addr = fields[11].split("=")[1]
                # only account for the (current) parent node
                if nodes[node].rpl_parent_lladdr == to_addr:
                    nodes[node].parent_packets_tx += tx
                    nodes[node].parent_packets_ack += ack
                    nodes[node].parent_packets_queue_dropped += queue_drops
                continue

            # 960073000 8 [INFO: Energest  ] Total time  :   60000000
            # 960073000 8 [INFO: Energest  ] CPU         :   60000000/  60000000 (69 permil)
            # 960073000 8 [INFO: Energest  ] LPM         :          0/  60000000 (0 permil)
            # 960073000 8 [INFO: Energest  ] Deep LPM    :          0/  60000000 (0 permil)
            # 960073000 8 [INFO: Energest  ] Radio Tx    :      49216/  60000000 (0 permil)
            # 960073000 8 [INFO: Energest  ] Radio Rx    :    2470552/  60000000 (41 permil)
            # 960073000 8 [INFO: Energest  ] Radio total :    2519768/  60000000 (41 permil)
            if "INFO: Energest" in line:
                if "Period" in line:
                    nodes[node].energest_period_seconds = int(fields[9][1:])
                elif "Total time" in line:
                    total = int(fields[8])
                    nodes[node].energest_total += total
                    nodes[node].energest_ticks_per_second = total / nodes[node].energest_period_seconds
                    if nodes[node].energest_joined:
                        nodes[node].energest_total_joined += total
                else:
                    ticks = int(fields[8][:-1])
                    if "CPU" in line:
                        nodes[node].energest_cpu_on += ticks
                    elif "Deep LPM" in line:
                        nodes[node].energest_cpu_sleep += ticks
                    elif "LPM" in line:
                        nodes[node].energest_cpu_deep_sleep += ticks
                    elif "Radio Tx" in line:
                        nodes[node].energest_radio_tx += ticks
                    elif "Radio Rx" in line:
                        nodes[node].energest_radio_rx += ticks
                        if nodes[node].energest_joined:
                            nodes[node].energest_radio_rx_joined += ticks
                        # update the state
                        nodes[node].energest_joined = nodes[node].has_joined
                    continue

    if sim_time_ms is None:
        # failed to parse sim end time
        output_stream.append("WARNING: Could not parse the total simulation time. Using last timestamp recorded instead.")
        sim_time_ms = ts

    r = []

    for k in sorted(nodes.keys()):
        n = nodes[k]
        if n.id == COORDINATOR_ID:
            continue
        if n.rpl_join_time_msec is not None:
            n.rpl_time_joined_msec += (sim_time_ms - n.rpl_join_time_msec)
        if n.is_valid or PLOT_ALL_NODES:
            d = {
                "id": n.id,
                "pdr": n.pdr,
                "par": n.par,
                "packets_sent": len(n.seqnums_sent[0]),
                "rpl_switches": n.rpl_parent_changes,
                "duty_cycle": n.rdc,
                "duty_cycle_joined": n.rdc_joined,
                "charge": n.charge,
                "time_joined": n.rpl_time_joined_msec / 1000,
                "avg_e2e_delay": n.avg_e2e_delay,
                "jitter": n.jitter
            }
            r.append(d)
            n.log_observations(log_dir)
    return r

#######################################################
# Plot the results of a given metric as a bar chart

# def plot(results, metric, ylabel):
#     pl.figure(figsize=(5, 4))

#     data = [r[metric] for r in results]
#     x = range(len(data))
#     barlist = pl.bar(x, data, width=0.4)

#     for b in barlist:
#         b.set_color("orange")
#         b.set_edgecolor("black")
#         b.set_linewidth(1)

#     ids = [r["id"] for r in results]
#     pl.xticks(x, [str(u) for u in ids], rotation=90)
#     pl.xlabel("Node ID")
#     pl.ylabel(ylabel)

#     pl.ylim(ymin=0)

#     pl.savefig(os.path.join(SIM_PATH, "plot_{}.pdf".format(metric)), format="pdf", bbox_inches='tight')
#     pl.close()

#######################################################
# Run the application

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--to-dir', default=None, dest='to_dir',
        help='Specify name of directory where the observation files will be placed')
    parser.add_argument('--fname', default=LOG_FILE, dest='fname',
        help='Specify name of log file')
    pargs = parser.parse_args()

    if pargs.to_dir is not None:
        global SIM_PATH
        SIM_PATH = os.path.join(SELF_PATH, pargs.to_dir)
    input_file = os.path.join(SIM_PATH, pargs.fname)

    if not os.access(input_file, os.R_OK):
        output_stream.append('The input file "{}" does not exist'.format(input_file))
        exit(-1)

    with open(input_file, "r") as f:
        is_testbed = "Starting COOJA logger" not in f.read()

    results = analyze_results(input_file, SIM_PATH, is_testbed)

    # plot(results, "pdr", "Packet Delivery Ratio, %")
    # plot(results, "par", "Packet Acknowledgement Ratio, %")
    # plot(results, "packets_sent", "Number of packets sent")
    # plot(results, "rpl_switches", "RPL parent switches")
    # plot(results, "duty_cycle", "Radio Duty Cycle, %")
    # plot(results, "duty_cycle_joined", "Joined Radio Duty Cycle, %")
    # plot(results, "charge", "Charge consumption, mC")
    # plot(results, "time_joined", "Total time joined to DAG, s")
    # plot(results, "avg_e2e_delay", "Average E2E delay, ms")
    # plot(results, "jitter", "E2E jitter, ms")

#######################################################

if __name__ == '__main__':
    main()
