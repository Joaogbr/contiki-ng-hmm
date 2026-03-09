#include "link-features.h"

/*---------------------------------------------------------------------------*/
static void lf_def_init(void)
{
}
/*---------------------------------------------------------------------------*/
static void lf_def_on_stats_init(struct link_stats *stats)
{
}
/*---------------------------------------------------------------------------*/
static void lf_def_on_tx(struct link_stats *stats)
{
}
/*---------------------------------------------------------------------------*/
static void lf_def_on_rx(struct link_stats *stats)
{
}
/*---------------------------------------------------------------------------*/
static void lf_def_reset(void)
{
}
/*---------------------------------------------------------------------------*/
const link_features_t lf_default = {
  lf_def_init,
  lf_def_on_stats_init,
  lf_def_on_tx,
  lf_def_on_rx,
  lf_def_reset
};