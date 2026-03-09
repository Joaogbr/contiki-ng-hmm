#include <float.h>
#include "viterbi.h"

#define MIN(a,b) ((a)<(b)?(a):(b))

/* Helper: argmax over float array */
static uint8_t argmax(const float *v, uint8_t n)
{
  uint8_t best = 0;
  float best_val = v[0];
  for(uint8_t i = 1; i < n; i++) {
    if(v[i] > best_val) {
      best = i;
      best_val = v[i];
    }
  }
  return best;
}

static void normalize_log_delta(viterbi_t *ctx)
{
  float max_val = ctx->delta[0];
  uint8_t N = ctx->num_states;

  /* Find max */
  for(uint8_t i = 1; i < N; i++) {
    if(ctx->delta[i] > max_val) {
      max_val = ctx->delta[i];
    }
  }

  /* Skip if all states are impossible */
  if(max_val == -FLT_MAX) {
    return;
  }

  /* Subtract max from all states */
  for(uint8_t i = 0; i < N; i++) {
    ctx->delta[i] -= max_val;
  }
}

void viterbi_init(viterbi_t *ctx,
                  uint8_t num_states,
                  const float *pi,
                  const float *A)
{
  uint8_t N = MIN(num_states, VITERBI_MAX_STATES);
  ctx->num_states = N;
  ctx->pi = pi;
  ctx->A = A;

  // Initialize delta with initial probabilities
  for(uint8_t i = 0; i < N; i++) {
    ctx->delta[i] = pi[i];
  }

  // Clear scratch buffer
  for(uint8_t i = 0; i < N; i++) {
    ctx->delta_tmp[i] = -FLT_MAX;
  }

  /* Normalize to keep numbers bounded */
  normalize_log_delta(ctx);
}

/*
 * One Viterbi iteration:
 * delta_new[j] = max_i(delta[i] + A[i->j]) + emission[j]
 */
void viterbi_step(viterbi_t *ctx, const float *emission)
{
  uint8_t N = ctx->num_states;

  for(uint8_t j = 0; j < N; j++) {
    float best = -FLT_MAX;

    const float *A = ctx->A;
    for(uint8_t i = 0; i < N; i++) {
      const float *Ai = &A[i * N];
      float candidate = ctx->delta[i] + Ai[j];
      if(candidate > best) {
        best = candidate;
      }
    }

    ctx->delta_tmp[j] = best + emission[j];
  }

  // Swap buffers
  for(uint8_t i = 0; i < N; i++) {
    ctx->delta[i] = ctx->delta_tmp[i];
  }

  /* Normalize to keep numbers bounded */
  normalize_log_delta(ctx);
}

uint8_t viterbi_state(const viterbi_t *ctx)
{
  return argmax(ctx->delta, ctx->num_states);
}

void viterbi_reset(viterbi_t *ctx)
{
  uint8_t N = ctx->num_states;
  // Initialize delta with initial probabilities
  for(uint8_t i = 0; i < N; i++) {
    ctx->delta[i] = ctx->pi[i];
  }

  // Clear scratch buffer
  for(uint8_t i = 0; i < N; i++) {
    ctx->delta_tmp[i] = -FLT_MAX;
  }

  /* Normalize to keep numbers bounded */
  normalize_log_delta(ctx);
}