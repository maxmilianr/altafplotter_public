
import altair as alt
import pandas as pd


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