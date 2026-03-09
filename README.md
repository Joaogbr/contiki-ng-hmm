HMM-Based RPL Objective Function for Mobile IoT Networks

## Overview

This repository contains the implementation of a new RPL Objective Function for
Contiki-NG that leverages Hidden Markov Models (HMMs) to predict link quality
and select more stable parents, producing longer-lasting routes in mobile
urban IoT networks.

## Problem

In RPL-based networks, route stability can degrade significantly when nodes are mobile, particularly in dense urban environments where wireless link quality fluctuates rapidly. Traditional RPL objective functions rely on instantaneous link metrics and therefore react only after link degradation occurs.

## Repository Structure

- `os/net/routing/rpl-classic/rpl-seqhmm-of.c` – implementation of the HMM-based objective function
- `os/lib` – C implementation of the HMM generated using CRAN's seqHMM package (`viterbi.c`, `hmm.c`, `seqhmm.c`, `seqhmm-model.c`, `link-hmm-ctx.c`, `link-features-hmm.c`) 
- `examples/rpl-udp-hmm` – example application using real mobility traces

## Running the Simulation

1. Clone this repository
2. Navigate to the example directory:
   - `examples/rpl-udp-hmm`
3. Compile the firmware using `make TARGET=cooja`
4. Open the `.csc` scenario file in the Cooja simulator, or run `python3 run-cooja.py --to-dir --fname`
5. Simulation performance metrics can be visualized with `python3 run-analysis.py --to-dir --fname`

## Platform

This project is implemented on top of Contiki-NG (https://github.com/contiki-ng/contiki-ng), an open-source operating system for IoT devices.

## Disclaimer

This repository contains a research-oriented implementation intended for
experimental evaluation. It may not be suitable for production environments.
