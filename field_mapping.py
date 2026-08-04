def get_field_mapping(role_name):

    if role_name == "Principal Investigator":

        return {
            "location_name": 8,
    "study_location": 9,
    "inpatient_description": 10,
    "other_location": 11,
    "therapeutic_specialties": 12,

    "pi_clinical_research": 13,
    "pi_clinical_research_count": 14,

    "pi_therapeutic_area": 15,
    "pi_therapeutic_area_count": 16,

    "pi_subject_population": 17,
    "pi_subject_population_count": 18,

    "pi_test_article": 19,
    "pi_test_article_count": 20,

    "pi_similar_studies": 21,
    "pi_similar_studies_count": 22,

    "sc_clinical_research": 23,
    "sc_clinical_research_count": 24,

    "sc_therapeutic_area": 25,
    "sc_therapeutic_area_count": 26,

    "sc_subject_population": 27,
    "sc_subject_population_count": 28,

    "sc_test_article": 29,
    "sc_test_article_count": 30,

    "sc_similar_studies": 31,
    "sc_similar_studies_count": 32,

    "enrollment_percentage": 33,
    "enrollment_reason": 34,

    "open_enrolling": 35,
    "follow_up_phase": 36,

    "conduct_study": 37,
    "monitoring_visits": 38,
    "study_meetings": 39,

    "licensed_clinician": 40,

    "regulatory_inspection": 41,
    "inspection_date": 42,
    "agency_name": 43,
    "inspected_person": 44,

    # ---------- Section 2 ----------
    "advertise_subjects": 45,

    "language1": 46,
    "language1_general": 47,
    "language1_target": 48,

    "language2": 49,
    "language2_general": 50,
    "language2_target": 51,

    "language3": 52,
    "language3_general": 53,
    "language3_target": 54,

    "language_capability": 55,

    "additional_languages": 56,

    "translation_method": 57,

    "enrollment_obstacles": 58,
    "obstacle_description": 59,

    "screening_schedule": 60,

    # ---------- Section 3 ----------
    "additional_training": 61,

    "study_objectives": 62,
    "inclusion_exclusion": 63,
    "study_procedures": 64,
    "participant_followup": 65,
    "laboratory_procedures": 66,
    "specimen_shipping": 67,
    "ae_reporting": 68,
    "staff_responsibilities": 69,
    "protocol_compliance": 70,

    # ---------- Section 4 ----------
    "annual_monitoring": 71,
    "adequate_workspace": 72,
    "medical_record_access": 73,

    "source_documents": 74,
    "source_document_other": 75,

    # ---------- Section 5 ----------
    "ich_gcp_training": 76,
    "human_subject_training": 77,
    "nidcr_training": 78,

    "training_method": 79,
    "training_date": 80,

    "additional_training_needed": 81,
    "training_needs": 82,

    "training_records": 83,

    # ---------- Section 6 ----------
    "english_communication": 84,
    "communication_method": 85,

    "crf_language": 86,
    "source_language": 87,
    "regulatory_language": 88,

    "english_consent": 89,
    "consent_language": 90,

    "consent_process": 91,

    "subject_literacy": 92,
    "literacy_procedure": 93,

    "local_customs": 94,
    "custom_description": 95,

    "community_board": 96,
    "community_support": 97,
    "community_leader_support":98,
    "community_engagement": 99,

    "country_requirements": 100,
    "country_requirement_description": 101
        }


    elif role_name == "Primary Contact For Site Communication":

        return {

            "contact_name":1,
            "contact_phone":2,
            "contact_email":3,

            "training_na": 4,
            "q13_1": 5,
            "q13_2": 6,
            "q13_3": 7,
            "q13_3_method": 8,
            "q13_3_date": 9,
            "q13_4": 10,
            "q13_4_needs": 11,
            "q13_5": 12
        }


    elif role_name == "Study Coordinator":

        return {

            # --- Section 1 ---
            "location_name": 1,
            "location_type": 2, 
            "inpatient_description": 3,
            "other_location_desc": 4,
            "therapeutic_specialties": 5,
            
            # PI Experience
            "cr": 6, "pi_cr_num": 7,
            "ta": 8, "pi_ta_num": 9,
            "sp": 10, "pi_sp_num": 11,
            "tp": 12, "pi_tp_num": 13,
            "rs": 14, "pi_rs_num": 15,
            
            # SC Experience
            "cr1": 16, "sc_cr_num": 17,
            "ta1": 18, "sc_ta_num": 19,
            "sp1": 20, "sc_sp_num": 21,
            "tp1": 22, "sc_tp_num": 23,
            "rs1": 24, "sc_rs_num": 25,
            
            "goals_na": 26,
            "goals_percentage": 27,
            "goals_explanation": 28,
            
            "studies_na": 29,
            "open_enrolling": 30,
            "follow_up": 31,
            
            "study": 32,
            "monitor": 33,
            "meeting": 34,
            "dentist": 35,
            
            "inspection": 36,
            "inspection_date": 37,
            "agency_name": 38,
            "inspected_who": 39,

            # --- Section 2 ---
            "advertise": 40,
            
            "lang_a": 41, "lang_a_gen": 42, "lang_a_tar": 43,
            "lang_b": 44, "lang_b_gen": 45, "lang_b_tar": 46,
            "lang_c": 47, "lang_c_gen": 48, "lang_c_tar": 49,
            
            "language_capability": 50,
            "documents": 51,
            "translation_desc": 52,
            
            "obstacles": 53,
            "obstacles_desc": 54,
            "screening_schedule": 55,

            # --- Section 3 ---
            "training": 56,
            "a": 57, "b": 58, "c": 59, "d": 60, "e": 61,
            "f": 62, "g": 63, "h": 64, "i": 65,

            # --- Section 4 ---
            "lab_na": 66,
            "lab_access": 67,
            "equipment_available": 68,
            "specimen_processing": 69,
            "specimen_collection": 70,
            
            "transfer_clinical": 71,
            "transfer_research": 72,
            
            "central_lab": 73,
            "central_lab_name": 74,
            "central_lab_purpose": 75,
            "iata": 76,
            "shipment": 77,
            "shipment_barriers": 78,
            "worked": 79,
            
            "local_lab": 80,
            "local_lab_name": 81,
            "qualified": 82,
            "certification_local": 83,
            "normalrange": 84,
            
            "research_storage": 85,
            "storage_lab_name": 86,
            "storage_lab_location": 87,
            "storage_equipment": 88,
            "storage_contact": 89,
            
            "analysis_lab": 90,
            "analysis_lab_name": 91,
            "analysis_lab_location": 92,
            "analysis_tests": 93,
            "staff_available": 94,
            "analysis_contact": 95,
            "lab_review": 96,
            "lab_policy": 97,
            "temp_method": 98,
            
            "q10_na": 99,
            "cert_international": 100,
            "cert_text": 101,
            "quality_control": 102,
            "reference_values": 103,
            "lab_requirements": 104,

            # --- Section 5 ---
            "training_na_sec5": 105,
            "q13_1": 106,
            "q13_2": 107,
            "q13_3": 108,
            "q13_3_method": 109,
            "q13_3_date": 110,
            "q13_4": 111,
            "q13_4_needs": 112,
            "q13_5": 113
        
        }


    elif role_name == "Pharmacist":

        return {

              "study_product_na": 1,

            "adequate_storage": 2,

            "storage_location[]": 3,

            "storage_location_other": 3,

            "security_measures": 4,

            "storage_requirements": 5,

            "storage_description": 5,

            "offsite_transport_procedure": 6,

            "transport_discussed": 7,

            "accountability_documentation": 8,

            "test_article_administrator": 9,

            # -------------------------
            # Section 2
            # -------------------------

            "training_na": 10,

            "ich_gcp_training": 10,

            "human_subjects_training": 11,

            "nidcr_training": 12,

            "training_method[]": 13,

            "training_date": 14,

            "additional_training_needed": 15,

            "training_needs": 16,

            "training_records": 17

           
        }


    elif role_name == "Test Article Shipment":

        return {

           "facility_na": 1,
            "room_space": 2,
            "emergency_equipment": 3,
            "emergency_plan_desc": 4,
            "clinical_equipment": 5,
            "equipment_schedule_desc": 6,
            "data_space": 7,
            "telephone": 8,
            "fax": 9,
            "copier": 10,
            "internet": 11,
            "cra_space": 12,
            "storage": 13,
            "source_doc_location": 14,
            "paper_crf_location": 15,
            "source_type": 16,
            "cra_access": 17,
            "paper_crf": 18,
            "paper_crf_transport_desc": 19,
            "training_na": 20,
            "q13_1": 21,
            "q13_2": 22,
            "q13_3": 23,
            "q13_3_method": 24,
            "q13_3_date": 25,
            "q13_4": 26,
            "q13_4_needs": 27,
            "q13_5": 28
        }


    elif role_name == "All Other Regulatory Supplies":

        return {

            "facility_na": 1,
            "room_space": 2,
            "emergency_equipment": 3,
            "emergency_plan_desc": 4,
            "clinical_equipment": 5,
            "equipment_schedule_desc": 6,
            "data_space": 7,
            "telephone": 8,
            "fax": 9,
            "copier": 10,
            "internet": 11,
            "cra_space": 12,
            "storage": 13,
            "source_doc_location": 14,
            "paper_crf_location": 15,
            "source_type": 16,
            "cra_access": 17,
            "paper_crf": 18,
            "paper_crf_transport_desc": 19,
            "training_na": 20,
            "q13_1": 21,
            "q13_2": 22,
            "q13_3": 23,
            "q13_3_method": 24,
            "q13_3_date": 25,
            "q13_4": 26,
            "q13_4_needs": 27,
            "q13_5": 28
        }


    elif role_name == "Regulatory Manager":

        return {

            "irb_na": 1,
            "reg_files_resp": 2,
            "irb_names": 3,
            "irb_meeting_freq": 4,
            "irb_meeting_date": 5,
            "irb_approval_timeframe": 6,
            "irb_obstacles": 7,
            "irb_obstacles_desc": 8,
            "add_committees": 9,
            "add_committees_desc": 10,
            "add_committees_order_flag": 11,
            "add_committees_order_desc": 12,
            "fwa_status": 13
        }


    elif role_name == "Central Unit Manager":

        return {
                
            "site_na": 1,
            "site_mgmt_resp": 2,
            "qmp": 3,
            "qmp_implemented": 4,
            "qmp_copy_nidcr": 5,
            "qmp_review_date": 6,
            "qmp_resp_person": 7,
            "qm_perform": 8,
            "qm_process_desc": 9,
            "communication_methods_desc": 10,
            "training_na": 11,
            "q13_1": 12,
            "q13_2": 13,
            "q13_3": 14,
            "q13_3_method": 15,
            "q13_3_date": 16,
            "q13_4": 17,
            "q13_4_needs": 18,
            "q13_5": 19,
            "international_na": 20,
            "q14_1": 21,
            "q14_1_desc": 22,
            "q14_2_crf_lang": 23,
            "q14_2_crf_lang_other": 24,
            "q14_2_source_lang": 25,
            "q14_2_source_lang_other": 26,
            "q14_2_reg_lang": 27,
            "q14_2_reg_lang_other": 28,
            "q14_3": 29,
            "q14_3_lang": 30,
            "q14_4_process_desc": 31,
            "q14_5": 32,
            "q14_5_literacy_proc": 33,
            "q14_6": 34,
            "q14_6_customs_desc": 35,
            "q14_7": 36,
            "q14_8": 37,
            "q14_9_engagement_desc": 38,
            "q14_10": 39,
            "q14_10_difficulties_desc": 40
        
    
            
          }


    elif role_name == "Data Manager":

        return {

            # --- Site Information (sites table) ---
    # --- Section 1: Data Management ---
            "lab_na": 1,
            "data_collection_process": 2,
            "part11_compliant": 3,
            "cdm_responsibility": 4,
            "analysis_responsibility": 5,
            "site_group": 6,
            "dcc": 7,
            "dcc_name": 8,
            "records": 9,
            "electronic_records_desc": 10,
            "paper_records_available": 11,
            "security_measures": 12,
            "storage_facility_location": 13,
            "source_docs": 14,
            "source_docs_other_spec": 15,
            "ae_data_flow": 16,
            "sae_system_exists": 17,
            "sae_chain_of_events": 18,
            "sae_resp_primary": 19,
            "sae_resp_secondary": 20,
            "sae_reconciliation": 21,
            "offsite_longterm_storage": 22,
            "offsite_storage_review_proc": 23,

            # --- Section 2: Training ---
            "training_na": 24,
            "q_training_gcp": 25,
            "q_training_hsp": 26,
            "q_training_nidcr": 27,
            "nidcr_training_method": 28,
            "nidcr_training_date": 29,
            "q_additional_training": 30,
            "additional_training_needs": 31,
            "q_training_records_maintained": 32
        }

    return {}