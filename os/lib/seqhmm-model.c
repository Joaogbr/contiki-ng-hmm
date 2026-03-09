#include "seqhmm.h"
#include "hmm-config.h"
#include <float.h>

static const uint8_t seqhmm_bins[HMM_OBS] = {
  2, 3
};

static const float seqhmm_pi[HMM_STATES] = {
  -0.320514f, -FLT_MAX, -FLT_MAX, -1.293664f
};

static const float seqhmm_A[HMM_STATES*HMM_STATES] = {
  -0.140503f, -2.049311f, -6.134276f, -18.077145f,
  -1.820933f, -0.311814f, -3.486830f, -2.586303f,
  -2.700909f, -3.150760f, -0.405095f, -1.500472f,
  -FLT_MAX,   -3.621240f, -1.802589f, -0.212627f
};

static const float seqhmm_B[HMM_STATES * HMM_BIN_SUM] = {
  // RSSI (2 bins)
  -0.010686f, -4.544778f,
  -5.131381f, -0.005932f,
  -0.023981f, -3.743463f,
  -17.744219f, -0.000000020f,

  // Trend (3 bins)
  -1.931616f, -0.306348f, -2.130875f,
  -FLT_MAX,   -2.764241f, -0.065162f,
  -0.174255f, -1.832788f, -FLT_MAX,
  -1.511531f, -0.437373f, -2.012903f
};

const hmm_model_t seqhmm_model = {
  .num_states = HMM_STATES,
  .num_obs = HMM_OBS,
  .bins = seqhmm_bins,
  .pi = seqhmm_pi,
  .A  = seqhmm_A,
  .B  = seqhmm_B
};