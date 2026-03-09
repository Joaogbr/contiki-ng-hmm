#ifndef HMM_CONFIG_H
#define HMM_CONFIG_H

/* -------------------------------------------------------------------------
 * HMM dimensions
 * ------------------------------------------------------------------------- */

#define HMM_STATES      4
#define HMM_OBS         2
#define HMM_RSSI_BINS   2
#define HMM_TREND_BINS  3
#define HMM_BIN_SUM     (HMM_RSSI_BINS + HMM_TREND_BINS)

/* -------------------------------------------------------------------------
 * Viterbi limits
 * ------------------------------------------------------------------------- */

/*
 * IMPORTANT:
 * This must be >= the maximum number of states of *any* HMM in the system.
 */
#define VITERBI_MAX_STATES  HMM_STATES

#endif /* HMM_CONFIG_H */
