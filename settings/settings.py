
# streamlit page config
main_page_config = {
    "page_title" :          "altAF-plotter",
    "page_icon" :           "🦔",
    "page_layout" :         "wide",
    "page_sidebar_state" :  "auto",
    "page_menu_items" : {
        "Get help":     "https://www.ecosia.org/",
        "Report a Bug": "https://www.ecosia.org/",
        "About" :       None
    }
}

# domain setting for altair

dict_domain = {
    "single" : ["unknown"],
    "trio" : ['biparental', 'de novo', 'maternal', 'paternal', 'unknown'],
    "duo_mat" : ['unknown', 'not maternal', 'maternal'],
    "duo_pat" : ['unknown', 'not paternal', 'paternal']
}
dict_range = {
    "single" : ["blue"],
    "trio" : ['blue', 'orange', 'red', 'green', 'grey'],
    "duo_mat" : ['grey', 'orange', 'red'],
    "duo_pat" : ['grey', 'orange', 'green']
    
}

#inheritance dicts
inheritance_dict_trio = {
                "001"   :   "unknown",
                "010"   :   "unknown",
                "011"   :   "unknown",
                "100"   :   "de novo",
                "101"   :   "paternal",
                "110"   :   "maternal",
                "111"   :   "biparental",
            }
inheritance_dict_duo_mother = {
                "00"   :   "unknown",
                "01"   :   "unknown",
                "10"   :   "not maternal",
                "11"   :   "maternal",
            }
inheritance_dict_duo_father = {
                "00"   :   "unknown",
                "01"   :   "unknown",
                "10"   :   "not paternal",
                "11"   :   "paternal",
            }


# flagging cutoffs:
roh_high_cutoff = 0.7
roh_high_mixed_start = 0.2
roh_high_mixed_end = 0.7

inh_ratio_high_trio_cutoff = 2
inh_ratio_high_duo_cutoff = 5

consanguin_min_chr_count = 3
consanguin_roh_cutoff = 0.1

min_snvs_per_chr = 200

# flags
roh_high_tag = "roh_high"
roh_high_mixed_tag = "roh_high_mixed"
inh_ratio_high_tag = "inh_ratio_high"
consanguin_tag = "likely_consanguineous"
not_consanguin_tag = "unlikely_consanguineous"
snv_per_chr_warning = "insufficient_snvs"

consanguinity_warning = "Consanguinity likely, handle potential UPD flags with extra care."
no_consanguinity = "Consanguinity unlikely"

