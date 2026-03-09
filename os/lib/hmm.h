#ifndef HMM_H
#define HMM_H

#include <stdint.h>
#include "viterbi.h"

struct hmm_ctx;

typedef struct {
  /* Initialize context */
  void (*init)(struct hmm_ctx *ctx, const void *model);
  /* Update input observations */
  void (*update_obs)(struct hmm_ctx *ctx, const int16_t *raw_obs);
  /* Compute Emission Probability */
  float (*emission)(const struct hmm_ctx *ctx, uint8_t state);
  /* Advance Viterbi one step and return current state */
  uint8_t (*step)(struct hmm_ctx *ctx);
  /* Get most likely current state */
  uint8_t (*state)(const struct hmm_ctx *ctx);
} hmm_api_t;

typedef struct {
  uint8_t num_states;
  uint8_t num_obs;
  const uint8_t *bins;

  // Initial probabilities π[i]
  const float *pi;
  
  // Transition probabilities matrix A[i][j]
  const float *A;

  // Emissions (multivariate)
  const float *B;
} hmm_model_t;

typedef struct hmm_ctx {
  const hmm_api_t *api;
  const void *model;
  viterbi_t vt;
  uint8_t *obs;
  float emission[VITERBI_MAX_STATES];
} hmm_ctx_t;

void hmm_init(hmm_ctx_t *ctx, const hmm_model_t *model, const hmm_api_t *api);
void hmm_update_obs(hmm_ctx_t *ctx, const int16_t *raw_obs);
uint8_t hmm_step(hmm_ctx_t *ctx);
uint8_t hmm_state(const hmm_ctx_t *ctx);
void hmm_reset(hmm_ctx_t *ctx);

#endif /* HMM_H */