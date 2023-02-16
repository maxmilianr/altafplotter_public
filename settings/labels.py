from settings import settings

sidebar_title = "# 🦔 AltAF-Plotter_beta"
sidebar_subtitle = """
:grey_question: **new here?**
check our [altAFplotter-guidelines](
""" + settings.main_page_config["page_menu_items"]["Get help"] + ")"

sidebar_legend = """
## :books: Quick Interpretation Guide
### :dna: Consanguinity
**`consanguinity unlikely`**&rarr; no striking ROH pattern detected

**`consanguinity likely`**&rarr; multiple ROHs detected, handle UPD flags with extra care 

### :rainbow-flag: UPD-flags
**`roh_high`**&rarr;potential isodisomy :warning: check for deletions

**`roh_high_mixed`**&rarr; potential isodisomy or mixed UPD :warning: check for deletions

**`inh_ratio_high`**&rarr; potential heterodisomy  
 
**`roh_high(_mixed)+inh_ratio_high`**&rarr; potential isodisomy or mixed UPD

### :gear: Flagging criteria 
**consanguinity:**

`>{consanguin_min_chr_count}` chromosomes covered by `>{consanguin_roh_cutoff}%` ROHs

**inheritance ratios:**

`inh_ratio_high:` 

*in duos:* ratio of (m/p)aternal/not (m/p)aternal SNVs per chr: `> {inh_ratio_high_trio_cutoff}`

*in trios:* ratio of maternal/paternal (or vice versa) per chr: `> {inh_ratio_high_duo_cutoff}`

**ROHs:**

`roh_high`: chromosome is covered by `>{roh_high_cutoff}%` ROHs

`roh_high_mixed`: chromosome is covered by `{roh_high_mixed_start}-{roh_high_mixed_end}%` ROHs

**insufficient SNVs**

`insufficient_snvs`: less than `{min_snvs_per_chr}` SNVs for this chromosome, insufficient to reliably detect UPD features

"""