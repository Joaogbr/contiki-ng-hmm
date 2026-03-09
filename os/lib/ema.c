#include "contiki-conf.h"
#include "ema.h"

#ifdef ENABLE_EMANEXT

#include <math.h>

/*---------------------------------------------------------------------------*/
/* Exponential Moving Average (EMA) function. */
float emanext(float prev_ema, float new_val, float time_diff_secs, float tau)
{
  float ema_wgt = exp(-time_diff_secs / tau);
  return prev_ema * ema_wgt + new_val * (1 - ema_wgt);
}

#endif /* ENABLE_EMANEXT */