#include "seqhmm.h"
#include <float.h>

#define RSSI_LIMIT    -78
#define TREND_LIMIT   3

/*---------------------------------------------------------------------------*/
/* Discretization Functions */
static uint8_t discretize_rssi(int16_t rssi)
{
  return (rssi >= RSSI_LIMIT) ? 1 : 0; // 0 = bad, 1 = good
}

static uint8_t discretize_trend(int16_t trend)
{
  /* trend < -TREND_LIMIT -> bin 0 (down)
     |trend| <= TREND_LIMIT -> bin 1 (stable)
     trend > TREND_LIMIT -> bin 2 (up) */
  if(trend < -TREND_LIMIT) {
    return 0;
  } else if(trend > TREND_LIMIT) {
    return 2;
  } else {
    return 1;
  }
}

/*---------------------------------------------------------------------------*/
/* Initialization */
static void seqhmm_init(hmm_ctx_t *ctx, const void *model)
{
  seqhmm_ctx_t *s = (seqhmm_ctx_t *)ctx;
  const hmm_model_t *m = (const hmm_model_t *)model;

  ctx->model = m;
  ctx->obs = s->obs;

  // Initialize Viterbi with pi, A, and  no. of states
  viterbi_init(&ctx->vt, m->num_states, m->pi, m->A);

  // Initialize obs with a neutral bin
  ctx->obs[0] = 0;
  ctx->obs[1] = 1;
}

/*---------------------------------------------------------------------------*/
/* Update Observations */
static void seqhmm_update_obs(hmm_ctx_t *ctx, const int16_t *raw_obs)
{
  ctx->obs[0] = discretize_rssi(raw_obs[0]);
  ctx->obs[1] = discretize_trend(raw_obs[1]);
}
/*---------------------------------------------------------------------------*/
static float seqhmm_emission(const hmm_ctx_t *ctx, uint8_t state)
{
  const hmm_model_t *m = ctx->model;
  float p = 0.0f; // Using log-domain

  // B is flattened
  uint16_t obs_offset = 0;
  uint8_t N = m->num_states;
  const uint8_t *obs = ctx->obs;
  for(uint8_t i = 0; i < m->num_obs; i++) {
    uint8_t bin_offset = obs[i];

    if(bin_offset >= m->bins[i]) {
      return -FLT_MAX; // Impossible observation
    }

    uint16_t state_offset = state * m->bins[i];

    // Assume independence -> multiply
    p += m->B[obs_offset + state_offset + bin_offset]; // Using log-domain
    obs_offset += N * m->bins[i];
  }
  return p;
}

/*---------------------------------------------------------------------------*/
const hmm_api_t seqhmm_api = {
  .init = seqhmm_init,
  .update_obs = seqhmm_update_obs,
  .emission = seqhmm_emission,
  .step = NULL,
  .state = NULL
};
