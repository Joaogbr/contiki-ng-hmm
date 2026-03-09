#ifndef EMA_H_
#define EMA_H_

#ifdef ENABLE_EMANEXT

/* Exponential Moving Average (EMA) function. */
float emanext(float prev_ema, float new_val, float time_diff_secs, float tau);

#endif /* ENABLE_EMANEXT */

#endif /* EMA_H_ */