/**
 * CLINICAL QUESTIONNAIRE SCORING ENGINE
 * Evaluates every question and text response for all 9 roles.
 */
const QuestionnaireScorer = {

  scorePrincipalInvestigator(data) {
    let earned = 0;
    const total = 29;
    const yesFields = [
      'pi_clinical_research', 'pi_therapeutic_area', 'pi_subject_population', 'pi_test_article', 'pi_similar_studies',
      'sc_clinical_research', 'sc_therapeutic_area', 'sc_subject_population', 'sc_test_article', 'sc_similar_studies',
      'conduct_study', 'monitoring_visits', 'study_meetings', 'licensed_clinician', 'regulatory_inspection',
      'advertise_subjects', 'language_capability', 'additional_languages', 'additional_training',
      'annual_monitoring', 'adequate_workspace', 'medical_record_access', 'ich_gcp_training',
      'human_subject_training', 'nidcr_training', 'training_records', 'english_communication',
      'subject_literacy', 'community_support'
    ];

    yesFields.forEach(f => {
      if (data[f] === 'Yes' || data[f] === 'No') {
        if (f === 'additional_training' || f === 'regulatory_inspection') {
          if (data[f] === 'No') earned++;
        } else {
          if (data[f] === 'Yes') earned++;
        }
      }
    });

    return Number(((earned / total) * 100).toFixed(1));
  },

  scorePrimaryContact(data) {
    let earned = 0;
    const total = 6;
    if (data.q13_1 === 'Yes') earned++;
    if (data.q13_2 === 'Yes') earned++;
    if (data.q13_3 === 'Yes') earned++;
    if (data.q13_4 === 'No') earned++;
    if (data.q13_5 === 'Yes') earned++;
    if (data.q13_3_date && data.q13_3_date.length > 0) earned++;
    return Number(((earned / total) * 100).toFixed(1));
  },

  scoreStudyCoordinator(data) {
    let earned = 0;
    const total = 39;
    const fields = [
      'cr', 'ta', 'sp', 'tp', 'rs', 'cr1', 'ta1', 'sp1', 'tp1', 'rs1',
      'study', 'monitor', 'meeting', 'dentist', 'inspection', 'advertise', 'language_capability',
      'documents', 'screening_schedule', 'lab_access', 'equipment_available', 'central_lab',
      'iata', 'worked', 'local_lab', 'qualified', 'certification_local', 'normalrange',
      'research_storage', 'analysis_lab', 'staff_available', 'lab_review', 'lab_policy',
      'cert_international', 'quality_control', 'reference_values', 'lab_requirements',
      'q13_1', 'q13_2', 'q13_3', 'q13_5'
    ];

    fields.forEach(f => {
      if (data[f] === 'Yes') earned++;
      if ((f === 'obstacles' || f === 'training' || f === 'shipment' || f === 'q13_4') && data[f] === 'No') earned++;
    });

    return Number(((earned / total) * 100).toFixed(1));
  },

  scorePharmacist(data) {
    let earned = 0;
    const total = 14;
    ['adequate_storage', 'storage_requirements', 'transport_discussed', 'accountability_documentation',
     'ich_gcp_training', 'human_subjects_training', 'nidcr_training', 'training_records'].forEach(f => {
      if (data[f] === 'Yes' || data[f] === 'N/A') earned++;
    });

    if (data.additional_training_needed === 'No') earned++;
    if (data.storage_location && data.storage_location.length > 0) earned++;
    if (data.security_measures && data.security_measures.length > 5) earned++;
    if (data.storage_description && data.storage_description.length > 5) earned++;
    if (data.test_article_administrator && data.test_article_administrator.length > 2) earned++;
    if (data.training_date && data.training_date.length > 0) earned++;

    return Number(((earned / total) * 100).toFixed(1));
  },

  scoreTestArticleShipment(data) { return this.scoreFacilityBasedRole(data); },
  scoreAllOtherSupplies(data) { return this.scoreFacilityBasedRole(data); },

  scoreRegulatoryManager(data) {
    let earned = 0;
    const total = 8;
    if (data.fwa_status === 'Yes') earned++;
    if (data.irb_obstacles === 'No') earned++;
    if (data.add_committees === 'No') earned++;
    if (data.reg_files_resp && data.reg_files_resp.length > 2) earned++;
    if (data.irb_names && data.irb_names.length > 2) earned++;
    if (data.irb_meeting_freq && data.irb_meeting_freq.length > 2) earned++;
    if (data.irb_meeting_date && data.irb_meeting_date.length > 0) earned++;
    if (data.irb_approval_timeframe && data.irb_approval_timeframe.length > 1) earned++;
    return Number(((earned / total) * 100).toFixed(1));
  },

  scoreCentralUnitManager(data) { return this.scoreFacilityBasedRole(data); },

  scoreDataManager(data) {
    let earned = 0;
    const total = 16;
    ['part11_compliant', 'site_group', 'dcc', 'storage_facility_location', 'sae_system_exists',
     'q_training_gcp', 'q_training_hsp', 'q_training_nidcr', 'q_training_records_maintained'].forEach(f => {
      if (data[f] === 'Yes' || data[f] === 'NA') earned++;
    });

    if (data.offsite_longterm_storage === 'No') earned++;
    if (data.q_additional_training === 'No') earned++;
    if (data.data_collection_process && data.data_collection_process.length > 5) earned++;
    if (data.cdm_responsibility && data.cdm_responsibility.length > 2) earned++;
    if (data.analysis_responsibility && data.analysis_responsibility.length > 2) earned++;
    if (data.security_measures && data.security_measures.length > 5) earned++;
    if (data.ae_data_flow && data.ae_data_flow.length > 5) earned++;

    return Number(((earned / total) * 100).toFixed(1));
  },

  scoreFacilityBasedRole(data) {
    let earned = 0;
    const total = 20;
    ['room_space', 'emergency_equipment', 'clinical_equipment', 'data_space', 'telephone', 'fax', 'copier', 'internet',
     'cra_space', 'storage', 'cra_access', 'q13_1', 'q13_2', 'q13_3', 'q13_5'].forEach(f => {
      if (data[f] === 'Yes' || data[f] === 'NA') earned++;
    });

    if (data.paper_crf === 'No' || data.paper_crf === 'NA') earned++;
    if (data.q13_4 === 'No') earned++;
    if (data.emergency_plan_desc && data.emergency_plan_desc.length > 5) earned++;
    if (data.equipment_schedule_desc && data.equipment_schedule_desc.length > 5) earned++;
    if (data.source_doc_location && data.source_doc_location.length > 2) earned++;

    return Number(((earned / total) * 100).toFixed(1));
  },

  calculateScoreForRole(roleName, formData) {
    switch(roleName) {
      case 'Principal Investigator': return this.scorePrincipalInvestigator(formData);
      case 'Primary Contact for Site Communication': return this.scorePrimaryContact(formData);
      case 'Study Coordinator': return this.scoreStudyCoordinator(formData);
      case 'Pharmacist': return this.scorePharmacist(formData);
      case 'Test Article Shipment': return this.scoreTestArticleShipment(formData);
      case 'All Other Study Supplies': return this.scoreAllOtherSupplies(formData);
      case 'Regulatory Manager': return this.scoreRegulatoryManager(formData);
      case 'Central Unit Manager': return this.scoreCentralUnitManager(formData);
      case 'Data Manager': return this.scoreDataManager(formData);
      default: return 85.0;
    }
  }
};