
# =============================================================================
# This version of the altAFplotter allow upload of 3 vcf files, runs a series 
# of analyses and displays the results of a UPD detection method
#
# =============================================================================

import pandas as pd
import streamlit as st
import altair as alt
import xlsxwriter
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb

from settings import settings, labels
from data_handling.graph_plotter import graph_plotter
from data_handling import \
    vcf_processing, \
    chromosome_handling, \
    general_plots, \
    general_functions

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

# =============================================================================
# web flow
# =============================================================================

# initialize session state
general_functions.initialize_session_state()

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
            vcf_dict["index"] = vcf_processing.save_temporary_file(vcf_file_index)
            plot_vcf = st.button("plot vcf")
        else:
            st.warning("index vcf required")

    with vcf_file_cols[2]:
        st.write("Mother vcf-file")
        vcf_file_mother = st.file_uploader("upload .vcf file", type=[".vcf", ".vcf.gz"],accept_multiple_files=False, key="vcf_mother")
        if vcf_file_mother:
            vcf_dict["mother"] = vcf_processing.save_temporary_file(vcf_file_mother)
            
    with vcf_file_cols[4]:
        st.write("Father vcf-file")
        vcf_file_father = st.file_uploader("upload .vcf file", type=[".vcf", ".vcf.gz"],accept_multiple_files=False, key="vcf_father")
        if vcf_file_father:    
            vcf_dict["father"] = vcf_processing.save_temporary_file(vcf_file_father)

    # check for changes and reset session state
    if vcf_dict != st.session_state["vcf_dict"]:
        st.session_state["plot_vcf"] = False
        st.session_state["vcf_dict"] = vcf_dict
    else:
        st.session_state["vcf_dict"] = vcf_dict

if plot_vcf or st.session_state["plot_vcf"]:
    st.session_state["plot_vcf"] = True
    df_altAF = vcf_processing.read_vcf_file(vcf_dict["index"])
    # get snv origin if at least one parent is given
    if (vcf_dict["index"] and vcf_dict["mother"]) or (vcf_dict["index"] and vcf_dict["father"]):
        df_snv_origin, domain_setting = vcf_processing.collect_snv_inheritance(vcf_dict)
        
    if vcf_dict["index"] and not (vcf_dict["mother"] or vcf_dict["father"]):
        domain_setting = "single"

# =============================================================================
# altAF processing and plotting
# =============================================================================
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
    df_roh_rg = vcf_processing.detect_roh(vcf_dict["index"])

    # gather chromosome numbers for dropdown
    chr_list = chromosome_handling.collect_chromosomes(df_altAF, True)  
    
    # apply modification to copy of dataframe to keep cached values intact
    df_altAF_mod = pd.DataFrame()
    df_altAF_mod = df_altAF.copy()
    if df_snv_origin.empty:
        df_altAF_mod["snv_occurence"] = "unknown"
    
    # create overview table
    df_cutoffs = chromosome_handling.get_cutoffs()
    df_overview = chromosome_handling.create_overview(df_altAF, df_roh_rg)
    df_overview, consanguin, li_collaps_tags = chromosome_handling.flagging(df_overview, df_altAF_mod)
    df_overview, style_cols = chromosome_handling.cleanup_overview(df_overview)

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
                                           .applymap(chromosome_handling.highlight_cells, subset=["upd_flagging"]),
                                    use_container_width=True)

        select_chr = st.selectbox("Select chromosome", chr_list, st.session_state["chr_sel_index"])
        
    with col_overview[1]:

        roh_plot = general_plots.create_roh_plot(df_overview, df_cutoffs, chr_list)
        st.altair_chart(roh_plot)

    with col_overview[2]:

        if df_snv_origin.empty:
            st.warning("add parent vcfs for inheritance analysis (trio or duo)")
        else:
            inh_roh_plot = general_plots.roh_inh_scatter(df_overview, df_cutoffs)
            st.altair_chart(inh_roh_plot)

    # initate graph plotter
    graph_plotter = graph_plotter(df_altAF_mod,
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
        chr_list_plot = chromosome_handling.collect_chromosomes(df_altAF, False)
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
        df_xlsx = general_functions.to_excel(df_altAF)
        st.download_button(label='Download allele frequencies',
                                data=df_xlsx,
                                file_name= 'altAF.xlsx')
      
    general_functions.delete_vcfs(vcf_dict)           