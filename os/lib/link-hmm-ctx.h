#ifndef LINK_HMM_CTX_H_
#define LINK_HMM_CTX_H_

#include "net/linkaddr.h"
#include "hmm.h"

struct link_hmm_ctx {
  hmm_ctx_t ctx;
  uint8_t state;
  uint16_t seq_count;
};

/* API */
struct link_hmm_ctx *link_hmm_from_lladdr(const linkaddr_t *addr);
void link_hmm_reset(void);
void link_hmm_init(void);

#endif /* LINK_HMM_CTX_H_ */
