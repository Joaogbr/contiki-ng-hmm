#ifndef LINK_FEATURES_H_
#define LINK_FEATURES_H_

#include "net/link-stats.h"
#include "link-hmm-ctx.h"

typedef struct link_features {
    /* On link-stats module initialization */
    void (*link_features_init)(void);
    /* On link statistics initialization */
    void (*link_features_on_stats_init)(struct link_stats *stats);
    /* On packet transmissions */
    void (*link_features_on_tx)(struct link_stats *stats);
    /* On packet receptions */
    void (*link_features_on_rx)(struct link_stats *stats);
    /* On link-stats module reset */
    void (*link_features_reset)(void);
} link_features_t;

extern const link_features_t lf_default;
extern const link_features_t lf_hmm;

#endif /* LINK_FEATURES_H_ */