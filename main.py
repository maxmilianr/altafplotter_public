import os
import json
import pandas as pd
import streamlit as st
import altair as alt
import xlsxwriter
from pyxlsb import open_workbook as open_xlsb

from data_handling.graph_plotter import graph_plotter
from settings import settings
from settings import labels

if not settings.toggle_public_version:
    from settings import credentials as cr
    from data_handling import \
        varvis_api, \
        gepado

from data_handling import \
    vcf_processing, \
    chromosome_handling, \
    general_plots, \
    general_functions

# =============================================================================
# define parameters
# =============================================================================
personID = ""
kit_selection = []
from_vcf = False
df_altAF = pd.DataFrame()
analyses_id = {
    "analysis_id_index" : "",
    "analysis_id_mother" : "",
    "analysis_id_father" : "",
    
}
df_snv_origin = pd.DataFrame()
df_roh_rg = pd.DataFrame()
vcf_file_index = ""
vcf_file_mother = ""
vcf_file_father = ""
get_varvis_vcf = False
plot_vcf = False
vcf_dict = {
        "index" : "",
        "mother" : "",
        "father" : "",
}
vcf_upload = {
    "index":"",
    "mother":"",
    "father":""
}
id_dict={
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
st.sidebar.markdown(labels.header_guideline)

legend_consanguinity = labels.legend_consanguinity.format(
    consanguin_min_chr_count = settings.consanguin_min_chr_count,
    consanguin_roh_cutoff = int(settings.consanguin_roh_cutoff*100),
)
legend_flag_settings = labels.legend_flag_settings.format(
    inh_ratio_high_trio_cutoff = settings.inh_ratio_high_trio_cutoff,
    inh_ratio_high_duo_cutoff = settings.inh_ratio_high_duo_cutoff,
    roh_high_cutoff = int(settings.roh_high_cutoff*100),
    roh_high_mixed_start = int(settings.roh_high_mixed_start*100),
    roh_high_mixed_end = int(settings.roh_high_mixed_end*100),
    min_snvs_per_chr = settings.min_snvs_per_chr
)

with st.sidebar.expander(labels.header_consanguinity):
    st.markdown(legend_consanguinity)
with st.sidebar.expander(labels.header_flagging):
    st.markdown(labels.legend_flagging)
with st.sidebar.expander(labels.header_flag_settings):
    st.markdown(legend_flag_settings)
with st.sidebar.expander(labels.header_legend):
    st.markdown(labels.yellow_squares)
    st.markdown(labels.purple_squares)
    st.code(labels.upd_regions)
with st.sidebar.expander(labels.header_requirements):
    st.markdown(labels.text_requirements)

with st.sidebar:
    st.markdown(labels.header_settings)
    assembly = st.selectbox(labels.select_assembly, settings.assemply_options)



# =============================================================================
# web flow
# =============================================================================

# initialize session state
general_functions.initialize_session_state()

if not settings.toggle_public_version:
    # collect person ID from URL params
    session_guid = gepado.get_url_param(cr.varvis_param)
    if not session_guid == "no person ID in params":
        # get person ID from Gepado
        id_dict["index"] = gepado.get_person_from_an_guid(cr.gep_db_server, cr.gep_db, cr.gep_user, cr.gep_password, session_guid)
        # primer go button to start execution with gepado person ID
        st.session_state["check_analyses"] = True
    else:
        id_dict["index"] = ""

### main page container to hold vcf input widgets
vcf_input_container = st.container()

with vcf_input_container.expander("select input options", expanded=True):
    if settings.toggle_public_version:
        tabs = settings.public_tabs
        vcf_tab = 0
        demo_tab = 1
    else: 
        tabs = settings.hug_tabs
        vcf_tab = 1
        demo_tab = 2

    input_tabs= st.tabs(tabs)
    
    if not settings.toggle_public_version:
        varvis_cols =  input_tabs[0].columns([6,1,6,1,6,10])
        with varvis_cols[0]:
            id_dict["index"] = st.text_input("Index ID", id_dict["index"]).replace(" ", "")
            if id_dict["index"]:
                check_analyses = True
            else:
                st.warning("index ID required")

        with varvis_cols[2]:
            id_dict["mother"] = st.text_input("mother ID", id_dict["mother"]).replace(" ", "")
        with varvis_cols[4]:
            id_dict["father"] = st.text_input("father ID", id_dict["father"]).replace(" ", "")

        if id_dict != st.session_state["id_dict"]:
            st.session_state["get_vcfs"] = False
            st.session_state["id_dict"] = id_dict
        else: 
            st.session_state["id_dict"] = id_dict

# =============================================================================
# Varvis setup
# =============================================================================
if not settings.toggle_public_version:
    if not st.session_state["session_id"]:
        st.session_state["session_id"] = varvis_api.varvis_api_login(cr.varvis_target, cr.varvis_user, cr.varvis_password)
    session_id = st.session_state["session_id"]

    if id_dict["index"]:
        response = varvis_api.get_analyses_per_person(id_dict["index"], session_id, cr.varvis_target)
        if response.status_code == 200:
            df_analyses = pd.DataFrame(json.loads(response.text))
            df_snvs_index = df_analyses.loc[df_analyses['analysisType'] == "SNV"]
        
            with varvis_cols[0]:
                kit_selection = st.selectbox("pick enrichment kit", df_snvs_index["enrichmentKitName"], index=0, key="index_kit")
                df_analysis = df_snvs_index.loc[df_snvs_index['enrichmentKitName'] == kit_selection] 
                analyses_id["analysis_id_index"] = str(df_analysis.iloc[0]["id"])
        else:
            st.warning("Error while obtaining analyses from varvis: " + str(response.status_code))
            st.stop()

    if id_dict["mother"]:
        response = varvis_api.get_analyses_per_person(id_dict["mother"], session_id, cr.varvis_target)
        if response.status_code == 200:
            df_analyses = pd.DataFrame(json.loads(response.text))
            df_snvs_mother = df_analyses.loc[df_analyses['analysisType'] == "SNV"]
        
            with varvis_cols[2]:
                kit_selection = st.selectbox("pick enrichment kit", df_snvs_mother["enrichmentKitName"], index=0, key="mother_kit")
                df_analysis = df_snvs_mother.loc[df_snvs_mother['enrichmentKitName'] == kit_selection] 
                analyses_id["analysis_id_mother"] = str(df_analysis.iloc[0]["id"])

        else:
            st.warning("Error while obtaining analyses from varvis: " + str(response.status_code))
            
            st.stop()  

    if id_dict["father"]:
        response = varvis_api.get_analyses_per_person(id_dict["father"], session_id, cr.varvis_target)
        if response.status_code == 200:
            df_analyses = pd.DataFrame(json.loads(response.text))
            df_snvs_father = df_analyses.loc[df_analyses['analysisType'] == "SNV"]
        
            with varvis_cols[4]:
                kit_selection = st.selectbox("pick enrichment kit", df_snvs_father["enrichmentKitName"], index=0, key="father_kit")
                df_analysis = df_snvs_father.loc[df_snvs_father['enrichmentKitName'] == kit_selection] 
                analyses_id["analysis_id_father"] = str(df_analysis.iloc[0]["id"])

        else:
            st.warning("Error while obtaining analyses from varvis: " + str(response.status_code))
            st.stop()  

    if "analysis_id_index" in analyses_id:
        if analyses_id["analysis_id_index"]:
            with varvis_cols[0]:
                get_varvis_vcf = st.button("get vcf")

    if get_varvis_vcf or st.session_state["get_vcfs"]:
        st.session_state["get_vcfs"] = True
        vcf_list = []

        if analyses_id["analysis_id_index"]:
            vcf_dict["index"] = varvis_api.download_vcf(analyses_id["analysis_id_index"], session_id, cr.varvis_target)

        if analyses_id["analysis_id_mother"]:
            vcf_dict["mother"] = varvis_api.download_vcf(analyses_id["analysis_id_mother"], session_id, cr.varvis_target)
        
        if analyses_id["analysis_id_father"]:
            vcf_dict["father"] = varvis_api.download_vcf(analyses_id["analysis_id_father"], session_id, cr.varvis_target)

        # get snv origin if at least one parent is given
        if (vcf_dict["index"] and vcf_dict["mother"]) or (vcf_dict["index"] and vcf_dict["father"]):
            df_snv_origin, domain_setting = vcf_processing.collect_snv_inheritance(vcf_dict)
        if vcf_dict["index"] and not (vcf_dict["mother"] or vcf_dict["father"]):
            domain_setting = "single"

        df_altAF = vcf_processing.read_vcf_file(vcf_dict["index"])


# =============================================================================
# vcf upload
# =============================================================================

with input_tabs[vcf_tab]:
    vcf_file_cols =  input_tabs[vcf_tab].columns([4,1,4,1,4])
    with vcf_file_cols[0]:
        st.write("Child vcf-file")
        vcf_upload["index"] = st.file_uploader("upload .vcf file", type=[".vcf.gz"],accept_multiple_files=False, key="vcf_index")
        if vcf_upload["index"]:
            from_vcf = True
            vcf_dict["index"] = vcf_processing.save_temporary_file(vcf_upload["index"])
            
            st.markdown("<div style='width: 1px; height: 28px'></div>", unsafe_allow_html=True)
            plot_vcf = st.button("plot vcf")
        else:
            st.warning("index vcf required")

    with vcf_file_cols[2]:
        st.write("Mother vcf-file")
        vcf_upload["mother"] = st.file_uploader("upload .vcf file", type=[".vcf", ".vcf.gz"],accept_multiple_files=False, key="vcf_mother")
        if vcf_upload["mother"]:
            vcf_dict["mother"] = vcf_processing.save_temporary_file(vcf_upload["mother"])
            
    with vcf_file_cols[4]:
        st.write("Father vcf-file")
        vcf_upload["father"] = st.file_uploader("upload .vcf file", type=[".vcf", ".vcf.gz"],accept_multiple_files=False, key="vcf_father")
        if vcf_upload["father"]:    
            vcf_dict["father"] = vcf_processing.save_temporary_file(vcf_upload["father"])

    # check for changes and reset session state
    if vcf_upload != st.session_state["vcf_upload"]:
        st.session_state["plot_vcf"] = False
        st.session_state["vcf_upload"] = vcf_upload
    else:
        st.session_state["vcf_upload"] = vcf_upload

if plot_vcf or st.session_state["plot_vcf"]:
    st.session_state["plot_vcf"] = True

    df_altAF = vcf_processing.read_vcf_file(vcf_dict["index"])

    # get snv origin if at least one parent is given
    if (vcf_dict["index"] and vcf_dict["mother"]) or (vcf_dict["index"] and vcf_dict["father"]):
        df_snv_origin, domain_setting = vcf_processing.collect_snv_inheritance(vcf_dict)
        
    if vcf_dict["index"] and not (vcf_dict["mother"] or vcf_dict["father"]):
        domain_setting = "single"

# =============================================================================
# demo
# =============================================================================
with input_tabs[demo_tab]:

    if st.button("Run Demo (hUPD8)") or st.session_state["bt_demo"]:
        st.session_state["bt_demo"] = True
        df_altAF = pd.read_csv(settings.demo_altaf)
        df_snv_origin = pd.read_csv(settings.demo_origin)
        df_roh_rg = pd.read_csv(settings.demo_roh)
        domain_setting = "trio"

    with open(settings.demo_vcf_file, 'rb') as f:
        st.download_button('Download sample vcf', f, file_name='HG001_GRCh38_1_22_v4.2.1_exome.vcf.gz')
        st.caption("this sample vcf file is a subset of [HG001](https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/NA12878_HG001/latest/GRCh38/HG001_GRCh38_1_22_v4.2.1_benchmark.vcf.gz) and can be used as a formatting reference")

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

    # remove "chr" to make different sources work together
    df_altAF["chr"] = df_altAF["chr"].str.replace("chr", "")

    # ROH detection
    if df_roh_rg.empty:
        df_roh_rg = vcf_processing.detect_roh(vcf_dict["index"])
        if df_roh_rg.empty:
            st.error("unable to process vcf file with bcftools roh, please check your file or [inform us.](https://github.com/HUGLeipzig/altafplotter/issues)")

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
        
        df_overview_flagged = df_overview[df_overview["upd_flagging"].str.len() != 0]
        upd_summary_list = []


        for idx, row in df_overview_flagged.iterrows():
            flags_txt = row['upd_flagging']
            # translate flags
            
            translate_flags = {
                "roh_high"          : "increased runs of homozygosity",
                "roh_high_mixed"    : "increased runs of homozygosity",
                "inh_ratio_high"    : "increased inheritance ratio",
                "insufficient_snvs" : "insufficient snvs"
            }

            flags_txt_translated = set([translate_flags[x] for x in flags_txt])

            upd_summary_list.append(f"chr{row['chr']}: `{','.join(flags_txt_translated)}`")


        upd_flag_summary = "**UPD-flag summary**\n\n"
        if consanguin:
            upd_flag_summary += settings.consanguinity_warning
        else:
            upd_flag_summary += settings.no_consanguinity

        if len(upd_summary_list) != 0:
            upd_flag_summary += "\n\n".join(upd_summary_list)

            st.warning(upd_flag_summary)
        else:
            upd_flag_summary += "no UPD flags raised"
            st.success(upd_flag_summary)
            
            
        styled_df = df_overview.style.applymap(
                chromosome_handling.highlight_cells, subset=["upd_flagging"]
                )
        

        ir_columns = [x for x in styled_df.columns if "_over_" in x]
        if "mat_over_notmat" in ir_columns or "pat_over_notpat" in ir_columns:
            # duo setup
            styled_df = styled_df.applymap(
                    chromosome_handling.highlight_ir_cells_duo, subset=ir_columns
                    )
        elif "mat_over_pat" in ir_columns:
            styled_df = styled_df.applymap(
                    chromosome_handling.highlight_ir_cells_trio, subset=ir_columns
                    )

        styled_df = styled_df.applymap(
                chromosome_handling.highlight_roh_cells, subset=["perc_covered_by_rohs"]
                )

        st.dataframe(
            data = styled_df,
            use_container_width=True,
            hide_index=True
        )

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
    graph_plotter = graph_plotter(  df_altAF_mod,
                                    select_chr
                                    )

    if select_chr != "all chromosomes":
        df_plot = graph_plotter.set_and_filter_single_chr(select_chr)

        df_roh_rg_plot = df_roh_rg[df_roh_rg["chr"] == select_chr]
        st.altair_chart(
            graph_plotter.draw_chr_altair(
                df_plot,
                df_roh_rg_plot,
                select_chr,
                domain_setting,
                1800,
                800,
                assembly
            )
        )
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
                plot = graph_plotter.draw_chr_altair(
                    df_plot,
                    df_roh_rg_plot,
                    chromosome,
                    domain_setting,
                    400,
                    200,
                    assembly
                )
            elif c in [5, 9, 13, 17, 21, 24]:
                plots.append(plot)
                plot = graph_plotter.draw_chr_altair(
                    df_plot,
                    df_roh_rg_plot,
                    chromosome,
                    domain_setting,
                    400,
                    200,
                    assembly
                )
            else:
                plot = alt.hconcat(
                    plot,
                    graph_plotter.draw_chr_altair(
                        df_plot,
                        df_roh_rg_plot,
                        chromosome,
                        domain_setting,
                        400,
                        200,
                        assembly
                    )
                )
            c+=1

        for plot in plots:
            st.altair_chart(plot)

        # excel download button
        df_xlsx = general_functions.to_excel(df_altAF)
        st.download_button(label='Download allele frequencies',
                                data=df_xlsx,
                                file_name= 'altAF.xlsx')

    if settings.toggle_public_version:
        general_functions.delete_vcfs(vcf_dict)

