import { Component, signal, computed, OnInit, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import * as d3 from 'd3';

// ─── Interfaces ───────────────────────────────────────────────────────────────

interface Treatment {
  id: string;
  name: string;
  type: 'pill' | 'therapy' | 'procedure' | 'vaccine' | 'gene-therapy';
  targetDisease: string;
  mechanism: string;
  stage: 'research' | 'clinical-trial' | 'approved' | 'conceptual';
  efficacy: string;
  timeline: string;
  description: string;
  molecularTarget: string;
  sideEffects: string[];
  pharmacokinetics: {
    absorption: string;
    distribution: string;
    metabolism: string;
    elimination: string;
    halfLife: string;
    bioavailability: string;
  };
  clinicalTrials: {
    phase: string;
    enrollment: number;
    primaryEndpoint: string;
    result: string;
  }[];
}

interface DiseaseCategory {
  id: string;
  name: string;
  icon: string;
  diseases: string[];
  description: string;
  globalBurden: { deaths_per_year: string; prevalence: string; economic_cost: string };
}

interface DrugMechanism {
  id: string;
  name: string;
  category: 'targeted' | 'immunotherapy' | 'gene-therapy' | 'vaccine' | 'small-molecule';
  pathway: string;
  targetProtein: string;
  description: string;
  steps: string[];
  molecularStructure: string;
}

interface MonteCarloTrialResult {
  scenario: string;
  trials: number;
  median_survival_months: number;
  survival_std: number;
  response_rate: number;
  complete_remission: number;
  progression_free_survival: number;
  description: string;
}

interface TechnicalDerivation {
  id: string;
  title: string;
  category: 'pharmacokinetics' | 'immunology' | 'genomics' | 'drug-design' | 'clinical-stats';
  equations: {
    name: string;
    latex: string;
    description: string;
    variables: { symbol: string; meaning: string; unit: string }[];
    derivation?: string[];
    numericalExample?: { inputs: Record<string, number | string>; calculation: string; result: string };
  }[];
}

interface SignalProcessingBlock {
  name: string;
  function: string;
  inputs: string[];
  outputs: string[];
  algorithm: string;
  pseudocode: string[];
}

interface ResearchArea {
  name: string;
  focus: string;
  breakthroughs: string[];
  potential: string;
}

interface ClinicalPipelinePhase {
  name: string;
  duration: string;
  cost: string;
  successRate: string;
  description: string;
  requirements: string[];
}

interface ManufacturingStep {
  id: string;
  name: string;
  phase: 'manufacturing' | 'quality' | 'regulatory' | 'distribution' | 'pharmacy';
  duration: string;
  cost: string;
  description: string;
  requirements: string[];
  qualityChecks: string[];
  output: string;
  personnel: string[];
  equipment: string[];
}

type DrugCategoryId = 'checkpoint' | 'car-t' | 'adc' | 'mrna' | 'crispr' | 'tki';

// ─── Component ────────────────────────────────────────────────────────────────

@Component({
  selector: 'app-disease-cure',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './disease-cure.component.html',
  styleUrl: './disease-cure.component.scss'
})
export class DiseaseCureComponent implements OnInit, AfterViewInit {
  @ViewChild('efficacyChart') efficacyChart!: ElementRef;
  @ViewChild('survivalCurveChart') survivalCurveChart!: ElementRef;
  @ViewChild('pipelineChart') pipelineChart!: ElementRef;
  @ViewChild('monteCarloChart') monteCarloChart!: ElementRef;
  @ViewChild('mechanismFlowChart') mechanismFlowChart!: ElementRef;
  @ViewChild('diseaseBurdenChart') diseaseBurdenChart!: ElementRef;

  readonly Math = Math;
  readonly Object = Object;

  activeCategory = signal<string>('cancer');
  activeTreatment = signal<string | null>(null);
  selectedDrugCategory = signal<DrugCategoryId>('checkpoint');
  showEquations = signal(false);
  activeDerivationSection = signal<string>('pharmacokinetics');
  activeProcessingStep = signal<number>(0);
  showResearch = signal(false);

  // ─── Disease Categories ───────────────────────────────────────────────

  diseaseCategories = signal<DiseaseCategory[]>([
    {
      id: 'cancer',
      name: 'Cancer',
      icon: '&#129516;',
      diseases: ['Lung Cancer', 'Breast Cancer', 'Colorectal Cancer', 'Pancreatic Cancer', 'Leukemia', 'Melanoma', 'Prostate Cancer', 'Liver Cancer'],
      description: 'Revolutionary approaches to oncology including targeted therapies, immunotherapy, and precision medicine. Cancer accounts for approximately 1 in 6 deaths worldwide.',
      globalBurden: { deaths_per_year: '10 million', prevalence: '19.3 million new cases/year', economic_cost: '$1.16 trillion/year' }
    },
    {
      id: 'cardiovascular',
      name: 'Cardiovascular',
      icon: '&#129729;',
      diseases: ['Heart Disease', 'Stroke', 'Hypertension', 'Arrhythmia', 'Heart Failure', 'Atherosclerosis'],
      description: 'Advanced treatments for heart and circulatory system disorders. Leading cause of death globally.',
      globalBurden: { deaths_per_year: '17.9 million', prevalence: '523 million cases', economic_cost: '$863 billion/year' }
    },
    {
      id: 'neurological',
      name: 'Neurological',
      icon: '&#129504;',
      diseases: ['Alzheimer\'s', 'Parkinson\'s', 'Multiple Sclerosis', 'ALS', 'Epilepsy', 'Huntington\'s'],
      description: 'Breakthrough therapies for neurodegenerative and neurological conditions. The blood-brain barrier makes these among the hardest diseases to treat.',
      globalBurden: { deaths_per_year: '9 million', prevalence: '3 billion affected', economic_cost: '$789 billion/year' }
    },
    {
      id: 'infectious',
      name: 'Infectious Diseases',
      icon: '&#129440;',
      diseases: ['HIV/AIDS', 'Tuberculosis', 'Malaria', 'Hepatitis', 'COVID-19', 'Antimicrobial Resistance'],
      description: 'Vaccines, antivirals, and novel antimicrobial treatments. Infectious diseases remain the leading killer in low-income countries.',
      globalBurden: { deaths_per_year: '13.7 million', prevalence: 'Billions affected', economic_cost: '$3.5 trillion/year' }
    },
    {
      id: 'autoimmune',
      name: 'Autoimmune',
      icon: '&#128170;',
      diseases: ['Rheumatoid Arthritis', 'Lupus', 'Crohn\'s Disease', 'Type 1 Diabetes', 'Psoriasis', 'Celiac Disease'],
      description: 'Immunomodulatory therapies and targeted biologics for diseases where the immune system attacks the body\'s own tissues.',
      globalBurden: { deaths_per_year: '780,000', prevalence: '800 million affected', economic_cost: '$100 billion/year' }
    },
    {
      id: 'rare',
      name: 'Rare Diseases',
      icon: '&#128300;',
      diseases: ['Cystic Fibrosis', 'Sickle Cell', 'Muscular Dystrophy', 'Hemophilia', 'Spinal Muscular Atrophy', 'Gaucher Disease'],
      description: 'Gene therapies and orphan drug development. Over 7,000 rare diseases affect 300 million people worldwide, 95% have no approved treatment.',
      globalBurden: { deaths_per_year: '3.5 million', prevalence: '300 million affected', economic_cost: '$966 billion/year' }
    }
  ]);

  // ─── Comprehensive Treatment Data ─────────────────────────────────────

  treatments = signal<Treatment[]>([
    {
      id: 'checkpoint',
      name: 'Checkpoint Inhibitors (Pembrolizumab/Nivolumab)',
      type: 'therapy',
      targetDisease: 'Melanoma, Lung Cancer, Renal Cell Carcinoma',
      mechanism: 'Block PD-1/PD-L1 interaction, restoring T-cell anti-tumor activity',
      stage: 'approved',
      efficacy: '20-45% overall response rate; 15-20% durable complete response',
      timeline: 'Available now (FDA approved 2014+)',
      description: 'PD-1/PD-L1 checkpoint inhibitors remove the "brakes" on T-cells, allowing the immune system to recognize and destroy cancer. Pembrolizumab (Keytruda) has become the world\'s best-selling drug, approved for 30+ tumor types.',
      molecularTarget: 'PD-1 receptor on T-cells / PD-L1 on tumor cells',
      sideEffects: ['Immune-related adverse events (irAEs)', 'Pneumonitis (3-5%)', 'Colitis (1-3%)', 'Hepatitis (1-2%)', 'Thyroiditis (5-10%)', 'Fatigue (20-30%)'],
      pharmacokinetics: {
        absorption: 'IV infusion (100% bioavailability)',
        distribution: 'Vd = 6.0-7.2 L (primarily vascular)',
        metabolism: 'Proteolytic degradation (not hepatic CYP)',
        elimination: 'Target-mediated drug disposition (TMDD)',
        halfLife: '22-25 days (pembrolizumab), 25-27 days (nivolumab)',
        bioavailability: '100% (IV)'
      },
      clinicalTrials: [
        { phase: 'KEYNOTE-001', enrollment: 1235, primaryEndpoint: 'Objective Response Rate', result: '33% ORR in melanoma, 19.4% in NSCLC' },
        { phase: 'KEYNOTE-024', enrollment: 305, primaryEndpoint: 'Progression-Free Survival', result: '10.3 vs 6.0 months (HR 0.50)' },
        { phase: 'KEYNOTE-042', enrollment: 1274, primaryEndpoint: 'Overall Survival', result: '16.7 vs 12.1 months in PD-L1 ≥1%' },
        { phase: 'CheckMate-067', enrollment: 945, primaryEndpoint: '5-Year Overall Survival', result: '52% (nivo+ipi) vs 44% (nivo) vs 26% (ipi)' }
      ]
    },
    {
      id: 'car-t',
      name: 'CAR-T Cell Therapy (Tisagenlecleucel/Axicabtagene)',
      type: 'gene-therapy',
      targetDisease: 'B-cell ALL, DLBCL, Follicular Lymphoma, Multiple Myeloma',
      mechanism: 'Autologous T-cells engineered with chimeric antigen receptor targeting CD19/BCMA',
      stage: 'approved',
      efficacy: '40-54% complete remission in DLBCL; 81% remission in pediatric ALL',
      timeline: 'Available now (FDA approved 2017+)',
      description: 'CAR-T therapy represents a paradigm shift — the patient\'s own T-cells are extracted, genetically reprogrammed in a laboratory to express a chimeric antigen receptor (CAR) that targets tumor antigens, then expanded and infused back. Each dose is a personalized, living drug.',
      molecularTarget: 'CD19 (B-cell lymphomas/leukemias), BCMA (multiple myeloma)',
      sideEffects: ['Cytokine Release Syndrome (CRS) - 60-90%', 'Neurotoxicity (ICANS) - 20-60%', 'B-cell aplasia', 'Hypogammaglobulinemia', 'Prolonged cytopenias'],
      pharmacokinetics: {
        absorption: 'IV infusion of living cells',
        distribution: 'Traffic to tumor sites, lymph nodes, bone marrow',
        metabolism: 'In-vivo expansion (peak 7-14 days post-infusion)',
        elimination: 'Contraction phase over weeks-months; memory cells persist years',
        halfLife: 'Biphasic: expansion (3-7 days doubling), contraction (months)',
        bioavailability: 'N/A (cellular therapy)'
      },
      clinicalTrials: [
        { phase: 'ELIANA (Pediatric ALL)', enrollment: 75, primaryEndpoint: 'Overall Remission Rate', result: '81% ORR (60% CR), 12-month EFS 50%' },
        { phase: 'JULIET (DLBCL)', enrollment: 93, primaryEndpoint: 'Best Overall Response', result: '52% ORR (40% CR), 12-month OS 49%' },
        { phase: 'ZUMA-1 (DLBCL)', enrollment: 101, primaryEndpoint: 'Objective Response Rate', result: '83% ORR (54% CR), median OS 25.8 months' },
        { phase: 'KarMMa (Myeloma)', enrollment: 128, primaryEndpoint: 'ORR at ≥150 dose', result: '73% ORR (33% CR), median PFS 8.8 months' }
      ]
    },
    {
      id: 'adc',
      name: 'Antibody-Drug Conjugates (T-DXd/Enhertu)',
      type: 'therapy',
      targetDisease: 'HER2+ Breast Cancer, HER2-low Breast Cancer, Gastric Cancer, NSCLC',
      mechanism: 'Monoclonal antibody linked to cytotoxic payload via cleavable linker; delivers chemotherapy directly to tumor cells',
      stage: 'approved',
      efficacy: '52-79% ORR in HER2+ breast cancer; bystander killing of HER2-low cells',
      timeline: 'Available now (FDA approved 2019+)',
      description: 'Trastuzumab deruxtecan (T-DXd/Enhertu) is a next-gen ADC that delivers a topoisomerase I inhibitor payload directly to HER2-expressing cancer cells. Its cleavable linker allows "bystander killing" of nearby HER2-low cells, dramatically expanding the treatable population.',
      molecularTarget: 'HER2 (ErbB2) receptor on tumor cells',
      sideEffects: ['Nausea (73%)', 'Neutropenia (38%)', 'Interstitial Lung Disease (10-15%)', 'Fatigue (49%)', 'Alopecia (38%)', 'Anemia (31%)'],
      pharmacokinetics: {
        absorption: 'IV infusion q3w',
        distribution: 'Target-mediated uptake by HER2+ cells; Vd = 5.4 L',
        metabolism: 'Antibody: proteolytic; Payload (DXd): CYP3A4',
        elimination: 'Antibody: TMDD; Payload: hepatic/renal',
        halfLife: 'ADC intact: 5.7 days; Released DXd: 5.8 hours',
        bioavailability: '100% (IV)'
      },
      clinicalTrials: [
        { phase: 'DESTINY-Breast03', enrollment: 524, primaryEndpoint: 'PFS by BICR', result: 'Median PFS 28.8 vs 6.8 months (HR 0.33)' },
        { phase: 'DESTINY-Breast04', enrollment: 557, primaryEndpoint: 'PFS in HER2-low', result: '9.9 vs 5.1 months PFS in HER2-low (HR 0.50)' },
        { phase: 'DESTINY-Lung01', enrollment: 91, primaryEndpoint: 'ORR', result: '55% ORR in HER2-mutant NSCLC' },
        { phase: 'DESTINY-Gastric01', enrollment: 187, primaryEndpoint: 'OS', result: '12.5 vs 8.4 months OS (HR 0.59)' }
      ]
    },
    {
      id: 'mrna-vaccine',
      name: 'mRNA Cancer Vaccines (mRNA-4157/V940)',
      type: 'vaccine',
      targetDisease: 'Melanoma, NSCLC, Pancreatic Cancer (personalized neoantigen)',
      mechanism: 'Personalized mRNA encoding up to 34 tumor-specific neoantigens; stimulates T-cell response against patient\'s unique tumor mutations',
      stage: 'clinical-trial',
      efficacy: '44% reduction in recurrence/death (melanoma Phase 2b, combined with pembrolizumab)',
      timeline: 'Phase 3 ongoing (2024-2026)',
      description: 'Each vaccine is a one-of-a-kind therapeutic created by whole-exome sequencing of the patient\'s tumor, identifying mutations (neoantigens) not found in normal tissue, then synthesizing mRNA encoding up to 34 neoantigens. Combined with a checkpoint inhibitor, it trains the immune system to hunt cancer cells carrying those specific mutations.',
      molecularTarget: 'Patient-specific tumor neoantigens (up to 34 per vaccine)',
      sideEffects: ['Injection site reactions (85%)', 'Fatigue (47%)', 'Myalgia (22%)', 'Fever (15%)', 'Nausea (12%)'],
      pharmacokinetics: {
        absorption: 'IM injection; LNP-encapsulated mRNA',
        distribution: 'LNPs traffic to draining lymph nodes; mRNA taken up by APCs',
        metabolism: 'mRNA degraded by cellular RNases (hours); protein expressed 24-48h',
        elimination: 'mRNA: enzymatic degradation; LNP lipids: hepatic metabolism',
        halfLife: 'mRNA expression: 24-48 hours; Immune response: weeks-months',
        bioavailability: 'N/A (immunogenic, not systemic drug)'
      },
      clinicalTrials: [
        { phase: 'KEYNOTE-942 (Phase 2b)', enrollment: 157, primaryEndpoint: 'Recurrence-Free Survival', result: '44% reduction in recurrence/death vs pembrolizumab alone (HR 0.561)' },
        { phase: 'V940-001 (Phase 3)', enrollment: 1089, primaryEndpoint: 'RFS in Stage III/IV melanoma', result: 'Ongoing — primary readout expected 2025-2026' },
        { phase: 'Autogene cevumeran (Panc)', enrollment: 16, primaryEndpoint: 'T-cell response', result: '50% showed neoantigen-specific T-cell response; 0 relapses in responders at 18 months' }
      ]
    },
    {
      id: 'crispr-sickle',
      name: 'CRISPR Gene Editing (Casgevy/Exagamglogene)',
      type: 'gene-therapy',
      targetDisease: 'Sickle Cell Disease, Beta-Thalassemia',
      mechanism: 'Ex vivo CRISPR-Cas9 editing of patient HSCs to reactivate fetal hemoglobin (HbF) by disrupting BCL11A erythroid enhancer',
      stage: 'approved',
      efficacy: '97% of sickle cell patients free from vaso-occlusive crises at 12 months; transfusion independence in 93% of thalassemia patients',
      timeline: 'FDA/EMA approved Dec 2023',
      description: 'Casgevy (exagamglogene autotemcel) is the first CRISPR-based therapy approved for clinical use. Patient hematopoietic stem cells are harvested, edited with CRISPR-Cas9 to disrupt the BCL11A gene\'s erythroid enhancer (increasing fetal hemoglobin production), then reinfused after myeloablative conditioning. Fetal hemoglobin replaces defective adult hemoglobin, functionally curing the disease.',
      molecularTarget: 'BCL11A erythroid-specific enhancer (chr2p16.1)',
      sideEffects: ['Myeloablative conditioning toxicity (universal)', 'Neutropenia (100%)', 'Thrombocytopenia (100%)', 'Mucositis (55%)', 'Febrile neutropenia (50%)', 'Hepatic veno-occlusive disease (5%)'],
      pharmacokinetics: {
        absorption: 'IV infusion of edited HSCs',
        distribution: 'HSCs home to bone marrow niches',
        metabolism: 'Edited cells engraft and self-renew; editing is permanent',
        elimination: 'N/A — permanent genomic modification',
        halfLife: 'Permanent (edited stem cells persist for life)',
        bioavailability: 'N/A (cellular therapy)'
      },
      clinicalTrials: [
        { phase: 'CLIMB-111 (SCD)', enrollment: 44, primaryEndpoint: 'Freedom from VOC (12 months)', result: '29/30 patients VOC-free for ≥12 consecutive months' },
        { phase: 'CLIMB-121 (Thalassemia)', enrollment: 52, primaryEndpoint: 'Transfusion independence', result: '39/42 achieved transfusion independence' },
        { phase: 'CLIMB-131 (Pediatric SCD)', enrollment: 12, primaryEndpoint: 'Safety and HbF induction', result: 'Mean HbF increase to 40%+; all patients VOC-free' }
      ]
    },
    {
      id: 'lecanemab',
      name: 'Anti-Amyloid Antibodies (Lecanemab/Leqembi)',
      type: 'therapy',
      targetDisease: 'Early Alzheimer\'s Disease',
      mechanism: 'Humanized IgG1 monoclonal antibody selectively binding soluble amyloid-beta protofibrils; promotes microglial phagocytosis and clearance',
      stage: 'approved',
      efficacy: '27% slowing of cognitive decline at 18 months; 59% amyloid plaque reduction',
      timeline: 'FDA approved Jan 2023',
      description: 'Lecanemab represents the first disease-modifying therapy for Alzheimer\'s proven to slow cognitive decline. It targets soluble amyloid-beta protofibrils (the most toxic amyloid species) and removes amyloid plaques from the brain. While the 27% slowing of decline is modest, it validates the amyloid hypothesis and opens the door for combination therapies.',
      molecularTarget: 'Amyloid-beta protofibrils and plaques',
      sideEffects: ['ARIA-E (edema/effusion) - 12.6%', 'ARIA-H (microhemorrhage) - 17.3%', 'Infusion reactions - 26.4%', 'Headache - 14%', 'Fall - 6%'],
      pharmacokinetics: {
        absorption: 'IV infusion q2w (10 mg/kg)',
        distribution: 'Crosses BBB (CSF/serum ratio ~0.1%); Vd = 3.22 L',
        metabolism: 'Fc-mediated recycling via FcRn; proteolytic catabolism',
        elimination: 'Target-mediated (amyloid clearance) + nonspecific IgG catabolism',
        halfLife: '5-7 days',
        bioavailability: '100% (IV)'
      },
      clinicalTrials: [
        { phase: 'Clarity AD (Phase 3)', enrollment: 1795, primaryEndpoint: 'CDR-SB change at 18 months', result: '-0.45 points vs placebo (27% less decline, p=0.00005)' },
        { phase: 'AHEAD 3-45 (Prevention)', enrollment: 1169, primaryEndpoint: 'Amyloid reduction (preclinical)', result: 'Ongoing — testing in asymptomatic amyloid-positive individuals' }
      ]
    },
    {
      id: 'tki-osimertinib',
      name: 'EGFR TKI (Osimertinib/Tagrisso)',
      type: 'pill',
      targetDisease: 'EGFR-mutant Non-Small Cell Lung Cancer',
      mechanism: 'Third-generation irreversible EGFR tyrosine kinase inhibitor; covalently binds C797 in ATP binding pocket; active against T790M resistance mutation; CNS penetrant',
      stage: 'approved',
      efficacy: '80% ORR in first-line; median PFS 18.9 months; 38.6 months OS; 51% reduction in CNS progression',
      timeline: 'FDA approved 2015 (2nd line), 2018 (1st line), 2020 (adjuvant)',
      description: 'Osimertinib is the definitive example of a "cancer pill" — an oral tablet taken once daily that specifically targets the molecular defect driving the cancer. It irreversibly inhibits EGFR with activating mutations (exon 19 del, L858R) and the T790M resistance mutation, while sparing wild-type EGFR (reducing skin/GI toxicity). It achieves meaningful CNS penetration, preventing brain metastases.',
      molecularTarget: 'EGFR (mutant: exon 19 del, L858R, T790M)',
      sideEffects: ['Diarrhea (41%)', 'Rash (34%)', 'Paronychia (25%)', 'Stomatitis (15%)', 'QTc prolongation (4%)', 'ILD (3.5%)'],
      pharmacokinetics: {
        absorption: 'Oral; Tmax 6 hours; food does not affect exposure',
        distribution: 'Vd/F = 986 L; protein binding 95% (albumin, AAG)',
        metabolism: 'CYP3A4/5 (primary); active metabolites AZ5104 and AZ7550',
        elimination: 'Fecal (68%), Renal (14%)',
        halfLife: '48 hours',
        bioavailability: '70%'
      },
      clinicalTrials: [
        { phase: 'FLAURA (1st line)', enrollment: 556, primaryEndpoint: 'PFS', result: '18.9 vs 10.2 months PFS (HR 0.46); 38.6 vs 31.8 months OS (HR 0.80)' },
        { phase: 'AURA3 (T790M)', enrollment: 419, primaryEndpoint: 'PFS', result: '10.1 vs 4.4 months (HR 0.30)' },
        { phase: 'ADAURA (Adjuvant)', enrollment: 682, primaryEndpoint: 'DFS in Stage IB-IIIA', result: 'HR 0.17 (83% reduction in recurrence)' },
        { phase: 'FLAURA2 (Combo)', enrollment: 557, primaryEndpoint: 'PFS (osi + chemo)', result: '25.5 vs 16.7 months (HR 0.62)' }
      ]
    },
    {
      id: 'hiv-cure',
      name: 'HIV Functional Cure (Broadly Neutralizing Antibodies + Latency Reversal)',
      type: 'therapy',
      targetDisease: 'HIV/AIDS',
      mechanism: 'Combination of broadly neutralizing antibodies (bNAbs) targeting HIV envelope protein + latency reversal agents to flush viral reservoirs + possible CRISPR excision of proviral DNA',
      stage: 'research',
      efficacy: 'Sustained viral suppression off ART for 6+ months in early trials (bNAbs alone)',
      timeline: '2028-2035 (functional cure); bNAbs as maintenance 2026+',
      description: 'The HIV cure strategy combines multiple approaches: broadly neutralizing antibodies (like VRC01, 3BNC117, 10-1074) that target conserved HIV envelope epitopes; latency reversal agents ("shock and kill") to flush HIV from reservoir cells; and potentially CRISPR-Cas9 to excise integrated proviral DNA from the host genome.',
      molecularTarget: 'HIV-1 envelope glycoprotein (gp120/gp41); CD4 reservoir cells',
      sideEffects: ['Infusion reactions (bNAbs)', 'Viral rebound risk during ART interruption', 'Immune reconstitution syndrome', 'Unknown long-term effects of latency reversal'],
      pharmacokinetics: {
        absorption: 'IV/SC infusion (bNAbs)',
        distribution: 'IgG1 distribution; limited tissue reservoir penetration',
        metabolism: 'Fc-mediated recycling; proteolytic catabolism',
        elimination: 'IgG catabolism; target-mediated disposition',
        halfLife: '11-38 days depending on antibody (VRC01: 15 days; 10-1074: 24 days)',
        bioavailability: '~65% (SC), 100% (IV)'
      },
      clinicalTrials: [
        { phase: 'Rockefeller bNAb Study', enrollment: 18, primaryEndpoint: 'Time to viral rebound off ART', result: 'Median 21 weeks suppression (3BNC117 + 10-1074) vs 2.3 weeks control' },
        { phase: 'VRC01 (HVTN 704)', enrollment: 2699, primaryEndpoint: 'HIV acquisition prevention', result: 'Effective only against VRC01-sensitive strains (not broad enough alone)' },
        { phase: 'Excision BioTherapeutics (CRISPR)', enrollment: 9, primaryEndpoint: 'Safety of EBT-101 (CRISPR HIV excision)', result: 'Phase 1/2 — safety data pending' }
      ]
    },
    {
      id: 'cf-modulator',
      name: 'CFTR Modulators (Elexacaftor/Tezacaftor/Ivacaftor - Trikafta)',
      type: 'pill',
      targetDisease: 'Cystic Fibrosis (F508del and other mutations)',
      mechanism: 'Triple combination: two correctors (elexacaftor + tezacaftor) rescue F508del-CFTR protein folding and trafficking; one potentiator (ivacaftor) enhances channel open probability at cell surface',
      stage: 'approved',
      efficacy: '14.3% absolute improvement in ppFEV1; 63% reduction in pulmonary exacerbations; sweat chloride reduction of 41.8 mmol/L',
      timeline: 'FDA approved Oct 2019',
      description: 'Trikafta is one of the greatest achievements in precision medicine. Cystic fibrosis is caused by mutations in the CFTR chloride channel gene. The F508del mutation (present in ~90% of CF patients) causes protein misfolding. Trikafta\'s triple combination corrects the folding defect (correctors), gets the protein to the cell surface, and then enhances its function (potentiator). It transforms CF from a fatal childhood disease to a manageable chronic condition.',
      molecularTarget: 'CFTR chloride channel protein (F508del and 177+ other mutations)',
      sideEffects: ['Headache (17%)', 'Upper respiratory infection (22%)', 'Abdominal pain (8%)', 'Elevated transaminases (10%)', 'Rash (11%)', 'Diarrhea (7%)'],
      pharmacokinetics: {
        absorption: 'Oral with fat-containing food (2-3x increase in exposure)',
        distribution: 'Protein binding >99% (all three components)',
        metabolism: 'Elexacaftor: CYP3A; Tezacaftor: CYP3A/CYP2C9; Ivacaftor: CYP3A',
        elimination: 'Primarily fecal (87% elexacaftor, 72% tezacaftor, 88% ivacaftor)',
        halfLife: 'Elexacaftor: 14h; Tezacaftor: 62h; Ivacaftor: 9h',
        bioavailability: 'Elexacaftor: ~70%; Tezacaftor: ~70%; Ivacaftor: ~70% (with fat)'
      },
      clinicalTrials: [
        { phase: 'VX-445-102 (Phase 3)', enrollment: 403, primaryEndpoint: 'ppFEV1 change at 24 weeks', result: '+14.3 percentage points vs placebo in F508del/MF (p<0.001)' },
        { phase: 'VX-445-104 (F508del homo)', enrollment: 107, primaryEndpoint: 'ppFEV1 change', result: '+10.0 points vs tez/iva alone' },
        { phase: 'Real-world (PROMISE)', enrollment: 487, primaryEndpoint: 'Sustained FEV1 improvement', result: 'Maintained +15.5 ppFEV1 at 30 months; BMI increase of 1.8 kg/m2' }
      ]
    }
  ]);

  // ─── Drug Mechanisms ──────────────────────────────────────────────────

  drugMechanisms = signal<DrugMechanism[]>([
    {
      id: 'checkpoint',
      name: 'PD-1/PD-L1 Checkpoint Blockade',
      category: 'immunotherapy',
      pathway: 'PD-1/PD-L1 Immune Checkpoint',
      targetProtein: 'Programmed Death-1 (PD-1) receptor',
      description: 'Tumor cells express PD-L1 to bind PD-1 on T-cells, sending an inhibitory signal that prevents T-cell activation. Checkpoint inhibitors block this interaction.',
      steps: [
        '1. Tumor cells upregulate PD-L1 expression to evade immune detection',
        '2. PD-L1 binds PD-1 receptor on cytotoxic T-lymphocytes (CTLs)',
        '3. PD-1 signaling recruits SHP-2 phosphatase to TCR complex',
        '4. SHP-2 dephosphorylates ZAP70/CD3-zeta, inhibiting T-cell activation',
        '5. Anti-PD-1 antibody (pembrolizumab) binds PD-1, blocking PD-L1 interaction',
        '6. T-cell activation signals restored: IL-2 production, proliferation, cytotoxicity',
        '7. Activated CTLs infiltrate tumor, recognize MHC-I presented neoantigens',
        '8. Granzyme B / perforin-mediated tumor cell apoptosis'
      ],
      molecularStructure: 'IgG4 kappa monoclonal antibody (149 kDa)'
    },
    {
      id: 'car-t',
      name: 'CAR-T Cell Engineering',
      category: 'gene-therapy',
      pathway: 'Synthetic T-cell Receptor Signaling',
      targetProtein: 'CD19 (B-cell marker)',
      description: 'CAR-T cells are engineered with a chimeric receptor combining an antibody-derived scFv for tumor recognition with intracellular signaling domains for T-cell activation.',
      steps: [
        '1. Patient T-cells collected via leukapheresis',
        '2. T-cells activated with anti-CD3/CD28 beads + IL-2',
        '3. Lentiviral vector transduces CAR construct into T-cells',
        '4. CAR structure: scFv(anti-CD19) — CD8a hinge — CD28/4-1BB costimulatory — CD3-zeta ITAM',
        '5. CAR-T cells expanded ex vivo for 9-14 days to therapeutic dose (10^8-10^9 cells)',
        '6. Patient receives lymphodepleting chemotherapy (fludarabine + cyclophosphamide)',
        '7. CAR-T cells infused; scFv recognizes CD19 on B-cell surface',
        '8. CAR signaling activates T-cell: cytokine release, proliferation, serial killing',
        '9. Peak expansion at day 7-14; cytokine storm (CRS) may occur',
        '10. Memory CAR-T cells persist for months-years, providing surveillance'
      ],
      molecularStructure: 'Chimeric receptor: scFv-Hinge-TM-Costimulatory-CD3zeta (~55 kDa)'
    },
    {
      id: 'adc',
      name: 'Antibody-Drug Conjugate Payload Delivery',
      category: 'targeted',
      pathway: 'Receptor-Mediated Endocytosis + Topoisomerase Inhibition',
      targetProtein: 'HER2 (ErbB2)',
      description: 'ADCs combine antibody specificity with cytotoxic payload potency. The antibody delivers the drug directly to tumor cells, minimizing systemic toxicity.',
      steps: [
        '1. Trastuzumab moiety binds HER2 on tumor cell surface (Kd ~ 0.1 nM)',
        '2. ADC-HER2 complex internalized via clathrin-mediated endocytosis',
        '3. Early endosome (pH 6.0) → late endosome (pH 5.5) → lysosome (pH 4.5)',
        '4. Lysosomal proteases cleave tetrapeptide linker (GGFG)',
        '5. DXd payload (exatecan derivative) released inside cell (~8 molecules per antibody)',
        '6. DXd inhibits topoisomerase I → DNA double-strand breaks → apoptosis',
        '7. Membrane-permeable DXd diffuses out of dying cell',
        '8. "Bystander effect": DXd kills neighboring HER2-low/negative cells',
        '9. Fc-mediated ADCC/CDC provides additional anti-tumor activity'
      ],
      molecularStructure: 'IgG1-GGFG-DXd (Drug:Antibody Ratio ~8; MW ~160 kDa)'
    },
    {
      id: 'crispr',
      name: 'CRISPR-Cas9 Gene Editing',
      category: 'gene-therapy',
      pathway: 'Genome Editing → Fetal Hemoglobin Reactivation',
      targetProtein: 'BCL11A erythroid enhancer',
      description: 'CRISPR-Cas9 creates a targeted double-strand break in the BCL11A erythroid enhancer, disrupting repression of gamma-globin genes and reactivating fetal hemoglobin production.',
      steps: [
        '1. Patient CD34+ hematopoietic stem cells (HSCs) mobilized and collected',
        '2. Guide RNA (gRNA) designed to target BCL11A erythroid enhancer at chr2p16.1',
        '3. Cas9 protein + gRNA delivered to HSCs via electroporation (ribonucleoprotein complex)',
        '4. Cas9-gRNA complex scans genome for PAM sequence (NGG) adjacent to target',
        '5. R-loop formation: gRNA base-pairs with target DNA strand',
        '6. HNH domain cleaves complementary strand; RuvC domain cleaves non-complementary strand',
        '7. Double-strand break (DSB) repaired by NHEJ → insertions/deletions disrupt enhancer',
        '8. Disrupted BCL11A enhancer → reduced BCL11A in erythroid cells',
        '9. Loss of BCL11A de-represses HBG1/HBG2 (gamma-globin) genes',
        '10. Fetal hemoglobin (HbF: alpha2-gamma2) produced instead of HbS (sickle)',
        '11. Patient receives myeloablative conditioning (busulfan)',
        '12. Edited HSCs infused; engraft in bone marrow; produce HbF-containing RBCs for life'
      ],
      molecularStructure: 'SpCas9 (1368 aa, 158 kDa) + sgRNA (100 nt)'
    }
  ]);

  // ─── Monte Carlo Clinical Simulation ──────────────────────────────────

  monteCarloResults = signal<MonteCarloTrialResult[]>([
    { scenario: 'Checkpoint Inhibitor Monotherapy (Melanoma)', trials: 10000, median_survival_months: 32.7, survival_std: 4.2, response_rate: 0.42, complete_remission: 0.15, progression_free_survival: 11.2, description: 'Pembrolizumab monotherapy in advanced melanoma. Durable responses in 15-20% of patients.' },
    { scenario: 'CAR-T (Relapsed DLBCL)', trials: 10000, median_survival_months: 25.8, survival_std: 6.1, response_rate: 0.83, complete_remission: 0.54, progression_free_survival: 14.7, description: 'Axi-cel in relapsed/refractory DLBCL. High initial response but significant CRS risk.' },
    { scenario: 'T-DXd (HER2+ Breast Cancer)', trials: 10000, median_survival_months: 35.4, survival_std: 5.3, response_rate: 0.79, complete_remission: 0.21, progression_free_survival: 28.8, description: 'Trastuzumab deruxtecan in HER2+ metastatic breast cancer after prior therapy.' },
    { scenario: 'mRNA Vaccine + Pembro (Melanoma Adjuvant)', trials: 10000, median_survival_months: 48.2, survival_std: 7.8, response_rate: 0.89, complete_remission: 0.56, progression_free_survival: 36.5, description: 'Personalized neoantigen vaccine combined with checkpoint blockade in adjuvant melanoma.' },
    { scenario: 'Osimertinib (EGFR+ NSCLC)', trials: 10000, median_survival_months: 38.6, survival_std: 4.8, response_rate: 0.80, complete_remission: 0.03, progression_free_survival: 18.9, description: 'First-line osimertinib in EGFR-mutant NSCLC. Standard of care with CNS protection.' },
    { scenario: 'Trikafta (Cystic Fibrosis)', trials: 10000, median_survival_months: 600, survival_std: 24, response_rate: 0.90, complete_remission: 0.87, progression_free_survival: 360, description: 'Elexacaftor/tezacaftor/ivacaftor in CF with F508del. Dramatic improvement in lung function and life expectancy.' },
    { scenario: 'CRISPR Sickle Cell (Casgevy)', trials: 10000, median_survival_months: 600, survival_std: 36, response_rate: 0.97, complete_remission: 0.93, progression_free_survival: 600, description: 'Exagamglogene autotemcel for sickle cell disease. Near-complete elimination of vaso-occlusive crises.' }
  ]);

  // ─── Technical Derivations ────────────────────────────────────────────

  technicalDerivations = signal<TechnicalDerivation[]>([
    {
      id: 'pharmacokinetics',
      title: 'Pharmacokinetics & Drug Metabolism',
      category: 'pharmacokinetics',
      equations: [
        {
          name: 'One-Compartment PK Model',
          latex: 'C(t) = (F × D / Vd) × e^(-k_e × t)',
          description: 'Plasma concentration over time after single oral dose, assuming first-order elimination',
          variables: [
            { symbol: 'C(t)', meaning: 'Plasma concentration at time t', unit: 'ng/mL' },
            { symbol: 'F', meaning: 'Oral bioavailability', unit: 'fraction (0-1)' },
            { symbol: 'D', meaning: 'Dose administered', unit: 'mg' },
            { symbol: 'Vd', meaning: 'Volume of distribution', unit: 'L' },
            { symbol: 'k_e', meaning: 'Elimination rate constant', unit: '1/h' }
          ],
          derivation: [
            'For osimertinib (Tagrisso): F = 0.70, D = 80 mg, Vd = 986 L',
            'k_e = ln(2) / t½ = 0.693 / 48 h = 0.0144 h⁻¹',
            'C(0) = (0.70 × 80,000 µg) / 986 L = 56.8 ng/mL',
            'At steady state (q.d. dosing): Css = F×D / (Vd × k_e × tau) = 79.2 ng/mL',
            'Accumulation ratio = 1 / (1 - e^(-k_e × 24)) = 3.45'
          ],
          numericalExample: {
            inputs: { 'F': 0.70, 'D_mg': 80, 'Vd_L': 986, 't_half_h': 48 },
            calculation: 'C_peak = (0.70 × 80,000) / 986 = 56.8 ng/mL; k_e = 0.0144 h⁻¹',
            result: 'Css,avg = 79.2 ng/mL (within therapeutic window 50-200 ng/mL)'
          }
        },
        {
          name: 'Michaelis-Menten Enzyme Kinetics',
          latex: 'v = Vmax × [S] / (Km + [S])',
          description: 'Rate of drug metabolism by CYP enzymes as function of substrate concentration',
          variables: [
            { symbol: 'v', meaning: 'Reaction velocity', unit: 'nmol/min/mg protein' },
            { symbol: 'Vmax', meaning: 'Maximum reaction velocity', unit: 'nmol/min/mg protein' },
            { symbol: '[S]', meaning: 'Substrate concentration', unit: 'µM' },
            { symbol: 'Km', meaning: 'Michaelis constant (affinity)', unit: 'µM' }
          ],
          derivation: [
            'CYP3A4 metabolizes osimertinib with Km ≈ 15 µM',
            'At therapeutic concentrations (~0.2 µM), [S] << Km',
            'v ≈ (Vmax/Km) × [S] → first-order kinetics',
            'Clearance (CL) = Vmax/Km = intrinsic clearance',
            'Hepatic CL = Q_H × (CL_int × f_u) / (Q_H + CL_int × f_u)'
          ]
        },
        {
          name: 'Therapeutic Index',
          latex: 'TI = TD₅₀ / ED₅₀',
          description: 'Ratio of dose causing toxicity to dose producing therapeutic effect — wider TI means safer drug',
          variables: [
            { symbol: 'TI', meaning: 'Therapeutic index', unit: 'dimensionless' },
            { symbol: 'TD₅₀', meaning: 'Dose causing toxicity in 50% of patients', unit: 'mg' },
            { symbol: 'ED₅₀', meaning: 'Dose producing effect in 50% of patients', unit: 'mg' }
          ],
          derivation: [
            'Traditional chemotherapy (cisplatin): TI ≈ 2-3 (narrow)',
            'Targeted therapy (osimertinib): TI ≈ 10-15 (wider)',
            'Checkpoint inhibitor (pembrolizumab): TI ≈ 8-12',
            'CFTR modulator (ivacaftor): TI ≈ 20+ (very wide)',
            'Wider TI → fewer dose-limiting toxicities → better quality of life'
          ]
        }
      ]
    },
    {
      id: 'immunology',
      title: 'Immunology & T-Cell Kinetics',
      category: 'immunology',
      equations: [
        {
          name: 'T-Cell Expansion Kinetics',
          latex: 'N(t) = N₀ × 2^(t / T_doubling)',
          description: 'Exponential expansion of CAR-T cells after infusion',
          variables: [
            { symbol: 'N(t)', meaning: 'CAR-T cell count at time t', unit: 'cells/µL' },
            { symbol: 'N₀', meaning: 'Initial infused cell dose', unit: 'cells/µL' },
            { symbol: 't', meaning: 'Time post-infusion', unit: 'days' },
            { symbol: 'T_doubling', meaning: 'Doubling time', unit: 'days' }
          ],
          derivation: [
            'Typical infusion: 2 × 10⁶ CAR-T cells/kg (for 70 kg patient = 1.4 × 10⁸ cells)',
            'Peak expansion ~1000-fold at day 7-14',
            'Doubling time during expansion: ~1.5-2 days',
            'Peak: N(10) = 1.4×10⁸ × 2^(10/1.5) = 1.4×10⁸ × 101 ≈ 1.4×10¹⁰ cells',
            'Contraction phase follows with memory subset persistence'
          ],
          numericalExample: {
            inputs: { 'N₀': '1.4×10⁸', 'T_doubling': 1.5, 't_days': 10 },
            calculation: 'N(10) = 1.4×10⁸ × 2^(10/1.5) = 1.4×10⁸ × 101.6',
            result: '~1.42 × 10¹⁰ cells at peak (consistent with clinical CRS timing)'
          }
        },
        {
          name: 'Immune Checkpoint Occupancy',
          latex: 'Occupancy = [Ab] / ([Ab] + Kd)',
          description: 'Fraction of PD-1 receptors occupied by anti-PD-1 antibody (saturating binding)',
          variables: [
            { symbol: 'Occupancy', meaning: 'Fraction of receptors bound', unit: '%' },
            { symbol: '[Ab]', meaning: 'Free antibody concentration', unit: 'nM' },
            { symbol: 'Kd', meaning: 'Dissociation constant', unit: 'nM' }
          ],
          derivation: [
            'Pembrolizumab Kd for PD-1 = 29 pM (0.029 nM)',
            'At trough concentration (~20 µg/mL = 134 nM):',
            'Occupancy = 134 / (134 + 0.029) = 99.98%',
            'Even at 1 µg/mL: Occupancy = 6.7 / (6.7 + 0.029) = 99.6%',
            'Explains why flat dosing (200 mg) works — near-complete receptor saturation'
          ]
        },
        {
          name: 'Cytokine Release Kinetics (CRS Model)',
          latex: 'IL6(t) = IL6_base × (1 + α × N_CAR(t) × k_kill)',
          description: 'IL-6 level as function of CAR-T expansion and tumor killing rate',
          variables: [
            { symbol: 'IL6(t)', meaning: 'Serum IL-6 at time t', unit: 'pg/mL' },
            { symbol: 'IL6_base', meaning: 'Baseline IL-6', unit: 'pg/mL' },
            { symbol: 'α', meaning: 'IL-6 production coefficient', unit: 'pg/cell/kill' },
            { symbol: 'N_CAR(t)', meaning: 'CAR-T cell count', unit: 'cells' },
            { symbol: 'k_kill', meaning: 'Tumor cell killing rate', unit: '1/day' }
          ]
        }
      ]
    },
    {
      id: 'genomics',
      title: 'Genomics & Gene Editing',
      category: 'genomics',
      equations: [
        {
          name: 'CRISPR On-Target Editing Efficiency',
          latex: 'E_edit = P_bind × P_cleave × P_NHEJ',
          description: 'Probability of successful gene disruption at target locus',
          variables: [
            { symbol: 'E_edit', meaning: 'Overall editing efficiency', unit: 'fraction' },
            { symbol: 'P_bind', meaning: 'Probability Cas9-gRNA finds target', unit: 'fraction' },
            { symbol: 'P_cleave', meaning: 'Probability of DSB after binding', unit: 'fraction' },
            { symbol: 'P_NHEJ', meaning: 'Probability NHEJ causes functional disruption', unit: 'fraction' }
          ],
          derivation: [
            'For BCL11A enhancer editing in Casgevy:',
            'P_bind ≈ 0.95 (optimized gRNA, high Cas9 concentration)',
            'P_cleave ≈ 0.90 (efficient PAM site, no chromatin occlusion)',
            'P_NHEJ ≈ 0.98 (NHEJ dominant in HSCs; most indels disrupt enhancer)',
            'E_edit = 0.95 × 0.90 × 0.98 = 0.838 (83.8%)',
            'Clinical data: >80% allelic editing in infused HSCs'
          ],
          numericalExample: {
            inputs: { 'P_bind': 0.95, 'P_cleave': 0.90, 'P_NHEJ': 0.98 },
            calculation: 'E_edit = 0.95 × 0.90 × 0.98',
            result: '83.8% editing efficiency (matches clinical observation of >80%)'
          }
        },
        {
          name: 'Fetal Hemoglobin Induction',
          latex: 'HbF% = 100 × (1 - f_BCL11A) × γ_max',
          description: 'Predicted fetal hemoglobin percentage after BCL11A disruption',
          variables: [
            { symbol: 'HbF%', meaning: 'Fetal hemoglobin as % of total Hb', unit: '%' },
            { symbol: 'f_BCL11A', meaning: 'Residual BCL11A function', unit: 'fraction' },
            { symbol: 'γ_max', meaning: 'Maximum gamma-globin as fraction of total', unit: 'fraction' }
          ],
          derivation: [
            'With 84% editing efficiency: f_BCL11A ≈ 0.16 residual',
            'γ_max ≈ 0.50 (gamma-globin can replace ~50% of beta-globin)',
            'HbF% = 100 × (1 - 0.16) × 0.50 = 42%',
            'Clinical observation: mean HbF of 40-46% in Casgevy patients',
            'HbF >20% prevents sickling; >30% is effectively curative'
          ]
        }
      ]
    },
    {
      id: 'drug-design',
      title: 'Drug Design & Molecular Targeting',
      category: 'drug-design',
      equations: [
        {
          name: 'Binding Affinity (IC50)',
          latex: 'IC₅₀ = Kd × (1 + [S] / Km)',
          description: 'Half-maximal inhibitory concentration for competitive kinase inhibitors',
          variables: [
            { symbol: 'IC₅₀', meaning: 'Concentration for 50% inhibition', unit: 'nM' },
            { symbol: 'Kd', meaning: 'Inhibitor dissociation constant', unit: 'nM' },
            { symbol: '[S]', meaning: 'ATP concentration (substrate)', unit: 'µM' },
            { symbol: 'Km', meaning: 'ATP Michaelis constant for kinase', unit: 'µM' }
          ],
          derivation: [
            'Osimertinib vs EGFR L858R/T790M: IC₅₀ = 0.5 nM',
            'vs wild-type EGFR: IC₅₀ = 184 nM',
            'Selectivity ratio: 184 / 0.5 = 368x mutant-selective',
            'This selectivity explains reduced skin/GI toxicity vs 1st-gen TKIs',
            'Covalent binding to C797 → irreversible inhibition → sustained effect'
          ],
          numericalExample: {
            inputs: { 'IC50_mutant': '0.5 nM', 'IC50_wildtype': '184 nM' },
            calculation: 'Selectivity = IC50_WT / IC50_mut = 184 / 0.5',
            result: '368-fold selectivity for mutant EGFR over wild-type'
          }
        },
        {
          name: 'Drug-Antibody Ratio (DAR) Impact',
          latex: 'Payload_delivered = DAR × N_internalized × f_release',
          description: 'Number of cytotoxic molecules delivered to each tumor cell by an ADC',
          variables: [
            { symbol: 'Payload_delivered', meaning: 'DXd molecules per tumor cell', unit: 'molecules' },
            { symbol: 'DAR', meaning: 'Drug-to-antibody ratio', unit: 'molecules/Ab' },
            { symbol: 'N_internalized', meaning: 'ADC molecules internalized per cell', unit: 'molecules' },
            { symbol: 'f_release', meaning: 'Fraction of payload released in lysosome', unit: 'fraction' }
          ],
          derivation: [
            'T-DXd DAR = ~8 (high DAR enabled by hydrophilic linker)',
            'HER2 receptor density: ~10⁵ per HER2+ cell',
            'Internalization rate: ~10⁴ ADCs per cell per hour',
            'Payload per cell/hour = 8 × 10⁴ × 0.95 = 76,000 DXd molecules',
            'Bystander killing: DXd membrane-permeable → diffuses to neighbors'
          ]
        }
      ]
    },
    {
      id: 'clinical-stats',
      title: 'Clinical Statistics & Trial Design',
      category: 'clinical-stats',
      equations: [
        {
          name: 'Kaplan-Meier Survival Estimator',
          latex: 'S(t) = ∏(1 - d_i / n_i) for all t_i ≤ t',
          description: 'Non-parametric estimator of survival function from censored data',
          variables: [
            { symbol: 'S(t)', meaning: 'Probability of survival beyond time t', unit: 'fraction' },
            { symbol: 'd_i', meaning: 'Number of events at time t_i', unit: 'count' },
            { symbol: 'n_i', meaning: 'Number at risk at time t_i', unit: 'count' }
          ],
          derivation: [
            'KEYNOTE-024 (pembrolizumab vs chemo in NSCLC):',
            'At 6 months: S_pembro(6) = 0.80, S_chemo(6) = 0.72',
            'At 12 months: S_pembro(12) = 0.70, S_chemo(12) = 0.54',
            'At 24 months: S_pembro(24) = 0.52, S_chemo(24) = 0.35',
            'Median OS: pembro 26.3 months vs chemo 13.4 months'
          ]
        },
        {
          name: 'Hazard Ratio',
          latex: 'HR = h_treatment(t) / h_control(t)',
          description: 'Ratio of instantaneous event rates — HR < 1 means treatment reduces risk',
          variables: [
            { symbol: 'HR', meaning: 'Hazard ratio', unit: 'dimensionless' },
            { symbol: 'h_treatment', meaning: 'Hazard rate in treatment arm', unit: 'events/time' },
            { symbol: 'h_control', meaning: 'Hazard rate in control arm', unit: 'events/time' }
          ],
          derivation: [
            'FLAURA trial (osimertinib vs 1st-gen TKI):',
            'PFS HR = 0.46 → 54% reduction in progression/death risk',
            'OS HR = 0.80 → 20% reduction in death risk',
            'ADAURA (adjuvant): DFS HR = 0.17 → 83% reduction in recurrence',
            'DESTINY-Breast03 (T-DXd): PFS HR = 0.33 → 67% risk reduction'
          ]
        },
        {
          name: 'Number Needed to Treat (NNT)',
          latex: 'NNT = 1 / (CER - EER) = 1 / ARR',
          description: 'Number of patients who must be treated for one additional patient to benefit',
          variables: [
            { symbol: 'NNT', meaning: 'Number needed to treat', unit: 'patients' },
            { symbol: 'CER', meaning: 'Control event rate', unit: 'fraction' },
            { symbol: 'EER', meaning: 'Experimental event rate', unit: 'fraction' },
            { symbol: 'ARR', meaning: 'Absolute risk reduction', unit: 'fraction' }
          ],
          derivation: [
            'KEYNOTE-942 (mRNA vaccine + pembro vs pembro alone):',
            'Recurrence: 22% control vs 13% treatment at 3 years',
            'ARR = 0.22 - 0.13 = 0.09',
            'NNT = 1 / 0.09 = 11.1',
            'For every 11 patients treated with mRNA vaccine, 1 additional patient is cured'
          ]
        }
      ]
    }
  ]);

  // ─── Drug Discovery Pipeline ──────────────────────────────────────────

  drugDiscoveryPipeline = signal<SignalProcessingBlock[]>([
    {
      name: 'Target Discovery & Validation',
      function: 'Identify and validate molecular targets driving disease pathology',
      inputs: ['Genomic sequencing data (WES/WGS)', 'Proteomics and transcriptomics', 'CRISPR knockout screens', 'Patient tumor samples'],
      outputs: ['Validated drug target', 'Target essentiality score', 'Druggability assessment'],
      algorithm: 'Multi-omics integration + CRISPR viability screens',
      pseudocode: [
        '# Target Discovery Pipeline',
        'tumor_samples = collect_patient_cohort(n=500)',
        'FOR each sample:',
        '  wes_data = whole_exome_sequencing(sample)',
        '  mutations = call_variants(wes_data, reference=hg38)',
        '  drivers = filter_driver_mutations(mutations, cosmic_db)',
        '',
        '# CRISPR Screen for Essentiality',
        'library = genome_wide_sgRNA_library()',
        'FOR each target_gene in candidate_genes:',
        '  ko_cells = crispr_knockout(cell_line, target_gene)',
        '  viability = measure_growth(ko_cells, days=14)',
        '  IF viability < 0.3:',
        '    essentiality_score = HIGH',
        '    EMIT validated_target(target_gene, score)',
      ]
    },
    {
      name: 'Lead Compound Discovery',
      function: 'Identify small molecules or biologics that interact with validated target',
      inputs: ['Validated target protein structure', 'Chemical compound libraries (~10⁶)', 'AI structure prediction (AlphaFold)', 'Fragment screening data'],
      outputs: ['Hit compounds (IC₅₀ < 10 µM)', 'Binding mode characterization', 'Selectivity profile'],
      algorithm: 'Virtual screening + high-throughput screening + AI-guided design',
      pseudocode: [
        '# AI-Guided Drug Discovery',
        'target_structure = alphafold_predict(target_sequence)',
        'binding_site = identify_pocket(target_structure)',
        '',
        '# Virtual Screening (10⁶ compounds)',
        'FOR each compound in virtual_library:',
        '  docking_score = molecular_docking(compound, binding_site)',
        '  admet_score = predict_admet(compound)  # absorption, metabolism, toxicity',
        '  druglikeness = lipinski_rule_of_five(compound)',
        '  IF docking_score > threshold AND druglikeness:',
        '    hits.append(compound)',
        '',
        '# Experimental Validation',
        'FOR each hit in top_500_hits:',
        '  ic50 = biochemical_assay(hit, target)',
        '  selectivity = counter_screen(hit, off_targets)',
        '  IF ic50 < 10_uM AND selectivity > 100x:',
        '    EMIT lead_compound(hit, ic50, selectivity)',
      ]
    },
    {
      name: 'Preclinical Development',
      function: 'Optimize lead compound and evaluate safety in animal models',
      inputs: ['Lead compounds', 'Structure-activity relationship (SAR) data', 'Animal model (PDX, transgenic)', 'GLP toxicology protocols'],
      outputs: ['Optimized drug candidate (IND-ready)', 'Toxicology package', 'PK/PD model', 'Manufacturing process'],
      algorithm: 'Iterative medicinal chemistry + in vivo efficacy/safety',
      pseudocode: [
        '# Lead Optimization',
        'WHILE potency < target OR selectivity < 100x:',
        '  analogs = generate_analogs(lead, SAR_model)',
        '  FOR each analog:',
        '    potency = measure_ic50(analog)',
        '    selectivity = measure_selectivity(analog)',
        '    pk_params = cassette_pk_study(analog, mouse)',
        '    IF potency < 1_nM AND oral_bioavailability > 30%:',
        '      candidate = analog; BREAK',
        '',
        '# Efficacy Study',
        'pdx_model = implant_patient_tumor(mice, n=30)',
        'treat(pdx_model, candidate, dose=range(1,100,10), days=28)',
        'tumor_growth_inhibition = measure_tgi(pdx_model)',
        '',
        '# GLP Toxicology',
        'tox_study = run_28day_tox(candidate, rat=60, dog=16)',
        'noael = determine_noael(tox_study)',
        'human_equivalent_dose = noael / safety_factor_10',
      ]
    },
    {
      name: 'Clinical Trial Phase I (Safety)',
      function: 'First-in-human dose escalation to establish safety and recommended Phase 2 dose',
      inputs: ['IND application (FDA)', 'Preclinical toxicology data', 'Manufacturing CMC package', 'Starting dose (from NOAEL)'],
      outputs: ['Maximum tolerated dose (MTD)', 'Recommended Phase 2 dose (RP2D)', 'Human PK parameters', 'Preliminary efficacy signals'],
      algorithm: '3+3 dose escalation or Bayesian optimal interval (BOIN)',
      pseudocode: [
        '# 3+3 Dose Escalation',
        'dose_levels = [10, 20, 40, 80, 160, 320]  # mg',
        'FOR each dose in dose_levels:',
        '  enroll patients(n=3)',
        '  administer(dose, cycle=28_days)',
        '  observe DLTs for 28 days',
        '  ',
        '  IF dlt_count == 0:',
        '    escalate to next dose',
        '  ELIF dlt_count == 1:',
        '    enroll 3 more (total 6)',
        '    IF dlt_count <= 1 of 6: escalate',
        '    ELSE: MTD = previous_dose',
        '  ELIF dlt_count >= 2:',
        '    MTD = previous_dose',
        '    STOP escalation',
        '',
        'rp2d = MTD or pharmacologically active dose',
        'EMIT safety_profile(adverse_events, pk_data, rp2d)',
      ]
    },
    {
      name: 'Clinical Trial Phase II/III (Efficacy)',
      function: 'Randomized controlled trial to demonstrate clinical benefit',
      inputs: ['RP2D from Phase I', 'Enrolled patient population', 'Comparator arm (standard of care)', 'Statistical analysis plan'],
      outputs: ['Primary endpoint results (PFS/OS/ORR)', 'Safety database (>300 patients)', 'Biomarker analysis', 'Regulatory submission package'],
      algorithm: 'Randomized controlled trial with Kaplan-Meier + Cox regression analysis',
      pseudocode: [
        '# Phase III Randomized Controlled Trial',
        'patients = screen_and_enroll(target_n=500)',
        'randomize(patients, ratio=1:1, stratify=[pd_l1, stage, ecog])',
        '',
        'FOR each patient:',
        '  IF arm == "treatment":',
        '    administer(drug, dose=rp2d, q3w)',
        '  ELSE:',
        '    administer(standard_of_care)',
        '  ',
        '  assess every 9 weeks (RECIST 1.1 imaging)',
        '  record(tumor_response, adverse_events, survival)',
        '',
        '# Statistical Analysis',
        'pfs_curves = kaplan_meier(treatment, control)',
        'hr = cox_proportional_hazards(pfs_curves)',
        'p_value = log_rank_test(pfs_curves)',
        '',
        'IF hr < 0.70 AND p_value < 0.025:  # one-sided alpha',
        '  SUBMIT to FDA (NDA/BLA)',
        '  EMIT regulatory_approval(drug, indication)',
      ]
    },
    {
      name: 'Regulatory Approval & Post-Market Surveillance',
      function: 'FDA/EMA review and real-world evidence generation',
      inputs: ['Complete clinical data package', 'Chemistry, Manufacturing, Controls (CMC)', 'Risk Evaluation and Mitigation Strategy (REMS)', 'Proposed label'],
      outputs: ['FDA approval decision', 'Drug label/prescribing information', 'REMS requirements', 'Phase IV commitments'],
      algorithm: 'Benefit-risk assessment + advisory committee review',
      pseudocode: [
        '# FDA Review Process',
        'submission = compile_nda(clinical_data, cmc, preclinical)',
        'review_type = determine_review_track(submission)',
        '  # Priority Review: 6 months (serious condition, meaningful advantage)',
        '  # Standard Review: 10 months',
        '  # Breakthrough Therapy: rolling submission + intensive FDA guidance',
        '  # Accelerated Approval: based on surrogate endpoint (ORR)',
        '',
        '# Advisory Committee',
        'IF complex_benefit_risk:',
        '  vote = advisory_committee_meeting(data, experts)',
        '  IF vote.favorable > 50%:',
        '    recommend_approval()',
        '',
        '# Post-Market Phase IV',
        'WHILE drug_on_market:',
        '  collect_real_world_evidence(EHR, registries)',
        '  monitor_safety_signals(FAERS_database)',
        '  IF new_safety_signal detected:',
        '    update_label(warning_or_contraindication)',
      ]
    }
  ]);

  // ─── Research Areas ───────────────────────────────────────────────────

  researchAreas = signal<ResearchArea[]>([
    { name: 'mRNA Technology Platform', focus: 'Rapid vaccine and therapeutic development', breakthroughs: ['COVID-19 vaccines in <1 year', 'Personalized cancer vaccines (mRNA-4157)', 'Rare disease enzyme replacement'], potential: 'Could deliver treatments for 100+ diseases within a decade; manufacturing scales in weeks' },
    { name: 'CRISPR Gene Editing', focus: 'Precise genetic corrections at single-nucleotide resolution', breakthroughs: ['Casgevy for sickle cell disease (first approved CRISPR therapy)', 'Beta-thalassemia cure', 'CAR-T enhancement via CRISPR'], potential: 'Potential to cure 7,000+ genetic diseases; base editing and prime editing expand to point mutations' },
    { name: 'AI-Driven Drug Discovery', focus: 'Accelerated identification of novel therapeutics', breakthroughs: ['AlphaFold2 solved protein folding', 'Insilico Medicine\'s INS018_055 (first AI-discovered drug in Phase II)', 'Halicin antibiotic (MIT)'], potential: '10x faster drug discovery, 50% cost reduction; AI designs novel molecular scaffolds never seen in nature' },
    { name: 'Bispecific Antibodies', focus: 'Engage two targets simultaneously', breakthroughs: ['Blinatumomab (CD3×CD19) for ALL', 'Teclistamab (BCMAxCD3) for myeloma', 'Amivantamab (EGFR×MET) for NSCLC'], potential: 'Bridge immune cells to tumors without ex-vivo engineering; "off-the-shelf" T-cell engagement' },
    { name: 'Radioligand Therapy', focus: 'Targeted radiation delivery to cancer cells', breakthroughs: ['Pluvicto (¹⁷⁷Lu-PSMA) for prostate cancer', 'Lutathera for neuroendocrine tumors'], potential: 'Precision radiation with minimal collateral damage; expanding to many solid tumors' },
    { name: 'Microbiome Therapeutics', focus: 'Gut bacteria-based treatments', breakthroughs: ['Vowst (fecal microbiota product) for C. diff', 'ICB response prediction from gut microbiome'], potential: 'Novel treatments for metabolic, immune, and neurological diseases; microbiome-enhanced immunotherapy' }
  ]);

  // ─── Manufacturing → CVS Pipeline ────────────────────────────────────

  activeManufacturingStep = signal<number>(0);

  manufacturingPipeline = signal<ManufacturingStep[]>([
    {
      id: 'gmp-manufacturing',
      name: 'GMP Drug Manufacturing',
      phase: 'manufacturing',
      duration: '3-6 months (scale-up), 4-8 weeks per batch',
      cost: '$50M-$500M facility buildout; $5K-$500K per batch',
      description: 'Active Pharmaceutical Ingredient (API) synthesis and drug product formulation under current Good Manufacturing Practice (cGMP) regulations. For small molecules like osimertinib: multi-step organic synthesis. For biologics like pembrolizumab: mammalian cell culture (CHO cells) at 2,000-20,000L bioreactor scale. For gene therapies like CAR-T: patient-specific autologous manufacturing.',
      requirements: [
        'FDA-registered cGMP facility (21 CFR Parts 210/211)',
        'Validated manufacturing process (Process Validation: PQ/PPQ)',
        'Raw material qualification & vendor audits',
        'Environmental monitoring (ISO Class 5-8 cleanrooms)',
        'In-process controls (IPC) at every critical step',
        'Batch Manufacturing Records (BMR) per lot'
      ],
      qualityChecks: [
        'Identity testing (HPLC, mass spectrometry)',
        'Purity analysis (≥99.5% for small molecules)',
        'Potency assay (biological activity)',
        'Sterility testing (USP <71>, 14-day incubation)',
        'Endotoxin testing (<5 EU/kg/dose)',
        'Particulate matter (USP <788>)',
        'Container closure integrity'
      ],
      output: 'Drug product lots ready for QC release testing',
      personnel: ['Manufacturing Director', 'Process Engineers', 'Production Operators (cGMP trained)', 'Quality Assurance (QA)', 'Supply Chain Manager'],
      equipment: ['Bioreactors (2,000-20,000L)', 'Chromatography systems (Protein A, IEX, HIC)', 'Lyophilizers', 'Fill/finish lines (aseptic)', 'HPLC/UPLC systems', 'Mass spectrometers']
    },
    {
      id: 'quality-control',
      name: 'Quality Control & Batch Release',
      phase: 'quality',
      duration: '2-6 weeks per batch',
      cost: '$50K-$200K per batch (testing costs)',
      description: 'Comprehensive analytical testing of every manufactured batch against pre-defined specifications in the Certificate of Analysis (CoA). Each test must pass acceptance criteria before lot release. QC labs operate under 21 CFR Part 211 with qualified analysts and validated methods.',
      requirements: [
        'Validated analytical methods (ICH Q2(R1))',
        'Qualified reference standards',
        'Stability program (ICH Q1A: 25°C/60%RH long-term, 40°C/75%RH accelerated)',
        'OOS/OOT investigation procedures',
        'Annual Product Review (APR)',
        'Method transfer validation'
      ],
      qualityChecks: [
        'Release testing per approved specifications',
        'Stability testing (T=0, 3, 6, 9, 12, 18, 24 months)',
        'Certificate of Analysis (CoA) generation',
        'QP (Qualified Person) batch release (EU/EMA)',
        'Deviation and CAPA management',
        'Environmental monitoring review'
      ],
      output: 'Released drug product lots with Certificate of Analysis',
      personnel: ['QC Director', 'QC Analysts (chemistry, microbiology)', 'Quality Assurance Reviewers', 'Qualified Person (EU)', 'Stability Coordinator'],
      equipment: ['HPLC/UPLC systems', 'Cell-based potency assays', 'Karl Fischer titration', 'Dissolution apparatus', 'Particle counters', 'PCR/qPCR (for gene therapies)']
    },
    {
      id: 'fda-lot-release',
      name: 'FDA Review & Lot Release',
      phase: 'regulatory',
      duration: '2-4 weeks (biologics), N/A for most small molecules',
      cost: '$100K-$300K (regulatory affairs)',
      description: 'For biologics (monoclonal antibodies, vaccines, gene therapies), CBER requires lot release before distribution. Manufacturer submits samples and protocols; FDA tests and releases each lot. For small molecules under CDER, lot release is manufacturer-controlled with FDA oversight via inspection.',
      requirements: [
        'BLA/NDA approval in effect',
        'Lot release protocol submission to FDA/CBER',
        'Representative samples from each lot',
        'Complete batch records and CoA',
        'Annual Biologics Report (for BLAs)',
        'Post-approval commitment compliance'
      ],
      qualityChecks: [
        'FDA independent lot testing (potency, purity, identity)',
        'Review of manufacturer CoA and batch records',
        'Confirmatory sterility testing',
        'Lot release certificate issuance',
        'GMP inspection readiness (FDA Form 483 compliance)',
        'REMS compliance verification (if applicable)'
      ],
      output: 'FDA lot release certificate; product cleared for US distribution',
      personnel: ['VP Regulatory Affairs', 'Regulatory CMC Lead', 'FDA Liaison', 'CBER/CDER Reviewers (FDA side)', 'Pharmacovigilance Lead'],
      equipment: ['Document management system (eCTD)', 'Regulatory tracking databases', 'FAERS safety monitoring', 'FDA ESG (Electronic Submissions Gateway)']
    },
    {
      id: 'packaging-labeling',
      name: 'Packaging, Labeling & Serialization',
      phase: 'manufacturing',
      duration: '1-2 weeks per batch',
      cost: '$10-$50 per unit (packaging)',
      description: 'Drug product is packaged into final commercial containers, labeled with FDA-approved labeling (PI, Medication Guide, carton), and serialized per DSCSA (Drug Supply Chain Security Act) with unique product identifiers for track-and-trace.',
      requirements: [
        'FDA-approved labeling and Prescribing Information',
        'DSCSA serialization (unique SNI per unit)',
        'NDC (National Drug Code) assignment',
        'Child-resistant packaging (Poison Prevention Act)',
        'Tamper-evident features',
        'Cold chain packaging validation (2-8°C biologics)'
      ],
      qualityChecks: [
        'Label reconciliation (100% accountability)',
        'Barcode/serialization verification',
        'Visual inspection (AQL sampling)',
        'Weight check (fill volume/count verification)',
        'Packaging integrity testing',
        'Temperature indicator placement (cold chain)'
      ],
      output: 'Serialized, labeled commercial drug product units',
      personnel: ['Packaging Supervisor', 'Line Operators', 'QA Inspector', 'Serialization Specialist', 'Artwork/Labeling Manager'],
      equipment: ['Packaging lines (blister, vial, syringe)', 'Serialization printers (2D data matrix)', 'Vision inspection systems', 'Checkweighers', 'Cartoners', 'Case packers/palletizers']
    },
    {
      id: 'distribution',
      name: 'Wholesale Distribution & Cold Chain',
      phase: 'distribution',
      duration: '1-5 days (domestic), 1-3 weeks (international)',
      cost: '$2-$20 per unit (logistics)',
      description: 'FDA-released product is shipped from manufacturer to wholesale distributors (McKesson, AmerisourceBergen, Cardinal Health — the "Big 3" controlling 90% of US pharma distribution). Products requiring cold chain (biologics at 2-8°C, some gene therapies at -80°C) use validated shipping containers with temperature monitors.',
      requirements: [
        'GDP (Good Distribution Practice) compliance',
        'DSCSA transaction documentation (TI, TH, TS)',
        'Validated cold chain shipping (2-8°C or -20°C or -80°C)',
        'Wholesale Drug Distributor license (state-level)',
        'Temperature-controlled warehousing',
        'Carrier qualification and lane validation'
      ],
      qualityChecks: [
        'Temperature monitoring (continuous data loggers)',
        'Shipment verification (serialization scan)',
        'Cold chain excursion assessment protocol',
        'Receipt verification at distribution center',
        'Inventory reconciliation',
        'Reverse distribution (returns/recalls) capability'
      ],
      output: 'Drug product delivered to CVS/pharmacy distribution centers',
      personnel: ['Supply Chain VP', 'Distribution Manager', 'Cold Chain Specialist', 'Logistics Coordinators', '3PL Partners (McKesson, Cardinal)'],
      equipment: ['Temperature-controlled trucks/containers', 'GPS tracking systems', 'Temperature data loggers', 'Validated shipping containers (Credo, va-Q-tec)', 'Warehouse Management Systems (WMS)']
    },
    {
      id: 'cvs-pharmacy',
      name: 'CVS Pharmacy Stocking & Dispensing',
      phase: 'pharmacy',
      duration: '1-3 days from distribution center to store shelf',
      cost: 'Pharmacy markup: 15-25% (retail); PBM reimbursement negotiated',
      description: 'CVS Pharmacy (9,900+ locations) receives drug product from wholesale distribution. Pharmacists verify prescriptions, check drug interactions, counsel patients, and dispense. For specialty drugs (biologics, oncology), CVS Specialty handles with dedicated pharmacists, patient support programs, and home delivery.',
      requirements: [
        'State pharmacy license and DEA registration',
        'Pharmacist verification of each prescription',
        'Drug Utilization Review (DUR) — interaction/allergy check',
        'Insurance/PBM adjudication (prior authorization if required)',
        'REMS compliance (for restricted drugs)',
        'Patient counseling (USP <17> standards)'
      ],
      qualityChecks: [
        'Prescription verification (RPh review)',
        'Drug-drug interaction screening',
        'Allergy cross-reference',
        'Dosage appropriateness check',
        'Insurance formulary/coverage verification',
        'Patient identity verification at pickup',
        'Cold chain maintenance (pharmacy refrigerator 2-8°C)'
      ],
      output: 'Patient receives FDA-approved medication at CVS pharmacy',
      personnel: ['Pharmacist (RPh/PharmD)', 'Pharmacy Technician (CPhT)', 'Pharmacy Manager', 'CVS Specialty Pharmacist', 'Patient Care Coordinator'],
      equipment: ['Pharmacy dispensing systems', 'Automated dispensing cabinets', 'Prescription verification imaging', 'Refrigerators (2-8°C monitored)', 'Point-of-sale systems', 'E-prescribing gateway (Surescripts)']
    }
  ]);

  selectManufacturingStep(index: number): void {
    this.activeManufacturingStep.set(index);
  }

  getManufacturingPhaseColor(phase: string): string {
    switch (phase) {
      case 'manufacturing': return '#3498db';
      case 'quality': return '#9b59b6';
      case 'regulatory': return '#e74c3c';
      case 'distribution': return '#f39c12';
      case 'pharmacy': return '#27ae60';
      default: return '#95a5a6';
    }
  }

  // ─── Computed Signals ─────────────────────────────────────────────────

  readonly activeCategoryData = computed(() => {
    return this.diseaseCategories().find(c => c.id === this.activeCategory());
  });

  readonly filteredTreatments = computed(() => {
    const category = this.activeCategoryData();
    if (!category) return this.treatments();
    return this.treatments().filter(t => {
      const diseases = category.diseases.map(d => d.toLowerCase());
      return diseases.some(d => t.targetDisease.toLowerCase().includes(d.split(' ')[0])) ||
             (category.id === 'cancer' && ['Leukemia', 'Lymphoma', 'Melanoma', 'Cancer', 'NSCLC', 'Breast', 'Gastric'].some(c => t.targetDisease.includes(c))) ||
             (category.id === 'neurological' && t.targetDisease.toLowerCase().includes('alzheimer')) ||
             (category.id === 'infectious' && t.targetDisease.toLowerCase().includes('hiv')) ||
             (category.id === 'rare' && ['Sickle', 'Cystic', 'Thalassemia'].some(c => t.targetDisease.includes(c)));
    });
  });

  readonly approvedTreatments = computed(() => this.treatments().filter(t => t.stage === 'approved'));
  readonly inTrialTreatments = computed(() => this.treatments().filter(t => t.stage === 'clinical-trial' || t.stage === 'research'));

  // ─── Methods ──────────────────────────────────────────────────────────

  selectCategory(id: string): void {
    this.activeCategory.set(id);
    this.activeTreatment.set(null);
  }

  selectTreatment(id: string): void {
    this.activeTreatment.set(this.activeTreatment() === id ? null : id);
  }

  selectDrugCategory(id: DrugCategoryId): void {
    this.selectedDrugCategory.set(id);
    setTimeout(() => {
      this.drawEfficacyChart();
      this.drawMonteCarloChart();
    }, 50);
  }

  toggleEquations(): void {
    this.showEquations.update(v => !v);
  }

  toggleResearch(): void {
    this.showResearch.update(v => !v);
  }

  selectDerivation(id: string): void {
    this.activeDerivationSection.set(id);
  }

  getActiveDerivation(): TechnicalDerivation | undefined {
    return this.technicalDerivations().find(d => d.id === this.activeDerivationSection());
  }

  selectProcessingStep(index: number): void {
    this.activeProcessingStep.set(index);
  }

  getActiveProcessingBlock(): SignalProcessingBlock | undefined {
    return this.drugDiscoveryPipeline()[this.activeProcessingStep()];
  }

  getStageColor(stage: string): string {
    switch (stage) {
      case 'approved': return '#27ae60';
      case 'clinical-trial': return '#f39c12';
      case 'research': return '#3498db';
      case 'conceptual': return '#9b59b6';
      default: return '#95a5a6';
    }
  }

  getTypeIcon(type: string): string {
    switch (type) {
      case 'pill': return '&#128138;';
      case 'therapy': return '&#129656;';
      case 'gene-therapy': return '&#129516;';
      case 'vaccine': return '&#128137;';
      default: return '&#128138;';
    }
  }

  ngOnInit(): void {}

  ngAfterViewInit(): void {
    setTimeout(() => {
      this.drawEfficacyChart();
      this.drawSurvivalCurves();
      this.drawMonteCarloChart();
      this.drawDiseaseBurdenChart();
      this.drawPipelineFlowChart();
    }, 100);
  }

  // ─── D3 Visualization: Efficacy Comparison Chart ──────────────────────

  drawEfficacyChart(): void {
    const element = this.efficacyChart?.nativeElement;
    if (!element) return;

    const width = 800;
    const height = 350;
    const margin = { top: 40, right: 30, bottom: 120, left: 60 };

    d3.select(element).selectAll('*').remove();

    const svg = d3.select(element)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .style('max-width', '100%');

    const data = this.treatments().filter(t => t.stage === 'approved').map(t => ({
      name: t.name.split('(')[0].trim().split('/')[0].trim(),
      response: parseFloat(t.efficacy.match(/[\d.]+/)?.[0] || '0') / 100,
      disease: t.targetDisease.split(',')[0].trim()
    }));

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const xScale = d3.scaleBand()
      .domain(data.map(d => d.name))
      .range([margin.left, margin.left + innerWidth])
      .padding(0.3);

    const yScale = d3.scaleLinear()
      .domain([0, 1])
      .range([margin.top + innerHeight, margin.top]);

    svg.append('g')
      .attr('transform', `translate(${margin.left}, 0)`)
      .call(d3.axisLeft(yScale).ticks(5).tickFormat(d3.format('.0%')))
      .selectAll('text').attr('fill', '#95a5a6');
    svg.selectAll('.domain, .tick line').attr('stroke', '#334455');

    svg.append('g')
      .attr('transform', `translate(0, ${margin.top + innerHeight})`)
      .call(d3.axisBottom(xScale))
      .selectAll('text')
      .attr('fill', '#95a5a6')
      .attr('font-size', '8px')
      .attr('text-anchor', 'end')
      .attr('transform', 'rotate(-30)');

    const colors = ['#27ae60', '#2ecc71', '#1abc9c', '#16a085', '#3498db', '#2980b9', '#9b59b6'];
    svg.selectAll('.bar')
      .data(data)
      .enter()
      .append('rect')
      .attr('x', d => xScale(d.name)!)
      .attr('y', d => yScale(d.response))
      .attr('width', xScale.bandwidth())
      .attr('height', d => margin.top + innerHeight - yScale(d.response))
      .attr('fill', (_, i) => colors[i % colors.length])
      .attr('rx', 4);

    svg.selectAll('.label')
      .data(data)
      .enter()
      .append('text')
      .attr('x', d => xScale(d.name)! + xScale.bandwidth() / 2)
      .attr('y', d => yScale(d.response) - 8)
      .attr('text-anchor', 'middle')
      .attr('fill', '#27ae60')
      .attr('font-size', '11px')
      .attr('font-weight', 'bold')
      .text(d => `${(d.response * 100).toFixed(0)}%`);

    svg.append('text')
      .attr('x', width / 2).attr('y', 22)
      .attr('text-anchor', 'middle')
      .attr('fill', '#27ae60')
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .text('Treatment Response Rates (Approved Therapies)');

    svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -(margin.top + innerHeight / 2))
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .attr('fill', '#95a5a6')
      .attr('font-size', '12px')
      .text('Response Rate');
  }

  // ─── D3 Visualization: Kaplan-Meier Survival Curves ───────────────────

  drawSurvivalCurves(): void {
    const element = this.survivalCurveChart?.nativeElement;
    if (!element) return;

    const width = 800;
    const height = 400;
    const margin = { top: 40, right: 150, bottom: 50, left: 60 };

    d3.select(element).selectAll('*').remove();

    const svg = d3.select(element)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .style('max-width', '100%');

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleLinear().domain([0, 36]).range([0, innerWidth]);
    const y = d3.scaleLinear().domain([0, 1]).range([innerHeight, 0]);

    // Grid
    [0.2, 0.4, 0.6, 0.8].forEach(v => {
      g.append('line').attr('x1', 0).attr('x2', innerWidth).attr('y1', y(v)).attr('y2', y(v))
        .attr('stroke', '#1a3a5c').attr('stroke-dasharray', '3,3');
    });

    // Survival curves (simulated Kaplan-Meier data)
    const curves: { name: string; color: string; data: [number, number][] }[] = [
      { name: 'Osimertinib (EGFR+ NSCLC)', color: '#27ae60', data: [[0, 1], [3, 0.95], [6, 0.88], [9, 0.82], [12, 0.75], [15, 0.68], [18, 0.58], [21, 0.52], [24, 0.48], [30, 0.40], [36, 0.35]] },
      { name: 'Pembrolizumab (Melanoma)', color: '#3498db', data: [[0, 1], [3, 0.88], [6, 0.78], [9, 0.70], [12, 0.65], [15, 0.60], [18, 0.55], [21, 0.52], [24, 0.50], [30, 0.48], [36, 0.45]] },
      { name: 'T-DXd (HER2+ Breast)', color: '#e67e22', data: [[0, 1], [3, 0.98], [6, 0.92], [9, 0.88], [12, 0.82], [15, 0.78], [18, 0.72], [21, 0.68], [24, 0.62], [30, 0.55], [36, 0.48]] },
      { name: 'Standard Chemo (ref)', color: '#e74c3c', data: [[0, 1], [3, 0.82], [6, 0.65], [9, 0.52], [12, 0.42], [15, 0.35], [18, 0.28], [21, 0.22], [24, 0.18], [30, 0.12], [36, 0.08]] }
    ];

    const lineGen = d3.line<[number, number]>()
      .x(d => x(d[0])).y(d => y(d[1])).curve(d3.curveStepAfter);

    curves.forEach(curve => {
      g.append('path')
        .datum(curve.data)
        .attr('fill', 'none')
        .attr('stroke', curve.color)
        .attr('stroke-width', 2.5)
        .attr('d', lineGen);
    });

    // Axes
    g.append('g').attr('transform', `translate(0,${innerHeight})`).call(d3.axisBottom(x).ticks(6))
      .selectAll('text').attr('fill', '#95a5a6');
    g.append('g').call(d3.axisLeft(y).ticks(5).tickFormat(d3.format('.0%')))
      .selectAll('text').attr('fill', '#95a5a6');

    // Labels
    svg.append('text').attr('x', width / 2).attr('y', height - 5).attr('text-anchor', 'middle')
      .attr('fill', '#95a5a6').attr('font-size', '12px').text('Months');
    svg.append('text').attr('transform', 'rotate(-90)').attr('x', -height / 2).attr('y', 15)
      .attr('text-anchor', 'middle').attr('fill', '#95a5a6').attr('font-size', '12px').text('Survival Probability');
    svg.append('text').attr('x', width / 2).attr('y', 22).attr('text-anchor', 'middle')
      .attr('fill', '#27ae60').attr('font-size', '14px').attr('font-weight', 'bold')
      .text('Kaplan-Meier Survival Curves (Landmark Trials)');

    // Legend
    const legend = svg.append('g').attr('transform', `translate(${width - margin.right + 10}, ${margin.top + 10})`);
    curves.forEach((c, i) => {
      legend.append('line').attr('x1', 0).attr('x2', 20).attr('y1', i * 22).attr('y2', i * 22)
        .attr('stroke', c.color).attr('stroke-width', 2.5);
      legend.append('text').attr('x', 25).attr('y', i * 22 + 4).attr('fill', '#95a5a6')
        .attr('font-size', '9px').text(c.name);
    });
  }

  // ─── D3 Visualization: Monte Carlo Treatment Outcomes ─────────────────

  drawMonteCarloChart(): void {
    const element = this.monteCarloChart?.nativeElement;
    if (!element) return;

    const width = 800;
    const height = 350;
    const margin = { top: 30, right: 30, bottom: 100, left: 60 };

    d3.select(element).selectAll('*').remove();

    const svg = d3.select(element)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .style('max-width', '100%');

    const scenarios = this.monteCarloResults().filter(r => r.median_survival_months < 100);
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const xScale = d3.scaleBand()
      .domain(scenarios.map(s => s.scenario))
      .range([margin.left, margin.left + innerWidth])
      .padding(0.3);

    const yScale = d3.scaleLinear()
      .domain([0, 1])
      .range([margin.top + innerHeight, margin.top]);

    svg.append('g')
      .attr('transform', `translate(${margin.left}, 0)`)
      .call(d3.axisLeft(yScale).ticks(5).tickFormat(d3.format('.0%')))
      .selectAll('text').attr('fill', '#95a5a6');
    svg.selectAll('.domain, .tick line').attr('stroke', '#334455');

    svg.append('g')
      .attr('transform', `translate(0, ${margin.top + innerHeight})`)
      .call(d3.axisBottom(xScale))
      .selectAll('text')
      .attr('fill', '#95a5a6')
      .attr('font-size', '8px')
      .attr('text-anchor', 'end')
      .attr('transform', 'rotate(-25)');

    svg.selectAll('.bar')
      .data(scenarios)
      .enter()
      .append('rect')
      .attr('x', d => xScale(d.scenario)!)
      .attr('y', d => yScale(d.response_rate))
      .attr('width', xScale.bandwidth())
      .attr('height', d => margin.top + innerHeight - yScale(d.response_rate))
      .attr('fill', '#1abc9c')
      .attr('rx', 3);

    svg.selectAll('.label')
      .data(scenarios)
      .enter()
      .append('text')
      .attr('x', d => xScale(d.scenario)! + xScale.bandwidth() / 2)
      .attr('y', d => yScale(d.response_rate) - 8)
      .attr('text-anchor', 'middle')
      .attr('fill', '#1abc9c')
      .attr('font-size', '11px')
      .attr('font-weight', 'bold')
      .text(d => `${(d.response_rate * 100).toFixed(0)}%`);

    svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -(margin.top + innerHeight / 2))
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .attr('fill', '#95a5a6')
      .attr('font-size', '12px')
      .text('Response Rate');

    svg.append('text')
      .attr('x', width / 2).attr('y', 18)
      .attr('text-anchor', 'middle')
      .attr('fill', '#1abc9c')
      .attr('font-size', '13px')
      .attr('font-weight', 'bold')
      .text('Monte Carlo Treatment Response Rates (N=10,000 per scenario)');
  }

  // ─── D3 Visualization: Disease Burden ─────────────────────────────────

  drawDiseaseBurdenChart(): void {
    const element = this.diseaseBurdenChart?.nativeElement;
    if (!element) return;

    const width = 700;
    const height = 300;
    const margin = { top: 40, right: 30, bottom: 60, left: 70 };

    d3.select(element).selectAll('*').remove();

    const svg = d3.select(element)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .style('max-width', '100%');

    const data = [
      { name: 'Cardiovascular', deaths: 17.9, color: '#e74c3c' },
      { name: 'Infectious', deaths: 13.7, color: '#f39c12' },
      { name: 'Cancer', deaths: 10.0, color: '#9b59b6' },
      { name: 'Neurological', deaths: 9.0, color: '#3498db' },
      { name: 'Rare Diseases', deaths: 3.5, color: '#1abc9c' },
      { name: 'Autoimmune', deaths: 0.78, color: '#e67e22' }
    ];

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const x = d3.scaleBand().domain(data.map(d => d.name)).range([0, innerWidth]).padding(0.3);
    const y = d3.scaleLinear().domain([0, 20]).range([innerHeight, 0]);
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    g.selectAll('.bar').data(data).join('rect')
      .attr('x', d => x(d.name) || 0).attr('y', d => y(d.deaths))
      .attr('width', x.bandwidth()).attr('height', d => innerHeight - y(d.deaths))
      .attr('fill', d => d.color).attr('rx', 4);

    g.selectAll('.val').data(data).join('text')
      .attr('x', d => (x(d.name) || 0) + x.bandwidth() / 2)
      .attr('y', d => y(d.deaths) - 8).attr('text-anchor', 'middle')
      .attr('fill', '#fff').attr('font-size', '11px').attr('font-weight', 'bold')
      .text(d => `${d.deaths}M`);

    g.append('g').attr('transform', `translate(0,${innerHeight})`).call(d3.axisBottom(x))
      .selectAll('text').attr('fill', '#95a5a6').attr('font-size', '10px');
    g.append('g').call(d3.axisLeft(y).ticks(4))
      .selectAll('text').attr('fill', '#95a5a6');

    svg.append('text').attr('transform', 'rotate(-90)').attr('x', -height / 2).attr('y', 15)
      .attr('text-anchor', 'middle').attr('fill', '#95a5a6').attr('font-size', '12px').text('Annual Deaths (millions)');
    svg.append('text').attr('x', width / 2).attr('y', 22).attr('text-anchor', 'middle')
      .attr('fill', '#27ae60').attr('font-size', '14px').attr('font-weight', 'bold')
      .text('Global Disease Burden by Category');
  }

  // ─── D3: Pipeline Flow ────────────────────────────────────────────────

  drawPipelineFlowChart(): void {
    const element = this.mechanismFlowChart?.nativeElement;
    if (!element) return;

    const width = 850;
    const height = 120;

    d3.select(element).selectAll('*').remove();

    const svg = d3.select(element)
      .append('svg').attr('width', width).attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`).style('max-width', '100%');

    const steps = this.drugDiscoveryPipeline();
    const boxWidth = 115;
    const boxHeight = 50;
    const gap = (width - steps.length * boxWidth) / (steps.length + 1);
    const colors = ['#3498db', '#9b59b6', '#e67e22', '#e74c3c', '#1abc9c', '#27ae60'];

    svg.append('defs').append('marker')
      .attr('id', 'arrowhead-pipe')
      .attr('viewBox', '0 0 10 10')
      .attr('refX', 8).attr('refY', 5)
      .attr('markerWidth', 6).attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path').attr('d', 'M 0 0 L 10 5 L 0 10 z').attr('fill', '#27ae60');

    steps.forEach((step, i) => {
      const xPos = gap + i * (boxWidth + gap);
      const yPos = (height - boxHeight) / 2;

      svg.append('rect')
        .attr('x', xPos).attr('y', yPos).attr('width', boxWidth).attr('height', boxHeight)
        .attr('fill', 'rgba(26, 42, 74, 0.8)').attr('stroke', colors[i % colors.length])
        .attr('stroke-width', 2).attr('rx', 6);

      svg.append('text')
        .attr('x', xPos + boxWidth / 2).attr('y', yPos + boxHeight / 2 + 4)
        .attr('text-anchor', 'middle').attr('fill', '#fff').attr('font-size', '7.5px').attr('font-weight', 'bold')
        .text(step.name.length > 18 ? step.name.substring(0, 16) + '...' : step.name);

      if (i < steps.length - 1) {
        const arrowX = xPos + boxWidth + 2;
        svg.append('line')
          .attr('x1', arrowX).attr('x2', arrowX + gap - 4)
          .attr('y1', height / 2).attr('y2', height / 2)
          .attr('stroke', '#27ae60').attr('stroke-width', 2)
          .attr('marker-end', 'url(#arrowhead-pipe)');
      }
    });
  }
}
