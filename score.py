
#differents functions in order to have our model scores


def score_ECG (M0_LVESV_3D,M0_LVED_3D,M0_LA_tot_EmF,M0_LA_strain_conduit) :
    return 2.628 + (0.035*M0_LVESV_3D) - (0.034*M0_LVED_3D) - (0.053*M0_LA_tot_EmF) - (0.261*M0_LA_strain_conduit)


def score_Clinical (GLYC, Urea) :
    return -68.028 + (3.126*GLYC) + (6.953*Urea)

def score_Metabolites (Arginine, Met_MetSufoxide, Kynurenine):
    return 36.33 - (3.79*Arginine) - (27.73*Met_MetSufoxide) + (3.60*Kynurenine)


def score_AF(age, lvef, sex, LA_d):
    return -11.896 + (0.092 * age) + (-0.040 * lvef) + (1.029 * sex) + (0.133 + LA_d)

def score_PAC (geat_volume_index, la_pls, geat_t1):
    return  11.886 + (-1.207 * geat_volume_index) + (-0.112 * la_pls) + (-0.056 * geat_t1)

def score_PSTAF (laa_emptying_flow_velocity, es_la_area, es_laav, laa_morphology):
    return -3.984 + (-0.114 * laa_emptying_flow_velocity) + (0.144 * es_la_area) + (0.101 * es_laav) + (0.424 * laa_morphology)