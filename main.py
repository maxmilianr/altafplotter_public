
# =============================================================================
# This version of the altAFplotter allow upload of 3 vcf files, runs a series 
# of analyses and displays the results of a UPD detection method
#
# =============================================================================

import pandas as pd
import streamlit as st
import altair as alt
import pymssql
import xlsxwriter
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import subprocess
import sys
import os
from os.path import exists
from io import StringIO
from tempfile import NamedTemporaryFile
from cyvcf2 import VCF

from graph_plotter import graph_plotter
from settings import settings
from settings import labels

# =============================================================================
# setup app
# =============================================================================

# =============================================================================
# define parameters
# =============================================================================
personID = ""
kit_selection = []
from_vcf = False
df_altAF = pd.DataFrame()

df_snv_origin = pd.DataFrame()
vcf_file_index = ""
vcf_file_mother = ""
vcf_file_father = ""
plot_vcf = False
vcf_dict = {
        "index" : "",
        "mother" : "",
        "father" : "",
}
vcf_file_name = ""

# =============================================================================
# functions
# =============================================================================
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data

@st.cache()
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

def Set_Chr_Nr_ (Chr):
    """ Sort by chromosome """
    if Chr:
        #New = Chr[3:]
        if Chr == 'X': Chr = 23
        elif Chr == 'Y': Chr = 24
        elif Chr == 'M': Chr = 25
        elif Chr == 'MT': Chr = 25
        else: Chr = int(Chr)
    else:
        Chr = 0
    return Chr

def collect_chromosomes(df_altAF, add_all_string):
    myset = set(df_altAF["chr"])
    chr_list = list(myset)
    chr_list = sorted(chr_list, key=lambda x: Set_Chr_Nr_(x))
    
    if add_all_string:
        chr_list.insert(0, "all chromosomes")
    return chr_list

def get_cutoffs():
    df_cutoffs = pd.DataFrame()
    df_cutoffs.at[0,"roh_high_start"] = float(settings.roh_high_cutoff)
    df_cutoffs.at[0,"roh_high_end"] = float(10000)
    df_cutoffs.at[0,"roh_mixed_start"] = float(settings.roh_high_mixed_start)
    df_cutoffs.at[0,"roh_high_mixed_end"] = float(settings.roh_high_mixed_end)
    df_cutoffs.at[0,"inh_ratio_high_cutoff_start"] = float(settings.inh_ratio_high_trio_cutoff)
    df_cutoffs.at[0,"inh_ratio_high_cutoff_end"] = float(settings.inh_ratio_high_duo_cutoff)
    df_cutoffs.at[0,"inh_ratio_high_cutoff_end_duos"] = float(10000)

    return df_cutoffs

#@st.cache
def get_chromosome_lengths(df_vcf_variants):
    li_chr = []
    li_length=[]

    chr_list = set(list(df_vcf_variants["chr"]))

    for chr in chr_list:
        df = df_vcf_variants[df_vcf_variants["chr"] == chr]
        
        snvs_per_chr = df.shape[0]
        #if snvs_per_chr < settings.min_snvs_per_chr:
        #    chr_length = 0
        #else:
        first_variant = df.iloc[0]["start"]
        last_variant = df.iloc[-1]["start"]
        chr_length = last_variant-first_variant
        
        #if not "chr" in str(chr):
        #    chr = "chr"+str(chr)
 
        li_chr.append(chr)
        li_length.append(chr_length)

    df_chromosomes = pd.DataFrame()
    df_chromosomes["chr"] = li_chr
    df_chromosomes["length"] = li_length

    df_chromosomes = df_chromosomes.set_index('chr')

    return df_chromosomes

def create_overview(df_altAF, df_roh_rg):

    df_overview = pd.DataFrame()
    li_mat_over_pat = []
    li_pat_over_mat = []
    li_mat_over_notmat = []
    li_pat_over_notpat = []
    li_number_of_rohs = []
    li_total_lengths_of_rohs = []
    li_perc_covered_by_rohs = []

    chromosomes = collect_chromosomes(df_altAF, False)

    df_chromosomes = get_chromosome_lengths(df_altAF)

    for chromosome in chromosomes:

        # collect inheritance ratios per chromosome
        df_chr = df_altAF[df_altAF["chr"] == chromosome]

        mat_variants = df_chr[df_chr["snv_occurence"] == "maternal"].shape[0]
        pat_variants = df_chr[df_chr["snv_occurence"] == "paternal"].shape[0]
        notmat_variants = df_chr[df_chr["snv_occurence"] == "not maternal"].shape[0]
        notpat_variants = df_chr[df_chr["snv_occurence"] == "not paternal"].shape[0] 

        if (notmat_variants > 0) and (mat_variants > 0):
            mat_over_notmat = mat_variants / notmat_variants
        else:
            mat_over_notmat = 0
        if (notpat_variants > 0) and (pat_variants > 0):
            pat_over_notpat = pat_variants / notpat_variants
        else:
            pat_over_notpat = 0
        if (mat_variants>0) and (pat_variants>0):
            mat_over_pat = mat_variants / pat_variants
            pat_over_mat = pat_variants / mat_variants
        else:
            mat_over_pat = 0
            pat_over_mat = 0
        
        li_mat_over_pat.append(mat_over_pat)
        li_pat_over_mat.append(pat_over_mat)
        li_mat_over_notmat.append(mat_over_notmat)
        li_pat_over_notpat.append(pat_over_notpat)

        #collect roh sizes per chromosome

        df_roh_chr = df_roh_rg[df_roh_rg["chr"] == chromosome]
        
        li_number_of_rohs.append(df_roh_chr.shape[0])
        
        total_lengths_of_rohs = df_roh_chr["length"].sum()
        li_total_lengths_of_rohs.append(total_lengths_of_rohs)

        perc_covered_by_rohs = total_lengths_of_rohs / df_chromosomes.at[chromosome,"length"]

        li_perc_covered_by_rohs.append(perc_covered_by_rohs)

    df_overview["chr"] = chromosomes
    df_overview["mat_over_pat"] = li_mat_over_pat
    df_overview["mat_over_notmat"] = li_mat_over_notmat
    df_overview["pat_over_mat"] = li_pat_over_mat
    df_overview["pat_over_notpat"] = li_pat_over_notpat
    #df_overview["number_of_rohs"] = li_number_of_rohs
    #df_overview["total_lengths_of_rohs"] = li_total_lengths_of_rohs
    df_overview["perc_covered_by_rohs"] = li_perc_covered_by_rohs

    # remove data for X and Y chromosomes
    df_overview.at[22, "perc_covered_by_rohs"] = 0
    df_overview.at[23, "perc_covered_by_rohs"] = 0

    chr_to_drop = ["x", "X", "y", "Y", "M", "m", "MT", "mt"]
    df_overview = df_overview[~df_overview["chr"].isin(chr_to_drop)]

    return df_overview

def cleanup_overview(df_overview):
    cols = list(df_overview.columns)
    cols.remove("chr")
    cols.remove("upd_flagging")
    for col in cols:
        if df_overview[col].sum() == 0:
            df_overview = df_overview.drop(col, axis=1)
    cols = list(df_overview.columns)
    cols.remove("chr")
    cols.remove("upd_flagging")
    return df_overview, cols

def highlight_cells(val):
    color = 'darkred' if val != [] else 'white' # Pastel blue
    return 'background-color: {}'.format(color)

def roh_inh_scatter(df, df_cutoffs):
    li_chr=[]
    li_setup=[]
    li_setup_value=[]
    li_perc_roh=[]
    li_flag=[]
    inh_cols = list(df.columns)
    inh_cols.remove("chr")
    inh_cols.remove("perc_covered_by_rohs")
    inh_cols.remove("upd_flagging")
    # reformat df to make inh selectable
    for idx, row in df.iterrows():
        for col in inh_cols:
            li_chr.append(row["chr"])
            li_setup.append(col)
            li_setup_value.append(row[col])
            li_perc_roh.append(row["perc_covered_by_rohs"])
            li_flag.append(row["upd_flagging"])

    df_roh_inh = pd.DataFrame()
    df_roh_inh["chr"] = li_chr
    df_roh_inh["setup"] = li_setup
    df_roh_inh["setup_value"] = li_setup_value
    df_roh_inh["perc_covered_by_rohs"] = li_perc_roh
    df_roh_inh["upd_flagging"] = li_flag

    selection = alt.selection_multi(fields=['setup'], bind='legend')

    points = alt.Chart(df_roh_inh).mark_circle(size=120).encode(
        alt.X('perc_covered_by_rohs:Q', 
                title='perc_covered_by_rohs',
                scale=alt.Scale(domain=[0, 1],
                clamp=True,)
                ),
        alt.Y("setup_value:Q",
            title="inheritance ratio",
            scale=alt.Scale(domain=[0, 20],
            clamp=True)
            ),
        tooltip=["chr", "perc_covered_by_rohs", "upd_flagging"],
        color=alt.Color('setup:N',
                        legend=alt.Legend(
                        orient='none',
                        legendX=130, legendY=-70,
                        direction='horizontal',
                        titleAnchor='middle')
                        ),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.02))
    ).properties(
        width=600,
        height=600,
        title="Inheritance ratios"
    ).interactive(
    ).add_selection(
        selection
    )

    roh_high_rect = alt.Chart(df_cutoffs).mark_rect(opacity=0.1, color="orange").encode(
                x = "roh_high_start",
                x2 = "roh_high_end",
                y = alt.value(0),
                y2 = alt.value(10000)
            )
    roh_mixed_rect = alt.Chart(df_cutoffs).mark_rect(opacity=0.1, color="yellow").encode(
                    x = "roh_mixed_start",
                    x2 = "roh_high_mixed_end",
                    y = alt.value(0),
                    y2 = alt.value(10000)
                )
    inh_duo_rect = alt.Chart(df_cutoffs).mark_rect(opacity=0.1, color="yellow").encode(
                    x = alt.value(0),
                    x2 = alt.value(10000),
                    y = "inh_ratio_high_cutoff_start",
                    y2 = "inh_ratio_high_cutoff_end"
                )    
    inh_trio_rect = alt.Chart(df_cutoffs).mark_rect(opacity=0.1, color="orange").encode(
                    x = alt.value(0),
                    x2 = alt.value(10000),
                    y = "inh_ratio_high_cutoff_end",
                    y2 = "inh_ratio_high_cutoff_end_duos"
                )    

    plot = points + roh_high_rect + roh_mixed_rect + inh_duo_rect + inh_trio_rect

    return plot

def create_roh_plot(df, df_cutoffs, chr_list):
    #TODO: color by tag
    roh_plot = alt.Chart(df).mark_circle(size=120).encode(
        alt.X('chr:N', title='chromosome',
        sort=chr_list),
        alt.Y("perc_covered_by_rohs:Q",
            scale=alt.Scale(domain=[0, 1],
            clamp=True),
            title="percentage covered by rohs"),
        tooltip=["chr", "perc_covered_by_rohs", "upd_flagging"],
        color=alt.Color('upd_flagging:N',
                        legend=alt.Legend(
                        orient='none',
                        legendX=130, legendY=-70,
                        direction='horizontal',
                        titleAnchor='middle')
                        ),
    ).properties(
        width=600,
        height=600,
        title="ROHs per Chromosome"
    ).interactive(
    )

    roh_high_rect = alt.Chart(df_cutoffs).mark_rect(opacity=0.1, color="orange").encode(
            y = "roh_high_start",
            y2 = "roh_high_end"
        )
    roh_mixed_rect = alt.Chart(df_cutoffs).mark_rect(opacity=0.1, color="yellow").encode(
            #x = "roh_high_start",
            #x2 = "roh_high_end",
            y = "roh_mixed_start",
            y2 = "roh_high_mixed_end"
        )
    plot = roh_plot + roh_high_rect + roh_mixed_rect

    return plot


def flagging(df_overview, df_variants):
    li_tags = []
    li_con = []
    # cansanguinity flags
    consanguin = False
    df_roh_cut = df_overview[df_overview["perc_covered_by_rohs"] >= settings.consanguin_roh_cutoff]
    if df_roh_cut.shape[0] >= settings.consanguin_min_chr_count:
        consanguin = True
    
    # chr specific flags
    for idx, row in df_overview.iterrows():
        chr_tags = []

        # ROH
        # check for sufficient snvs
        snvs_per_chr = df_variants[df_variants["chr"] == row["chr"]].shape[0]
        if snvs_per_chr < settings.min_snvs_per_chr:
            chr_tags.append(settings.snv_per_chr_warning)
        else:
            if row["perc_covered_by_rohs"] >= settings.roh_high_cutoff:
                chr_tags.append(settings.roh_high_tag)
            if (row["perc_covered_by_rohs"] >= settings.roh_high_mixed_start) and (row["perc_covered_by_rohs"] <= settings.roh_high_mixed_end):
                chr_tags.append(settings.roh_high_mixed_tag)
        
        # Inheritance
        if row["mat_over_pat"] and row["pat_over_mat"]:
            if (row["mat_over_pat"] >= settings.inh_ratio_high_trio_cutoff) or (row["pat_over_mat"] >= settings.inh_ratio_high_trio_cutoff):
                chr_tags.append(settings.inh_ratio_high_tag)
        if row["mat_over_notmat"] or row["pat_over_notpat"]:
            if (row["mat_over_notmat"] >= settings.inh_ratio_high_duo_cutoff) or (row["pat_over_notpat"] >= settings.inh_ratio_high_duo_cutoff):
                chr_tags.append(settings.inh_ratio_high_tag)
        
        
        li_tags.append(chr_tags)

    df_overview["upd_flagging"] = li_tags

    #collect all flags set:
    li_collaps_tags=[]
    li_collaps_tags = [val for sublist in li_tags for val in sublist]
    li_collaps_tags = set(li_collaps_tags)
    return df_overview, consanguin, li_collaps_tags

def initialize_session_state():

    if "check_analyses" not in st.session_state:
        st.session_state["check_analyses"] = False
    if "cutoff_depth" not in st.session_state:
        st.session_state["cutoff_depth"] = 0
    if "cutoff_qual" not in st.session_state:
        st.session_state["cutoff_qual"] = 0
    if "df_altAF" not in st.session_state:
        st.session_state["df_altAF"] = pd.DataFrame()
    if "df_SNV" not in st.session_state:
        st.session_state["df_SNV"] = pd.DataFrame()
    if "df_sample_bin_stretches" not in st.session_state:
        st.session_state["df_sample_bin_stretches"] = pd.DataFrame()
    if "chr_sel_index" not in st.session_state:
        st.session_state["chr_sel_index"] = 0
    if "tmp_vcf" not in st.session_state:
        st.session_state["tmp_vcf"] = ""
    if "plot_vcf" not in st.session_state:
        st.session_state["plot_vcf"] = False
    if "vcf_dict" not in st.session_state:
        st.session_state["vcf_dict"] = {
            "index" : "",
            "mother" : "",
            "father" : "",
        }

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
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

@st.cache()
def detect_roh(vcf_file):

    cmd = ["bcftools roh --AF-dflt 0.4 -I " + vcf_file + " | awk '$1==\"RG\"{print $0}'"]
    bcf_roh_results = StringIO(subprocess.check_output(cmd, shell=True).decode('utf-8'))
    df_roh_rg = pd.read_csv(bcf_roh_results, sep="\t", names=["RG", "sample", "chr", "start", "end", "length", "number_of_markers", "quality"])

    df_roh_rg["chr"] = df_roh_rg["chr"].astype(str)
    df_roh_rg["chr"] = df_roh_rg["chr"].str.replace("chr", "")
    return df_roh_rg

@st.cache()
def create_vcf_tbi(vcf_file):
    try:
        cmd = ["tabix " + vcf_file]
        tabix_result = StringIO(subprocess.check_output(cmd, shell=True).decode('utf-8'))
    except:
        st.write("tabix failed")

@st.cache()
def save_temporary_file(vcf_file_in):
        with NamedTemporaryFile("wb", suffix=".vcf.gz", delete=False) as vcf_file:
            vcf_file.write(vcf_file_in.getvalue())
        create_vcf_tbi(vcf_file.name)
        return vcf_file.name

# =============================================================================
# web-GUI
# =============================================================================

st.set_page_config(
    page_title =            settings.main_page_config["page_title"], 
    page_icon =             settings.main_page_config["page_icon"], 
    layout =                settings.main_page_config["page_layout"], 
    initial_sidebar_state = settings.main_page_config["page_sidebar_state"], 
    menu_items =            settings.main_page_config["page_menu_items"]
)
# configure sidebar
st.sidebar.markdown(labels.sidebar_title)
st.sidebar.markdown(labels.sidebar_subtitle)
sidebar_legend = labels.sidebar_legend.format(
    consanguin_min_chr_count = settings.consanguin_min_chr_count,
    consanguin_roh_cutoff = int(settings.consanguin_roh_cutoff*100),
    inh_ratio_high_trio_cutoff = settings.inh_ratio_high_trio_cutoff,
    inh_ratio_high_duo_cutoff = settings.inh_ratio_high_duo_cutoff,
    roh_high_cutoff = int(settings.roh_high_cutoff*100),
    roh_high_mixed_start = int(settings.roh_high_mixed_start*100),
    roh_high_mixed_end = int(settings.roh_high_mixed_end*100),
    min_snvs_per_chr = settings.min_snvs_per_chr
)

st.sidebar.markdown(sidebar_legend)

# initialize session state
initialize_session_state()

### main page container to hold vcf input widgets
vcf_input_container = st.container()
with vcf_input_container.expander("select input options", expanded=True):
    tab_vcf, tab_batch = st.tabs(["vcf upload", "batch mode"])
with tab_batch:
    "coming soon..."
with tab_vcf:
    vcf_file_cols =  tab_vcf.columns([4,1,4,1,4])
    with vcf_file_cols[0]:
        st.write("Child vcf-file")
        vcf_file_index = st.file_uploader("upload .vcf file", type=[".vcf.gz"],accept_multiple_files=False, key="vcf_index")
        if vcf_file_index:
            from_vcf = True            
            vcf_dict["index"] = save_temporary_file(vcf_file_index)
            plot_vcf = st.button("plot vcf")
        else:
            st.warning("index vcf required")

    with vcf_file_cols[2]:
        st.write("Mother vcf-file")
        vcf_file_mother = st.file_uploader("upload .vcf file", type=[".vcf", ".vcf.gz"],accept_multiple_files=False, key="vcf_mother")
        if vcf_file_mother:
            vcf_dict["mother"] = save_temporary_file(vcf_file_mother)
            
    with vcf_file_cols[4]:
        st.write("Father vcf-file")
        vcf_file_father = st.file_uploader("upload .vcf file", type=[".vcf", ".vcf.gz"],accept_multiple_files=False, key="vcf_father")
        if vcf_file_father:    
            vcf_dict["father"] = save_temporary_file(vcf_file_father)

    # check for changes and reset session state
    if vcf_dict != st.session_state["vcf_dict"]:
        st.session_state["plot_vcf"] = False
        st.session_state["vcf_dict"] = vcf_dict
    else:
        st.session_state["vcf_dict"] = vcf_dict

if plot_vcf or st.session_state["plot_vcf"]:
    st.session_state["plot_vcf"] = True
    df_altAF = read_vcf_file(vcf_dict["index"])
    # get snv origin if at least one parent is given
    if (vcf_dict["index"] and vcf_dict["mother"]) or (vcf_dict["index"] and vcf_dict["father"]):
        df_snv_origin, domain_setting = collect_snv_inheritance(vcf_dict)
        
    if vcf_dict["index"] and not (vcf_dict["mother"] or vcf_dict["father"]):
        domain_setting = "single"

# if we have snv origins: merge with df_altAF 
if not df_snv_origin.empty:
    
    if "snv_occurence" in df_altAF.columns:
        df_altAF = df_altAF.drop(["snv_occurence"], axis = 1)
    df_altAF_origin = pd.merge(df_altAF, df_snv_origin, how="left", left_on=["chr", "start"], right_on=["chr", "pos"])
    df_altAF_origin.drop(["pos", "ref", "alt"], axis=1)
    
    df_altAF = df_altAF_origin
elif df_snv_origin.empty:
    df_altAF["snv_occurence"] = "index"


if not df_altAF.empty:
    # remove "chr" to make different versions work
    df_altAF["chr"] = df_altAF["chr"].str.replace("chr", "")
    # ROH detection
    df_roh_rg = detect_roh(vcf_dict["index"])

    # gather chromosome numbers for dropdown
    chr_list = collect_chromosomes(df_altAF, True)  
    
    # apply modification to copy of dataframe to keep cached values intact
    df_altAF_mod = pd.DataFrame()
    df_altAF_mod = df_altAF.copy()
    if df_snv_origin.empty:
        df_altAF_mod["snv_occurence"] = "unknown"
    
    # create overview table
    df_cutoffs = get_cutoffs()
    df_overview = create_overview(df_altAF, df_roh_rg)
    df_overview, consanguin, li_collaps_tags = flagging(df_overview, df_altAF_mod)
    df_overview, style_cols = cleanup_overview(df_overview)

    st.write("### Chromosome overview (excluding X,Y,M)")
    col_overview = st.columns([1,1,1])
    with col_overview[0]:
        
        if consanguin:
            st.warning(settings.consanguinity_warning)
        else:
            st.info(settings.no_consanguinity)
        if li_collaps_tags:
            st.warning("following UPD-flags have been raised: **" + str(li_collaps_tags) + "**")
        else:
            st.info("No UPD-flags have been raised.")

        st.dataframe(data=df_overview.style.background_gradient(cmap="OrRd", subset=style_cols) \
                                           .applymap(highlight_cells, subset=["upd_flagging"]),
                                    use_container_width=True)

        select_chr = st.selectbox("Select chromosome", chr_list, st.session_state["chr_sel_index"])
        
    with col_overview[1]:

        roh_plot = create_roh_plot(df_overview, df_cutoffs, chr_list)
        st.altair_chart(roh_plot)

    with col_overview[2]:

        if df_snv_origin.empty:
            st.warning("add parent vcfs for inheritance analysis (trio or duo)")
        else:
            inh_roh_plot = roh_inh_scatter(df_overview, df_cutoffs)
            st.altair_chart(inh_roh_plot)

    # initate graph plotter
    graph_plotter = graph_plotter(  df_altAF_mod,
                                    select_chr
                                    )

    if select_chr != "all chromosomes":
        df_plot = graph_plotter.set_and_filter_single_chr(select_chr)

        df_roh_rg_plot = df_roh_rg[df_roh_rg["chr"] == select_chr]
        st.altair_chart(graph_plotter.draw_chr_altair(df_plot, df_roh_rg_plot, select_chr, domain_setting, 1800, 800))
        st.write("RoH:")
        st.write(df_roh_rg_plot)

    if select_chr == "all chromosomes":

        # gather chromosome numbers for dropdown
        chr_list_plot = collect_chromosomes(df_altAF, False)
        li_chr = []
        li_mat_over_pat = []
        li_notmat_over_pat = []
        c = 1
        plots = []

        for chromosome in chr_list_plot:
            
            chr_str = chromosome
            df_plot = graph_plotter.set_and_filter_single_chr(chromosome)

            df_roh_rg_plot = df_roh_rg[df_roh_rg["chr"] == chromosome]

            if c == 1:
                plot = graph_plotter.draw_chr_altair(df_plot, df_roh_rg_plot, chromosome, domain_setting, 400, 200)
            elif c in [5, 9, 13, 17, 21, 24]:
                plots.append(plot)
                plot = graph_plotter.draw_chr_altair(df_plot, df_roh_rg_plot, chromosome, domain_setting, 400, 200)
            else:
                plot = alt.hconcat(plot, graph_plotter.draw_chr_altair(df_plot, df_roh_rg_plot, chromosome, domain_setting, 400, 200))
            c+=1

        for plot in plots:
            st.altair_chart(plot)

        # excel download button
        df_xlsx = to_excel(df_altAF)
        st.download_button(label='Download allele frequencies',
                                data=df_xlsx,
                                file_name= 'altAF.xlsx')
            
            