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

https://wiki.wubrowse.org/How_to_install_tabix

https://samtools.github.io/bcftools/howtos/install.html

## Starting the streamlit server

In order to start the streamlit server, run

```
streamlit run main.py
```

and your are good to go.

## User guidelines

Guidelines on how to use the altafplotter and interpretation of potential UPD findings can be found [here](https://github.com/maxmilianr/altafplotter_public/blob/main/user_guideline/user_guideline.md).

## Integration with Varvis/Gepado

We run a local version of this tool, that is integrated with our NGS-evaluation software Varvis and our LIMS Gepado.

Feel free to [contact us](mailto:hug-ito@medizin.uni-leipzig.de), if you are interested in integrating your LIMS or NGS-software.

## License

MIT License

Copyright (c) 2023 HUG IT-Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
