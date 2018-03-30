import pandas as pd
import numpy as np
import os

def get_tables(table):
# read in redcap
    RC = pd.read_csv(os.environ.get(table),low_memory=False,sep="\t")
    RCinstr = redcap_instruments(RC)

    # read in labels of RC
    text_file = open(os.path.join(os.environ.get("CODEDIR"),"postbids/notebooks/utils/neuropsych_labels.txt"),'r')
    lines = text_file.read().split("\n")

    labeltable = pd.DataFrame([RC.columns,lines])
    labeltable = labeltable.transpose()
    labeltable.columns = ['code','label']
    for idx,row in labeltable.iterrows():
        scale = [k for k,v in RCinstr.iteritems() if row.code in v]
        if len(scale)==0:
            scale = ''
        else:
            scale = scale[0]
        labeltable = labeltable.set_value(idx,"scale",scale)
    return RC, labeltable

def subset_tables(table=None,include=None,RC=None, labeltable=None):
    if (RC is None and labeltable is None):
        RC, labeltable = get_tables(table)

    if include == None:
        include = [
            'legal_issues',
            'wasi',
            'bprse',
            'hamd',
            'ymrs',
            'ldps',
            'family_history_assessment',
            'ctq',
            # 'thq',
            'scid',
            'scid_face'
            ]

    # function get_measures_subset gets all non-text questions of the questionnaire
    # (without 'has this instr been collected' and 'iscomplete')
    neuropsych_cols = get_measures_subset(include=include)
    lbl_id = np.sort([np.where(x==labeltable.code)[0][0] for x in neuropsych_cols])

    #subset labeltable
    labeltable = labeltable.iloc[lbl_id]
    print("There are %i variables considered."%len(labeltable))

    #subset subjectstable and standardise
    FA_table = RC[labeltable.code]
    FA_table = FA_table.replace("n/a",np.nan)
    FA_table = FA_table.astype('float')
    FA_table = (FA_table - FA_table.mean()) / (FA_table.max() - FA_table.min())
    FA_table = FA_table.fillna(0)

    return labeltable, FA_table


def clean_tables(labeltable, FA_table,cor_lim):
    # append Nan columns
    dropvars = []
    for column in FA_table:
        FAnan = np.sum(FA_table[column]==0)
        if FAnan==len(FA_table):
            dropvars.append(column)

    # drop variables with too high correlations
    cormat = FA_table.corr()
    idx = np.where(cormat > cor_lim)
    collin = [[x,y] for x,y in zip(idx[0],idx[1]) if x!=y and np.sort([x,y]).tolist()==[x,y]]
    for pair in collin:
        x = pair[0]
        y = pair[1]
        print("Correlation between %s and %s: %f"%(list(FA_table)[x],list(FA_table)[y],np.array(cormat)[x,y]))
        vardrop = list(FA_table)[y]
        dropvars.append(vardrop)

    labeltable = labeltable.reset_index()
    delvar = [np.where(x==labeltable.code)[0][0] for x in dropvars]
    labeltable.drop(delvar,inplace=True)

    FA_table = FA_table[labeltable.code]
    FA_table = (FA_table - FA_table.mean()) / (FA_table.max() - FA_table.min())
    FA_table = FA_table.fillna(0)

    return labeltable, FA_table


def redcap_instruments(RC):
    print("    ...getting redcap instruments...")
    # extract and organise redcap variables
    RC_instruments = {
        "subject_status": RC.columns.values[:12].tolist(),
        "health_screening": RC.columns.values[12:130].tolist(),
        "legal_issues": RC.columns.values[130:203].tolist(),
        "wasi_2scale": RC.columns.values[203:211].tolist(),
        "bprse": RC.columns.values[211:238].tolist(),
        "hamd": RC.columns.values[238:263].tolist(),
        "ymrs": RC.columns.values[263:277].tolist(),
        "ldps_c26a": RC.columns.values[277:346].tolist(),
        "family_history_assessment": RC.columns.values[346:624].tolist(),
        "ctq": RC.columns.values[624:654].tolist(),
        'THQ': RC.columns.values[654:746].tolist(),
        "mri": RC.columns.values[746:777].tolist(),
        "scid": RC.columns.values[777:803].tolist(),
        "scid_face_page": RC.columns.values[803:825].tolist(),
        "scid_axis_diagnosis": RC.columns.values[825:848].tolist()
    }
    return RC_instruments

def get_measures_subset(include=None):
    if not include:
        include = [
            'legal_issues',
            'wasi', #IQ
            'bprse', #brief psychiatric rating scale expanded
            'hamd', #hamilton depression scale
            'ymrs', #young mania rating scale
            'ldps', #lifetime dimensions of psychosis scale
            'family_history_assessment',
            'ctq', #childhood trauma questionnaire
            # 'thq', #traima history questionnaire
            'scid', # structured clinical interview for DSM-5
            'scid_face'
            ]

    cols = []

    if 'legal_issues' in include:
        cols += ['suspended',
         'ticketed',
         'expelled',
         'alternative_school',
         'have_you_ever_been_arreste',
         'violent_crime',
         'property',
         'sexual_offense',
         'drug_law',
         'traffic_law',
         'weapons_law_violation',
         'other_crimes',
         'were_you_first_seen_by_a_m',
         'was_it_while_you_were_in_c',
         'convictions',
         'misdemeanor',
         'felony',
         'have_you_ever_been_incarce',
         'what_type_of_facility___1',
         'what_type_of_facility___2',
         'what_type_of_facility___3',
         'what_type_of_facility___4',
         'have_you_been_on_probation',
         'probation_has_it_been_succesfully_co',
         'have_you_been_on_parole',
         'has_parole_been_successful']

    # wasi
    if 'wasi' in include:
        cols += ['matrix_reasoning_t_score','vocabulary_t_score']

    # bprse
    if 'bprse' in include:
        cols +=  ['somatic_concerns',
         'anxiety',
         'depression',
         'guilt',
         'hostility',
         'suspiciousness',
         'unusual_thought_content',
         'grandiosity',
         'hallucinations',
         'disorientation',
         'conceptual_disorganization',
         'excitement',
         'motor_retardation',
         'blunted_affect',
         'tension',
         'mannerisms_and_posturing',
         'uncooperativeness',
         'emotional_withdrawal',
         'suicidality',
         'self_neglect',
         'bizarre_behaviors',
         'elevated_mood',
         'motor_hyperactivity',
         'distractability']

    if 'hamd' in include:
        cols += ['depressed_mood',
         'feelings_of_guilt',
         'suicide',
         'insomnia_early',
         'insomnia_middle',
         'insomnia_late',
         'work_and_activities',
         'retardation_psychomotor',
         'agitation',
         'anxiety_psychological',
         'anxiety_somatic',
         'somatic_symtpoms_gastroint',
         'somatic_symptoms_general',
         'genital_symptoms',
         'hypochondriasis',
         'loss_of_weight',
         'hamd_insight',
         'diurnal_variation_a_marked',
         'diurnal_variation_part_b_s',
         'depersonalization',
         'paranoid_symptoms',
         'obsessional_and_compulsive']

    if 'ymrs' in include:
        cols += ['ymrs_elevated_mood',
         'increased_motor_activity_e',
         'sexual_interest',
         'sleep',
         'irritability',
         'speech',
         'language_thought_disorder',
         'content',
         'disruptive_aggressive_beha',
         'appearance',
         'insight']

    if 'ldps' in include:
        cols += ['p1___1',
         'p1___2',
         'p1___3',
         'p1___4',
         'p1___5',
         'p1___6',
         'p1___7',
         'duration_p1',
         'severity_p1',
         'duration_p2',
         'severity_p2',
         'duration_p3',
         'severity_p3',
         's1___1',
         's1___2',
         's1___3',
         'duration_s1',
         'severity_s1',
         'duration_s2',
         'severity_s2',
         's3___1',
         's3___2',
         's3___3',
         'duration_s3',
         'severity_s3',
         's4___1',
         's4___2',
         's4___3',
         'duration_s4',
         'severity_s4',
         'nap___1',
         'nap___2',
         'nap___3',
         'duration_nap',
         'severity_nap',
         'duration_n1',
         'severity_b1',
         'duration_n2',
         'severity_n2',
         'duration_d1',
         'severity_d1',
         'duration_d2',
         'severity_d2',
         'duration_de1',
         'severity_de1',
         'duration_m1',
         'severity_m1',
         'mp1___1',
         'mp1___catastrophe',
         'mp1___2',
         'mp1___3',
         'duration_mp1',
         'severity_mp1',
         'mp2___1',
         'mp2___2',
         'duration_mp2',
         'severity_mp2',
         'severity_c',
         'a___1',
         'a___2',
         'a___3',
         'a___4',
         'a___5',
         'severity_a',
         'quality',
        ]

    if 'family_history_assessment' in include:
        cols += ['alcohol_use_family___1',
         'alcohol_use_family___2',
         'alcohol_use_family___3',
         'alcohol_use_family___4',
         'alcohol_use_family___5',
         'alcohol_use_family___6',
         'alcohol_use_family___7',
         'alcohol_use_family___8',
         'alcohol_use_family___9',
         'alcohol_use_family___10',
         'alcohol_use_family___11',
         'alcohol_use_family___12',
         'alcohol_use_family___13',
         'alcohol_use_family___14',
         'alcohol_use_family___15',
         'alcohol_use_family___16',
         'alcohol_use_family___17',
         'alcohol_use_family___18',
         'alcohol_use_family___19',
         'alcohol_use_family___20',
         'alcohol_use_family___21',
         'alcohol_use_family___22',
         'alcohol_use_family___23',
         'drug_use_family___1',
         'drug_use_family___2',
         'drug_use_family___3',
         'drug_use_family___4',
         'drug_use_family___5',
         'drug_use_family___6',
         'drug_use_family___7',
         'drug_use_family___8',
         'drug_use_family___9',
         'drug_use_family___10',
         'drug_use_family___11',
         'drug_use_family___12',
         'drug_use_family___13',
         'drug_use_family___14',
         'drug_use_family___15',
         'drug_use_family___16',
         'drug_use_family___17',
         'drug_use_family___18',
         'drug_use_family___19',
         'drug_use_family___20',
         'drug_use_family___21',
         'drug_use_family___22',
         'drug_use_family___23',
         'depression_family___1',
         'depression_family___2',
         'depression_family___3',
         'depression_family___4',
         'depression_family___5',
         'depression_family___6',
         'depression_family___7',
         'depression_family___8',
         'depression_family___9',
         'depression_family___10',
         'depression_family___11',
         'depression_family___12',
         'depression_family___13',
         'depression_family___14',
         'depression_family___15',
         'depression_family___16',
         'depression_family___17',
         'depression_family___18',
         'depression_family___19',
         'depression_family___20',
         'depression_family___21',
         'depression_family___22',
         'depression_family___23',
         'mania_family___1',
         'mania_family___2',
         'mania_family___3',
         'mania_family___4',
         'mania_family___5',
         'mania_family___6',
         'mania_family___7',
         'mania_family___8',
         'mania_family___9',
         'mania_family___10',
         'mania_family___11',
         'mania_family___12',
         'mania_family___13',
         'mania_family___14',
         'mania_family___15',
         'mania_family___16',
         'mania_family___17',
         'mania_family___18',
         'mania_family___19',
         'mania_family___20',
         'mania_family___21',
         'mania_family___22',
         'mania_family___23',
         'schizophrenia_family___1',
         'schizophrenia_family___2',
         'schizophrenia_family___3',
         'schizophrenia_family___4',
         'schizophrenia_family___5',
         'schizophrenia_family___6',
         'schizophrenia_family___7',
         'schizophrenia_family___8',
         'schizophrenia_family___9',
         'schizophrenia_family___10',
         'schizophrenia_family___11',
         'schizophrenia_family___12',
         'schizophrenia_family___13',
         'schizophrenia_family___14',
         'schizophrenia_family___15',
         'schizophrenia_family___16',
         'schizophrenia_family___17',
         'schizophrenia_family___18',
         'schizophrenia_family___19',
         'schizophrenia_family___20',
         'schizophrenia_family___21',
         'schizophrenia_family___22',
         'schizophrenia_family___23',
         'antisocial_personality_fam___1',
         'antisocial_personality_fam___2',
         'antisocial_personality_fam___3',
         'antisocial_personality_fam___4',
         'antisocial_personality_fam___5',
         'antisocial_personality_fam___6',
         'antisocial_personality_fam___7',
         'antisocial_personality_fam___8',
         'antisocial_personality_fam___9',
         'antisocial_personality_fam___10',
         'antisocial_personality_fam___11',
         'antisocial_personality_fam___12',
         'antisocial_personality_fam___13',
         'antisocial_personality_fam___14',
         'antisocial_personality_fam___15',
         'antisocial_personality_fam___16',
         'antisocial_personality_fam___17',
         'antisocial_personality_fam___18',
         'antisocial_personality_fam___19',
         'antisocial_personality_fam___20',
         'antisocial_personality_fam___21',
         'antisocial_personality_fam___22',
         'antisocial_personality_fam___23',
         'anxiety_family___1',
         'anxiety_family___2',
         'anxiety_family___3',
         'anxiety_family___4',
         'anxiety_family___5',
         'anxiety_family___6',
         'anxiety_family___7',
         'anxiety_family___8',
         'anxiety_family___9',
         'anxiety_family___10',
         'anxiety_family___11',
         'anxiety_family___12',
         'anxiety_family___13',
         'anxiety_family___14',
         'anxiety_family___15',
         'anxiety_family___16',
         'anxiety_family___17',
         'anxiety_family___18',
         'anxiety_family___19',
         'anxiety_family___20',
         'anxiety_family___21',
         'anxiety_family___22',
         'anxiety_family___23',
         'mental_health_care_family___1',
         'mental_health_care_family___2',
         'mental_health_care_family___3',
         'mental_health_care_family___4',
         'mental_health_care_family___5',
         'mental_health_care_family___6',
         'mental_health_care_family___7',
         'mental_health_care_family___8',
         'mental_health_care_family___9',
         'mental_health_care_family___10',
         'mental_health_care_family___11',
         'mental_health_care_family___12',
         'mental_health_care_family___13',
         'mental_health_care_family___14',
         'mental_health_care_family___15',
         'mental_health_care_family___16',
         'mental_health_care_family___17',
         'mental_health_care_family___18',
         'mental_health_care_family___19',
         'mental_health_care_family___20',
         'mental_health_care_family___21',
         'mental_health_care_family___22',
         'mental_health_care_family___23',
         'psychiatric_hospitalizatio___1',
         'psychiatric_hospitalizatio___2',
         'psychiatric_hospitalizatio___3',
         'psychiatric_hospitalizatio___4',
         'psychiatric_hospitalizatio___5',
         'psychiatric_hospitalizatio___6',
         'psychiatric_hospitalizatio___7',
         'psychiatric_hospitalizatio___8',
         'psychiatric_hospitalizatio___9',
         'psychiatric_hospitalizatio___10',
         'psychiatric_hospitalizatio___11',
         'psychiatric_hospitalizatio___12',
         'psychiatric_hospitalizatio___13',
         'psychiatric_hospitalizatio___14',
         'psychiatric_hospitalizatio___15',
         'psychiatric_hospitalizatio___16',
         'psychiatric_hospitalizatio___17',
         'psychiatric_hospitalizatio___18',
         'psychiatric_hospitalizatio___19',
         'psychiatric_hospitalizatio___20',
         'psychiatric_hospitalizatio___21',
         'psychiatric_hospitalizatio___22',
         'psychiatric_hospitalizatio___23',
         'suicide_attempt_family___1',
         'suicide_attempt_family___2',
         'suicide_attempt_family___3',
         'suicide_attempt_family___4',
         'suicide_attempt_family___5',
         'suicide_attempt_family___6',
         'suicide_attempt_family___7',
         'suicide_attempt_family___8',
         'suicide_attempt_family___9',
         'suicide_attempt_family___10',
         'suicide_attempt_family___11',
         'suicide_attempt_family___12',
         'suicide_attempt_family___13',
         'suicide_attempt_family___14',
         'suicide_attempt_family___15',
         'suicide_attempt_family___16',
         'suicide_attempt_family___17',
         'suicide_attempt_family___18',
         'suicide_attempt_family___19',
         'suicide_attempt_family___20',
         'suicide_attempt_family___21',
         'suicide_attempt_family___22',
         'suicide_attempt_family___23',
         'suicide_complete_family___1',
         'suicide_complete_family___2',
         'suicide_complete_family___3',
         'suicide_complete_family___4',
         'suicide_complete_family___5',
         'suicide_complete_family___6',
         'suicide_complete_family___7',
         'suicide_complete_family___8',
         'suicide_complete_family___9',
         'suicide_complete_family___10',
         'suicide_complete_family___11',
         'suicide_complete_family___12',
         'suicide_complete_family___13',
         'suicide_complete_family___14',
         'suicide_complete_family___15',
         'suicide_complete_family___16',
         'suicide_complete_family___17',
         'suicide_complete_family___18',
         'suicide_complete_family___19',
         'suicide_complete_family___20',
         'suicide_complete_family___21',
         'suicide_complete_family___22',
         'suicide_complete_family___23',
         'tabacco_family___1',
         'tabacco_family___2',
         'tabacco_family___3',
         'tabacco_family___4',
         'tabacco_family___5',
         'tabacco_family___6',
         'tabacco_family___7',
         'tabacco_family___8',
         'tabacco_family___9',
         'tabacco_family___10',
         'tabacco_family___11',
         'tabacco_family___12',
         'tabacco_family___13',
         'tabacco_family___14',
         'tabacco_family___15',
         'tabacco_family___16',
         'tabacco_family___17',
         'tabacco_family___18',
         'tabacco_family___19',
         'tabacco_family___20',
         'tabacco_family___21',
         'tabacco_family___22',
         'tabacco_family___23']

    if 'ctq' in include:
        cols += ['i_didn_t_have_enough_to_ea',
         'i_knew_there_was_someone_t',
         'peopel_in_my_family_called',
         'my_parents_were_too_drunk',
         'there_was_someone_in_my_fa',
         'i_had_to_wear_dirty_clothe',
         'i_felt_loved',
         'i_thought_my_parents_wishe',
         'i_got_hit_so_hard_by_someo',
         'there_was_nothing_i_wanted',
         'people_in_my_family_hit_me',
         'i_was_punished_with_a_belt',
         'people_in_my_family_looked',
         'people_in_my_family_said_h',
         'i_believe_that_i_was_physi',
         'i_had_the_perfect_childhoo',
         'i_got_hit_or_beaten_so_bad',
         'i_felt_that_someone_in_my',
         'people_in_my_family_felt_c',
         'someone_tried_to_touch_me',
         'someone_threatened_to_hurt',
         'i_had_the_best_family_in_t',
         'someone_tried_to_make_me_d',
         'someone_molested_me',
         'i_believe_i_was_emotionall',
         'there_was_someone_to_take',
         'i_believe_i_was_sexually_a',
         'my_family_was_a_source_of',
        ]

    if 'thq' in include:
        cols += [
         'has_anyone_ever_tried_to_t',
         'cre_q2_has_anyone_ever_att',
         'cre_q3_has_anyone_ever_att',
         'cre_q4_has_anyone_ever_att',
         'gd_q5_have_you_ever_had_a',
         'gd_q6_have_you_ever_experi',
         'gd_q7_have_you_ever_experi',
         'gd_q8_have_you_ever_been_e',
         'gd_q9_have_you_ever_been_i',
         'gd_q10_have_you_ever_been',
         'gd_q11_have_you_ever_seen',
         'qd_q12_have_you_ever_seen',
         'gd_q13_have_you_ever_had_a',
         'gd_q14_have_you_ever_had_a',
         'gd_q15_have_you_ever_had_a',
         'gd_q16_have_you_ever_recei',
         'gd_q17_have_you_ever_had_t',
         'pse_q18_has_anyone_ever_ma',
         'pse_q19_has_anyone_ever_to',
         'pse_q20_other_than_inciden',
         'pse_q21_has_anyone_includi',
         'pse_q22_has_anyone_includi',
         'pse_q23_has_anyone_in_your',
         'pse_q24_have_you_experienc']

    if 'scid' in include:
        cols += ['have_you_ever_had_a_panic',
         'were_you_ever_afraid_of_go',
         'is_there_anything_that_you',
         'are_there_any_other_things',
         'have_you_been_bothered_by',
         'ocd',
         'over_the_last_six_months_h',
         'has_there_been_any_time_in',
         'have_you_ever_used_street',
         'have_you_ever_gotten_hooke',
         'have_you_ever_had_a_time_w',
         'have_you_often_had_times_w',
         'depression1',
         'depression2',
         'scid_suicide',
         'mania1',
         'mania2',
         'have_you_ever_heard_things',
         'has_it_ever_seemed_like_yo',
         'have_you_ever_experienced',
         'over_the_years_have_you_of',
         'do_you_worry_much_about_yo',
         'have_you_been_very_bothere',
         'do_you_have_any_concerns_r']

    if 'scid_face' in include:
        cols += ['sex',
         'age',
         'has_there_ever_been_a_prio',
         'have_you_been_in_any_kind',
         'have_you_ever_been_a_patie',
         'have_you_ever_been_in_a_ho',
         'any_problems_this_past_mon']

    return cols
