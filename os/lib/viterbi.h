#ifndef VITERBI_H
#define VITERBI_H

#include <stdint.h>
#include <stdlib.h>
#include "hmm-config.h"

typedef struct {
  uint8_t num_states;

  // Transition probabilities A[i][j]
  const float *pi;  // Initial probabilities (size num_states)
  const float *A;   // Flattened view (size num_states*num_states)

  float delta[VITERBI_MAX_STATES];     // Current delta values (size num_states)
  float delta_tmp[VITERBI_MAX_STATES]; // Scratch buffer (size num_states)
} viterbi_t;

void viterbi_init(viterbi_t *ctx,
                  uint8_t num_states,
                  const float *pi,
                  const float *A);

void viterbi_step(viterbi_t *ctx, const float *emission);

uint8_t viterbi_state(const viterbi_t *ctx);

void viterbi_reset(viterbi_t *ctx);

#endif /* VITERBI_H */
