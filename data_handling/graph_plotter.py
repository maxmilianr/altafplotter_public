
from numpy import int64
import requests
import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt
import sys
import pymssql

from settings import settings


class graph_plotter:

    def __init__(   self,
                    df_altAF_mod,
                    select_chr,
                ):
        self.df_altAF_mod = df_altAF_mod
        self.select_chr = select_chr,

    def set_and_filter_single_chr(self, select_chr):

       # select data for chosen chromosome
        df_plot = pd.DataFrame()
        df_plot["chromosome_position"] = self.df_altAF_mod[self.df_altAF_mod["chr"]==select_chr]["start"]
        df_plot["altAF"] = self.df_altAF_mod[self.df_altAF_mod["chr"]==select_chr]["altAF"]
        df_plot["reads"] = self.df_altAF_mod[self.df_altAF_mod["chr"]==select_chr]["reads"]
        df_plot["quality"] = self.df_altAF_mod[self.df_altAF_mod["chr"]==select_chr]["quality"]
        df_plot["snv_occurence"] = self.df_altAF_mod[self.df_altAF_mod["chr"]==select_chr]["snv_occurence"]
      
        return df_plot

    def draw_chr_altair(self, df_plot, df_roh_rg, chromosome, domain_setting, w, h, assembly):
        
        selection = alt.selection_multi(fields=['snv_occurence'], bind='legend', toggle="true")

        scatter = alt.Chart(df_plot).mark_circle(size=60).encode(
            x = 'chromosome_position',
            y = 'altAF',
            color = alt.Color(
                'snv_occurence',
                scale=alt.Scale(
                domain=settings.dict_domain[domain_setting],
                range=settings.dict_range[domain_setting])),
            opacity=alt.condition(selection, alt.value(0.4), alt.value(0.02)),
            tooltip=['altAF', 'snv_occurence', 'chromosome_position']
        ).properties(
            width = w, height = h,
            title=chromosome
        ).interactive(  
        ).add_selection(
            selection
        )

        plot = scatter

        if not df_roh_rg.empty:        

            var_rect = alt.Chart(df_roh_rg).mark_rect(opacity=0.3, color="orange").encode(
                x = "start",
                x2 = "end",
                y = alt.value(0),
                y2 = alt.value(1000)
            )
            plot = plot+var_rect
        
        plot = plot + read_and_plot_upd_regions(assembly, chromosome)
        
        return plot


    def set_and_filter_all_chr(self):

       # select data for chosen chromosome
        df_plot = pd.DataFrame()
        df_plot["chr"] = self.df_altAF_mod["chr"]
        df_plot["chromosome_position"] = self.df_altAF_mod["start"]
        df_plot["altAF"] = self.df_altAF_mod["altAF"]
        df_plot["reads"] = self.df_altAF_mod["reads"]
        df_plot["quality"] = self.df_altAF_mod["quality"]
        df_plot["snv_occurence"] = self.df_altAF_mod["snv_occurence"]
      
        return df_plot

@st.cache_data
def read_upd_regions(assembly):
    # add UPD region rectangle
    with open(settings.upd_region_file) as f:
        upd_regions = json.load(f)
    
    df_region = pd.DataFrame(
        {
            "region"    : [x["name"] for x in upd_regions],
            "chr"       : [x["coordinates"][assembly]["chromosome"] for x in upd_regions],
            "start"     : [x["coordinates"][assembly]["start"] for x in upd_regions],
            "end"       : [x["coordinates"][assembly]["end"] for x in upd_regions]
        }
    )
    return df_region


def read_and_plot_upd_regions(assembly, chromosome):
    # add UPD region rectangle
    with open(settings.upd_region_file) as f:
        upd_regions = json.load(f)
    
    df_region = read_upd_regions(assembly)

    df_region = df_region[df_region["chr"] == chromosome]

    upd_region_rect = alt.Chart(df_region).mark_rect(opacity=0.3, color="purple").encode(
            x = "start",
            x2 = "end",
            y = alt.value(0),
            y2 = alt.value(1000)
        )
    
    return upd_region_rect