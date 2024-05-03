# Introduction

The altAFplotter allows detection of copy number variations and uniparental disomies using alternative allele frequencies and origin of SNVs/SNPs from NGS data.

Runs of homozygosity and the ratios of maternal and paternal variants are used to identfy the presence of a uniparental disomy.

ℹ️ vcf files are deleted as soon as the analysis steps are completed

## UPD-Analysis

The following parameters are included in the evaluation of the alternative allele fractions per chromosome.

### Runs of Homozygosity (ROH)

* continous stretch of DNA sequence without heterozygosity, all SNPs or microsatellites have two identical alleles
* allows the identification of isodisomies
* cut offs for flagging have been determined using appropriate controls
* ROHs are visualized as orange boxes in the AltAF-Plots

### Inheritance ratio

* Requires at least one additional parenal vcf file, better both.
* SNV origins are determined via bcftools isec.
* For Trios, the inheritance ratios are the fraction of maternal over paternal (and vice versa) SNVs per chromosome. Here the expected ratio is 1 (50% paternal, 50% maternal variants).
* For duos, the ratio is calculated by the fraction of maternal over not maternal (or paternal over not paternal) variants.
* cut offs for flagging have been determined using appropriate controls

Inheritance ratio can only used in Duo- or Trio analysis!

### UPD-sensitive regions

* certain regions are known to be disease causing, when included in a UPD
* these regions are visualized as purple boxes in the AltAF-Plots
* a description of these regions can be found in the sidebar, under "Plot legends/UPD regions"
* The exact coordinates for these regions are dependant on the assembly used. Select the correct assembly in the sidebar menu under "Settings".

### Flags

Using the above mentioned parameters, each chromosome is analyzed and flagged as follows:

| Flag                             | Cut-Offs                            | Status/Interpretation                                          | Next steps                                                                                |
| -------------------------------- | ----------------------------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| consanguinity unlikely           | <3 chromosomes with  >10% ROHs      | -                                                              | check ROHs and inheritance ratios                                                         |
| consanguinity likely             | >=3 chromosomes >10% ROHs           | handle potential UPD flags with extra care                     | check ROHs and inheritance ratio with extra care                                          |
| roh_high                         | > 70% ROH coverage per chromosome   | potential Isodisomy or deletions                               | check CNV analysis: if there is no deletion, validate potential Isodisomy with 2nd method |
| roh_high_mixed                   | 20-70% ROH coverage per chromosome | potential Isodisomy or mixed UPD                               | check CNV analysis and inheritance ratio on this chromosome                               |
| inh_ratio_high                   | in Duos >2; in Trios > 5            | potential heterodisomy                                         | validate with 2nd method                                                                  |
| roh_high(_mixed) +inh_ratio_high | as above                            | potential isodisomy or mixed UPD                               | mixed UPD is possible, check CNV analysis for deletion and validate with 2nd methode      |
| insufficient_snv                 | <200 SNVs/chr                       | number of SNVs is insufficient to reliably detect UPD features | exclude chromosomes from analysis                                                         |


### Chromosem Overview

The chromoseome overview table shows all chromosomes, their ROH and IR values and the flags that have been raised. If any of these values are above a defined threshhold, it is colored in orange or yellow.

![Figure 1](https://github.com/HUGLeipzig/altafplotter/blob/main/user_guideline/images/figure_2.png?raw=true)

**Fig. 1** : Overview of ROHs and inheritance ratios.

The plot "ROHs per Chromosome" shows an overview of all chromosomes and their ROH values. Cutoffs for ROH coverage are shown as yellow and orange boxes.

![Figure 2](https://github.com/HUGLeipzig/altafplotter/blob/main/user_guideline/images/roh_plot.png?raw=true)

**Fig. 2** : ROH-plot overview

The plot "Inheritance ratios" (only available in duo or trio analyses) plots ROH coverage versus inheritance ratio per chromosome, and for each chromosome the maternal and paternal ratios.

![Figure 3](https://github.com/HUGLeipzig/altafplotter/blob/main/user_guideline/images/IR_plot.png?raw=true)
**Fig. 3** : IR-plot overview


## Interpretation

See the "Quick Interpretation Guide" on the sidebar as a quick reference for flag interpretation and cutoffs.

## CNVs

#### Deletions

In case of a deletion, all reads come from the remaining allele. If this allele carries an SNV, the alternative allele frequency is ~1.0 (keep in mind, that this state is also true for isodisomies*).

Compare AltAF results with an appropriate CNV analysis. Detection of CNVs is much more reliable and precise in a dedicated CNV analysis!

#### Duplications

Duplications can be identified by a shifted allele frequency (1/3 vs 2/3). CNV analysis is recommended for small and large duplication events. No additional information can be extracted from the altAF-plots.

## Uniparental disomies

An uniparental disomy is characterized by the inheritance of two alleles of one chromosomes from one parent.

### Isodisomy

Isodisomy: the same parental chromosome is duplicated

All SNVs in an isodisomeric region are present in homozygous state and therefore have an alternative allele frequency of ~1. Thus, longer runs of homozygosity can be an indicator for an isodisomy.

It is important to compare this result with a CNV analysis – since two alleles are present in isodisomies, no copy number change should be observed.

![Figure 4](https://github.com/HUGLeipzig/altafplotter/blob/main/user_guideline/images/figure_3.png?raw=true)
**Fig. 4:** Distribution of SNPs on chromosome 14 indicate iUPD14(mat). ROH is marked in orange, color scheme represents inheritance of the SNPs (snv_occurence).

### Heterodisomy

Heterodisomy: both copies of a chromosome originate from one parent

The determination of heterodisomies is only possible with variant information of the parents.

A shifted inheritance ratio can indicate a heterodisomy and raises the flag  **inh_ratio_high** .

![Figure 5](https://github.com/HUGLeipzig/altafplotter/blob/main/user_guideline/images/figure_4.png?raw=true)
**Fig. 5** : Distribution of SNVs on chromosome 7 indicates a potential hUPD7 (mat) (A) Maternal (red) and paternal (green) are plotted. Note rare occurence of paternal variants. (B) Inheritance ratio mat_over_pat ~ 16 indicates that the number of paternal variants is low.

Be careful with mixed UPDs

Check potential UPDs with a second method, e.g. fragment analysis or SNParray

### How to handle consanguinity and mosaicism

#### Consanguinity

Depending on the degree of consanguinity, the number and length of ROHs is increased. The AltAF plotter calculates the occurence of ROHs over all chromosomes.

If least 3 chromosomes are covered by >10% ROHs each, the analysis is flagged with: **consanguinity_likely.**

This will mostly be accompanied by the **roh_high_mixed** flag. Execute extra caution, when interpreting consanguinous cases.

![Figure 6](https://github.com/HUGLeipzig/altafplotter/blob/main/user_guideline/images/figure_5.png?raw=true)

# Closing remarks

The altAFplotter can support the analysis of whole-exome and large-panel data.

Cut-offs for UPD flagging and consanguinity calling have been determined using respective control cohorts.

Despite a high sensitivity, the individual evaluation of each case and flag raised is a sustained necissity. Therefore, be mindful with the interpretation and use a second method for validation.
