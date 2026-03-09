#ifndef SEQHMM_H
#define SEQHMM_H

#include <stdint.h>
#include "hmm.h"
#include "hmm-config.h"

typedef struct {
  hmm_ctx_t hmm;

  // last discretized observations (for debugging or access)
  uint8_t obs[HMM_OBS];
} seqhmm_ctx_t;


/* Exposed API and model */
extern const hmm_api_t seqhmm_api;
extern const hmm_model_t seqhmm_model;

#endif /* SEQHMM_H */
