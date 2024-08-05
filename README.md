# altafplotter_public

Plotting alternative allele fractions and identifying UPDs

This tool is a python streamlit app, and allows for quick and interactive exploration of panel or exome-vcf files.

Additionally, all deviations from expected distributions of ROHs and inheritance are flagged accordingly, to allow a reliable detection of potential UPD-patterns.

Publication:

[altAFplotter: a web app for reliable UPD detection in NGS diagnostics](https://www.biorxiv.org/content/10.1101/2023.08.08.546838v1)

## Public version

A public version of the plotter is available [here](https://altafplotter.uni-leipzig.de/).

## Installation

Install python packages

`pip install -r requirements.txt`

Install additional tools needed:

[Tabix](https://wiki.wubrowse.org/How_to_install_tabix)

[BCFtools](https://samtools.github.io/bcftools/howtos/install.html)

## Starting the streamlit server

In order to start the streamlit server, run

```
streamlit run main.py
```

and your are good to go.

## User guidelines

Guidelines on how to use the altafplotter and interpretation of potential UPD findings can be found [here](https://github.com/HUGLeipzig/altafplotter/blob/main/user_guideline/user_guideline.md).

## Integration with Varvis/Gepado

We run a local version of this tool, that is integrated with our NGS-evaluation software Varvis and our LIMS Gepado.

Feel free to [contact us](mailto:hug-ito@medizin.uni-leipzig.de), if you are interested in integrating your LIMS or NGS-software.

There is a branch available, that includes the varvis functionality, here is what you need to do to use it:

1. switch branch to `varvis_release_1.x.x`
2. `toggle_varvis` in `settings.settings` should be `True`
3. add your varvis url and user credentials in `settings.credentials`
