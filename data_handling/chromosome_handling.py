import pandas as pd
from settings import settings

def Set_Chr_Nr_ (Chr):
    """ Sort by chromosome """
    if Chr:
        #New = Chr[3:]
        if Chr == 'X': Chr = 23
        elif Chr == 'Y': Chr = 24
        elif Chr == 'M': Chr = 25
        elif Chr == 'MT': Chr = 25
        else: 
            try:
                Chr = int(Chr)
            except:
                pass
    else:
        Chr = 0
    return Chr

def collect_chromosomes(df_altAF, add_all_string):

    myset = set(df_altAF["chr"])
    chr_list = list(myset)

    # drop all non-standard contigs
    chr_list_clean = [a for a in chr_list if len(a) < 3]

    chr_list = sorted(chr_list_clean, key=lambda x: Set_Chr_Nr_(x))
    if add_all_string:
        chr_list.insert(0, "all chromosomes")
    return chr_list

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

    df_overview = pd.DataFrame(columns=[
        "chr",
        "mat_over_pat",
        "mat_over_notmat",
        "pat_over_mat",
        "pat_over_notpat",
        #"number_of_rohs",
        #"total_lengths_of_rohs",
        "perc_covered_by_rohs"
    ])

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
 
    df_overview = df_overview.fillna(0)

    return df_overview

def cleanup_overview(df_overview):

    cols = list(df_overview.columns)
    cols.remove("chr")
    cols.remove("upd_flagging")
    for col in cols:
        if df_overview[col].sum() == 0:
            if col in ["mat_over_pat", "mat_over_notmat", "pat_over_mat", "pat_over_notpat"]:
                df_overview = df_overview.drop(col, axis=1)
    cols = list(df_overview.columns)
    cols.remove("chr")
    cols.remove("upd_flagging")
    return df_overview, cols

def highlight_cells(val):
    color = 'darkred' if val != [] else 'white' # Pastel blue
    return 'background-color: {}'.format(color)

def highlight_ir_cells(val):
    color = 'white' # Pastel blue
    if val > settings.inh_ratio_high_duo_cutoff:
        color = 'yellow'
    if val > settings.inh_ratio_high_trio_cutoff:
        color = 'orange'
    if val < settings.inh_ratio_low_cutoff:
        color = 'lightblue'
    return 'background-color: {}'.format(color)

def highlight_roh_cells(val):
    color = 'white' # Pastel blue
    if val > settings.roh_high_mixed_start:
        color = 'yellow'
    if val > settings.roh_high_cutoff:
        color = 'orange'
    return 'background-color: {}'.format(color)

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