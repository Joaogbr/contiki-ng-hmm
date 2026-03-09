#include "link-features.h"
#include "hmm.h"
#include "seqhmm.h"

#define WARM_START_THRESH (60 * (clock_time_t)CLOCK_SECOND)
#define HMM_UPDATE_PERIOD CLOCK_SECOND

/*---------------------------------------------------------------------------*/
static void lf_hmm_init(void)
{
  link_hmm_init();
}
/*---------------------------------------------------------------------------*/
static void lf_hmm_on_stats_init(struct link_stats *stats)
{
}
/*---------------------------------------------------------------------------*/
static void lf_hmm_on_tx(struct link_stats *stats)
{
}
/*---------------------------------------------------------------------------*/
static void lf_hmm_on_rx(struct link_stats *stats)
{
  if(stats != NULL && stats->rx_time[0] != 0) {
    struct link_hmm_ctx *hmm;
    
    hmm = link_hmm_from_lladdr(link_stats_get_lladdr(stats));
    if(hmm != NULL) {
      /* Warm start / Hard reset */
      clock_time_t gap = clock_time() - stats->rx_time[0];
      if(gap > WARM_START_THRESH && hmm->seq_count > 0) {
        hmm_reset(&hmm->ctx);
        hmm->seq_count = 0;
      }
      /* Update HMM */
      int16_t trend = stats->rssi[0] - stats->rssi_smoothed;
      int16_t raw_obs[HMM_OBS];
      raw_obs[0] = stats->rssi[0];
      raw_obs[1] = trend;
      hmm_update_obs(&hmm->ctx, raw_obs);
      hmm->state = hmm_step(&hmm->ctx);
      hmm->seq_count++;
    }
  }
}
/*---------------------------------------------------------------------------*/
static void lf_hmm_reset(void)
{
  link_hmm_reset();
}
/*---------------------------------------------------------------------------*/
const link_features_t lf_hmm = {
  lf_hmm_init,
  lf_hmm_on_stats_init,
  lf_hmm_on_tx,
  lf_hmm_on_rx,
  lf_hmm_reset
};