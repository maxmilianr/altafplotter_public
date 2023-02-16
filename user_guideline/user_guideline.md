# Introduction

With this tool, copy number variations and uniparental disomies can be determined using alternative allele frequencies of SNVs/SNPs from NGS data.

The tool creates a plot with the chromosomal position on the x-axis and the alternative allele frequeny of all SNVs on the y-axis (Fig. 1).

![image-20230206131049-1.png](https://wiki.hugapps.medizin.uni-leipzig.de/xwiki/bin/download/How%20to/altAFplotter-Installation/WebHome/image-20230206131049-1.png?width=595&height=407&rev=1.1)

 **Fig 1** .: Distribution of alternative allele frequency. Different colors indicate inheritance of the specific SNP.

## UPD-Analysis

The following parameters are included in the evaluation of the alternative allele fractions per chromosome.

### ROH (= runs of homozygosity)

* continous stretch of DNA sequence without heterozygosity, all SNPs or microsatellites have two identical alleles
* cut offs for flagging have been determined using positive and negative controls

### Inheritance ratio

* SNV origins are determined via bcftools isec.
* For Trios, the inheritance ratios are the fraction of maternal over paternal (and vice versa) SNVs per chromosome. Here the expected ratio is 1 (50% paternal, 50% maternal variants).
* For duos, the ratio is calculated by the fraction of maternal over not maternal (or paternal over not paternal) variants.
* cut offs for flagging have been determined using positive and negative controls

Inheritance ratio can only used in Duo- or Trio analysis!

### Flags

Using the above mentioned parameters, each chromosome is analyzed and flagged with the following states (Tab. 1, Fig. 2):

| Flag                             | Cut-Offs                                             | Status/Interpretation                                          | Next steps                                                                                |
| -------------------------------- | ---------------------------------------------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| consanguinity unlikely           | <3 chromosomes with  >10% ROHs                       | -                                                              | check ROHs and inheritance ratios                                                         |
| consanguinity likely             | >=3 chromosomes >10% ROHs                            | handle potential UPD flags with extra care                     | check ROHs and inheritance ratio with extra care                                          |
| roh_high                         | > 70%                                                | potential Isodisomy or deletions                               | check CNV analysis: if there is no deletion, validate potential Isodisomy with 2nd method |
| roh_high_mixed                   | 20-70%                                               | potential Isodisomy or mixed UPD                               | check CNV analysis and inheritance ratio on this chromosome                               |
| inh_ratio_high                   | in Duos >2in Trios > 5                               | potential heterodisomy                                         | validate with 2nd method                                                                  |
| roh_high(_mixed) +inh_ratio_high | combined inh_ratio_high with roh_high/roh_high_mixed | potential isodisomy or mixed UPD                               | mixed UPD is possible, check CNV analysis for deletion and validate with 2nd methode      |
| insufficient_snv                 | <200 SNVs/chr                                        | number of SNVs is insufficient to reliably detect UPD features | exclude chromosomes from analysis                                                         |

![image-20230207082455-1.png](https://wiki.hugapps.medizin.uni-leipzig.de/xwiki/bin/download/How%20to/altAFplotter-Installation/WebHome/image-20230207082455-1.png?width=509&height=515&rev=1.1)

 **Fig. 2** : Overview of ROHs and inheritance ratios.


## Interpretation

## CNVs

#### Deletions

In case of a deletion, all reads come from the remaining allele. If this allele carries an SNV, the alternative allele frequency is ~1.0 (keep in mind, that this state is also true for isodisomies*).

Compare AltAF result with CNV analysis. Detection of CNVs is much more reliable and precise in a dedicated CNV analysis!

#### Duplications

Duplications can be identified through a shifted allele frequency (1/3 vs 2/3). CNV analysis is recommended for small and large duplication events. No additional information can be extracted from the altAF-plots.

EXAMPLE IMAGE

## Uniparental disomies

An uniparental disomy is characterized by the occurence of two chromosomes from one parent.

### Isodisomy

Isodisomy: the same parental chromosome is duplicated

All SNVs in an isodisomeric region are present in homozygous state and therefore have an alternative allele frequency of ~1. Thus, longer runs of homozygosity can be an indicator for an isodisomy.

It is important to compare this result with a CNV analysis – since two alleles are present in isodisomies, no copy number change should be observed.

![image-20230206131801-3.png](https://wiki.hugapps.medizin.uni-leipzig.de/xwiki/bin/download/How%20to/altAFplotter-Installation/WebHome/image-20230206131801-3.png?width=1026&height=460&rev=1.1)

**Fig. 3:** Distribution of SNPs on chromosome 14 indicate iUPD14(mat). ROH is marked in orange, color scheme represents inheritance of the SNPs (snv_occurence).

### Heterodisomy

Heterodisomy: both copies of a chromosome originate from one parent

The determination of heterodisomies is only possible with variant information of the parents.

A shifted inheritance ratio can indicate a heterodisomy and raises the flag  **inh_ratio_high** .

![image-20230206132437-6.png](https://wiki.hugapps.medizin.uni-leipzig.de/xwiki/bin/download/How%20to/altAFplotter-Installation/WebHome/image-20230206132437-6.png?width=946&height=638&rev=1.1)

 **Fig. 4** : Distribution of SNVs on chromosome 7 indicates a potential hUPD7 (mat) (A) Maternal (red) and paternal (green) are plotted. Note rare occurence of paternal variants. (B) Inheritance ratio mat_over_pat ~ 16 indicates that the number of paternal variants is low.

Be careful with mixed UPDs

Check potential UPDs with a second method, e.g. fragment analysis or SNParray

### How to handle consanguinity and mosaicism

#### Consanguinity

Depending on the degree of consanguinity, the number and length of ROHs is increased. The AltAF plotter calculates the occurence of ROHs over all chromosomes.

If least 3 chromosomes are covered by >10% ROHs each, the analysis is flagged with: **consanguinity_likely.**

This will mostly be accompanied by the **roh_high_mixed** flag. Execute extra caution, when interpreting consanguinous cases.

![image-20230206133834-10.png](https://wiki.hugapps.medizin.uni-leipzig.de/xwiki/bin/download/How%20to/altAFplotter-Installation/WebHome/image-20230206133834-10.png?width=831&height=855&rev=1.1)

# Closing remarks

The altAFplotter can support the analysis of whole-exome and large-panel data.

Cut-offs for UPD flagging and consanguinity calling have been determined using respective control cohorts.

Despite a high sensitivity, the individual evaluation of each case and flag raised is a sustained necissity. Therefore, be mindful with the interpretation and use a second method for validation.
