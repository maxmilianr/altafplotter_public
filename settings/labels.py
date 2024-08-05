from settings import settings


sidebar_title = "# 🦔 AltAF-Plotter"
sidebar_subtitle = """
:grey_question: **new here?**
check our [altAFplotter-guidelines]("""+settings.main_page_config["page_menu_items"]["Get help"]+")"

header_guideline = "## :books: Quick Interpretation Guide"
header_consanguinity = "**:dna: Consanguinity**"
legend_consanguinity = """
    **`consanguinity unlikely`**&rarr; no striking ROH pattern detected

    **`consanguinity likely`**&rarr; multiple ROHs detected, handle UPD flags with extra care 


    **Settings:**

    **`>{consanguin_min_chr_count}`** chromosomes covered by **`>{consanguin_roh_cutoff}%`** ROHs
"""

header_flagging = "**:rainbow-flag: UPD-flags**"
legend_flagging ="""
    **`roh_high`**&rarr;potential isodisomy :warning: check for deletions

    **`roh_high_mixed`**&rarr; potential isodisomy or mixed UPD :warning: check for deletions

    **`inh_ratio_high`**&rarr; potential heterodisomy  
    
    **`roh_high(_mixed)+inh_ratio_high`**&rarr; potential isodisomy or mixed UPD
    """

header_flag_settings = "**:gear: Flagging criteria**"
legend_flag_settings = """
    **inheritance ratios:**

    **`inh_ratio_high:`**

    *in duos:* ratio of (m/p)aternal/not (m/p)aternal SNVs per chr: **`> {inh_ratio_high_trio_cutoff}`**

    *in trios:* ratio of maternal/paternal (or vice versa) per chr: **`> {inh_ratio_high_duo_cutoff}`**

    **ROHs:**

    `roh_high`: chromosome is covered by **`>{roh_high_cutoff}%`** ROHs

    `roh_high_mixed`: chromosome is covered by **`{roh_high_mixed_start}-{roh_high_mixed_end}%`** ROHs

    **insufficient SNVs**

    `insufficient_snvs`: less than **`{min_snvs_per_chr}`** SNVs for this chromosome, insufficient to reliably detect UPD features

"""
header_legend = "**:bar_chart: Plot legends/UPD regions**"
yellow_squares = ":large_yellow_square: runs of homozygosity"
purple_squares = ":large_purple_square: main UPD-sensitive regions:"
upd_regions = """
            Prader Willi/Angelman on chr. 15
            Silver-Russel on chr. 7
            Temple-Syndrom/
            Kagami-Ogata on chr. 14
            """
### Settings
header_settings = "## :gear: Settings"
select_assembly = "## :butter: select your assembly"
select_assembly_btn = "## this will affect the position or the known UPD regions"

### Additional Information
header_additional_info = "## :card_file_box: Additional Information"

header_cohort = ":people_holding_hands: cutoffs and population"
text_cohort = """
Cutoffs used for UPD detection have been determined with a largely western european cohort.
The reliability of UPD-tagging for patients from another population is therefore yet to be determined.
Please pay extra attention to the provided plots and graphs, in addition to the flags, if your patient is from a non-european population.
We are working on including extensive population data to make UPD detection reliable for everyone!
"""

header_requirements = "## :page_facing_up: VCF requirements"
text_requirements = """
	vcf file requirements:
	- adhere to vcf-fileformat > 4.1
	- single sample files (multisample support is coming soon)
	- contain format fields: AD,DP
	- contain info fields: AC,AN
	- bgzipped
	- vcf files should be unfiltered or only moderately quality filtered. Too stringent filters can introduce ROH-artefacts.
	- vcfs should be generated with a best-practice workflow, resulting in good specificity and sensitivity 
	- vcfs from panel analyses must contain sufficient SNVs per chromosome to allow UPD detection. Panels for narrow phenotypes are unsuitable for this analysis.

		
	:bulb: if your files are not accepted, you can compare them to a sample vcf in the Demo-tab or [contact us.](https://github.com/HUGLeipzig/altafplotter/issues)
"""
header_my_files = "## :wastebasket: What happens to my files?"
text_my_files = """
	vcf files are processed as follows:
	- uploaded files are indexed with tabix
	- files are then analysed with bcftools roh and bcftools isec
	- files are then parsed with cyvcf2
	- all uploaded and generated files are deleted immediatly
	- if any of the above step fails, all files are deleted
	
	Data usage:
	- your uploaded files are not used in any way other than what is required for the detection of UPDs and the visualization depicted here and removed from our systems as soon as possible.
"""

header_clinical_setup = ":hospital: Clinical Usage"
text_clinical_setup = """
	For clinical use, we recommend the following setup:
	- [Set up your your own local instance.](https://github.com/HUGLeipzig/altafplotter) Which could also be directly connected to your LIMS and bioinformatic services.
	- Validate with your own dataset. Genetic workflows are diverse and might produce different outcomes to what we established the app with. To make sure, our settings are valid for your data, perform your own validation. [Cutoffs can then be adjusted if necessary.](https://github.com/HUGLeipzig/altafplotter/blob/c97bc690bd6f27c85232c24a932d907688385535/settings/settings.py#L93)
"""