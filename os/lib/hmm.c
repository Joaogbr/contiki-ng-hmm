#include "hmm.h"

/*---------------------------------------------------------------------------*/
/* Initialize Context */
void hmm_init(hmm_ctx_t *ctx, const hmm_model_t *model, const hmm_api_t *api)
{
  ctx->api = api;
  ctx->model = model;
  
  /* Let model-specific code initialize everything else */
  api->init(ctx, model);
}

/*---------------------------------------------------------------------------*/
/* Update Observation Context */
void hmm_update_obs(hmm_ctx_t *ctx, const int16_t *raw_obs)
{
  ctx->api->update_obs(ctx, raw_obs);
}

/*---------------------------------------------------------------------------*/
/* Advance Viterbi by one Step Using Emission Vector */
uint8_t hmm_step(hmm_ctx_t *ctx)
{
  const hmm_model_t *m = ctx->model;
  float *emit = ctx->emission;
  uint8_t N = m->num_states;

  /* Emission computation is delegated to model API */
  for(uint8_t s = 0; s < N; s++) {
    emit[s] = ctx->api->emission(ctx, s);
  }

  viterbi_step(&ctx->vt, emit);

  // Return current best state
  return viterbi_state(&ctx->vt);
}

/*---------------------------------------------------------------------------*/
/* Get Current HMM State */
uint8_t hmm_state(const hmm_ctx_t *ctx)
{
  return viterbi_state(&ctx->vt);
}

/*---------------------------------------------------------------------------*/
/* Reset Context */
void hmm_reset(hmm_ctx_t *ctx)
{
  viterbi_reset(&ctx->vt);
}