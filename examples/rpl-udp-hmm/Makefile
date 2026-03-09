CONTIKI_PROJECT = udp-client udp-server
all: $(CONTIKI_PROJECT)

PROJECT_SOURCEFILES += link-features-def.c link-features-hmm.c link-hmm-ctx.c hmm.c seqhmm.c seqhmm-model.c viterbi.c

# Add math library
USE_LIBM ?= 1
PROJECT_SOURCEFILES += ema.c

MAKE_MAC = MAKE_MAC_CSMA
MAKE_ROUTING = MAKE_ROUTING_RPL_CLASSIC

CONTIKI=../..
include $(CONTIKI)/Makefile.include
