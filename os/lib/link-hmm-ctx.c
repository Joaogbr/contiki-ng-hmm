#include "link-hmm-ctx.h"
#include "net/nbr-table.h"
#include "hmm-selection.h"

NBR_TABLE(struct link_hmm_ctx, link_hmm_ctx);

/*---------------------------------------------------------------------------*/
/* Returns HMM context module */
struct link_hmm_ctx *
link_hmm_from_lladdr(const linkaddr_t *addr)
{
  struct link_hmm_ctx *entry;

  entry = nbr_table_get_from_lladdr(link_hmm_ctx, addr);
  if(entry == NULL) {
    entry = nbr_table_add_lladdr(link_hmm_ctx, addr, NBR_TABLE_REASON_UNDEFINED, NULL);

    if(entry != NULL) {
      hmm_init(&entry->ctx, HMM_MODEL, HMM_API);
      entry->state = 0;
      entry->seq_count = 0;
    }
  }
  return entry;
}
/*---------------------------------------------------------------------------*/
/* Resets HMM context module */
void
link_hmm_reset(void)
{
  struct link_hmm_ctx *entry;
  entry = nbr_table_head(link_hmm_ctx);
  while(entry != NULL) {
    nbr_table_remove(link_hmm_ctx, entry);
    entry = nbr_table_next(link_hmm_ctx, entry);
  }
}
/*---------------------------------------------------------------------------*/
/* Initializes HMM context module */
void
link_hmm_init(void)
{
  nbr_table_register(link_hmm_ctx, NULL);
}
