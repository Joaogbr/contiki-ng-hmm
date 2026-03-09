#ifndef HMM_BINDINGS_H
#define HMM_BINDINGS_H

#include "hmm.h"

/* Visible models and APIs */
extern const hmm_api_t seqhmm_api;
extern const hmm_model_t seqhmm_model;

/* HMM selection */
#define HMM_API    (&seqhmm_api)
#define HMM_MODEL  (&seqhmm_model)

#endif /* HMM_BINDINGS_H */
