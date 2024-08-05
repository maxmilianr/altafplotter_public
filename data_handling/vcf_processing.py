import streamlit as st
import pandas as pd
from cyvcf2 import VCF
from io import StringIO
import subprocess
from tempfile import NamedTemporaryFile
import os
from settings import settings

from data_handling import general_functions


@st.cache_data
def collect_snv_inheritance(vcf_dict):
    # 1. index, mother and father:
    if (vcf_dict["index"] and vcf_dict["mother"] and vcf_dict["father"]):
        inheritance_dict = settings.inheritance_dict_trio
        
        cmd = ["bcftools isec -n +1 " + vcf_dict["index"] + " " + vcf_dict["mother"] + " " + vcf_dict["father"]]
        domain_setting = "trio"
    
    # 2. index and mother:
    elif (vcf_dict["index"] and vcf_dict["mother"]):
        inheritance_dict = settings.inheritance_dict_duo_mother

        cmd = ["bcftools isec -n +1 " + vcf_dict["index"] + " " + vcf_dict["mother"] ]
        domain_setting = "duo_mat"

    # 3. index and father:
    elif (vcf_dict["index"] and vcf_dict["father"]):
        inheritance_dict = settings.inheritance_dict_duo_father
        cmd = ["bcftools isec -n +1 " + vcf_dict["index"] + " " + vcf_dict["father"] ]
        domain_setting = "duo_pat"

    if cmd:
        
        isec_result = StringIO(subprocess.check_output(cmd, shell=True).decode('utf-8'))
        df_isec = pd.read_csv(isec_result, sep="\t", header=None, dtype=str, names=["chr", "pos", "ref", "alt","snv_occurence"])
        df_isec["pos"] = df_isec["pos"].astype(int)
        df_isec["snv_occurence"] = df_isec["snv_occurence"].replace(inheritance_dict, regex=True)
        
        return df_isec, domain_setting
    
@st.cache_data
def read_vcf_file(vcf_file):
    
    if vcf_file is None:
        st.warning("no vcf-file obtained, please select another analysis")
        st.stop()
    
    df_vcf_variants = pd.DataFrame(columns = ["chr", "start", "end", "altAF", "quality", "reads"])

    li_chr = []
    li_start = []
    li_end = []
    li_qual = []
    li_af = []
    li_reads = []

    try:
        for variant in VCF(vcf_file):
            
            # some variants have no alt allele, these return "[]" as ALT 
            if not variant.ALT == []:
                # calculate altAF from alt alleles and depth
                ad = variant.format('AD') #TODO -> move to settings
                dp = variant.format('DP') #TODO -> move to settings
                
                if (ad is None) or (dp is None):
                    altaf = 0
                else:
                    altaf = ad[0,1] / dp[0,0]

                li_chr.append(variant.CHROM)
                li_start.append(variant.POS)
                li_end.append(variant.POS + len(variant.REF))
                li_qual.append(variant.QUAL)
                li_af.append(altaf)
                if not dp is None:
                    li_reads.append(dp[0,0])
                else:
                    li_reads.append(0)
        
        df_vcf_variants["chr"] = li_chr
        df_vcf_variants["start"] = li_start
        df_vcf_variants["end"] = li_end
        df_vcf_variants["quality"] = li_qual
        df_vcf_variants["altAF"] = li_af
        df_vcf_variants["reads"] = li_reads

        df_vcf_variants["start"] = df_vcf_variants["start"].astype(int)

        return df_vcf_variants
    
    except Exception as e:
    
        st.error(
            """
                Parsing of the vcf-file failed, please make sure your file is formatted according to [4.1](https://samtools.github.io/hts-specs/VCFv4.1.pdf) specifications or higher and can be parsed with cyvcf2.
                If the Problem persists, please [contact](https://github.com/HUGLeipzig/altafplotter/issues) us.
            """
        )
        with st.expander("parsing error message"):
            st.code(repr(e))
        general_functions.delete_vcfs(vcf_file)
        st.stop()

@st.cache_data 
def detect_roh(vcf_file):

    cmd = ["bcftools roh --AF-dflt 0.4 -I " + vcf_file + " | awk '$1==\"RG\"{print $0}'"]
    bcf_roh_results = StringIO(subprocess.check_output(cmd, shell=True).decode('utf-8'))

    df_roh_rg = pd.read_csv(bcf_roh_results, sep="\t", names=["RG", "sample", "chr", "start", "end", "length", "number_of_markers", "quality"])
    if df_roh_rg.empty:
        cmd = ["bcftools roh --AF-dflt 0.4 -G 30 -I " + vcf_file + " | awk '$1==\"RG\"{print $0}'"]
        bcf_roh_results = StringIO(subprocess.check_output(cmd, shell=True).decode('utf-8'))
        df_roh_rg = pd.read_csv(bcf_roh_results, sep="\t", names=["RG", "sample", "chr", "start", "end", "length", "number_of_markers", "quality"])
    
    df_roh_rg["chr"] = df_roh_rg["chr"].astype(str)
    df_roh_rg["chr"] = df_roh_rg["chr"].str.replace("chr", "")
    return df_roh_rg

@st.cache_data 
def create_vcf_tbi(vcf_file):
    if not os.path.isfile(vcf_file + ".tbi"):
        try:
            cmd = ["tabix " + vcf_file]
            tabix_result = StringIO(subprocess.check_output(cmd, shell=True).decode('utf-8'))
            return True
        except:
            st.warning(
                """
                    tabix failed, please make sure your file is formatted according to [4.1](https://samtools.github.io/hts-specs/VCFv4.1.pdf) specifications or higher and bgzipped.
                    If the Problem persists, please [contact](https://github.com/HUGLeipzig/altafplotter/issues) us.
                """
            )
            return False


def save_temporary_file(vcf_file_in):
    with NamedTemporaryFile("wb", suffix=".vcf.gz", delete=False) as vcf_file:
        vcf_file.write(vcf_file_in.getvalue())
    if not create_vcf_tbi(vcf_file.name):
        general_functions.delete_vcfs(vcf_file.name)
        st.stop()
    return vcf_file.name