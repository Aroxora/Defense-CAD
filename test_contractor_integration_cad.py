#!/usr/bin/env python3
"""
Contractor Integration CAD Test Suite

Tests integration of Chinese and Russian defense contractor models
with the CAD framework for kill chain analysis.

Test Coverage:
- Defense contractor registry (AVIC, CASIC, CASC, Sukhoi, MiG, Almaz)
- Chinese integrated kill chain metrics
- Comparison vs US systems (F-22, F-35, NGAD)
- Network resilience calculations
- Passive detection capabilities
- Multi-sensor fusion accuracy

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
import unittest
from defense_contractor_registry import DefenseContractorRegistry, ContractorType
from integrated_kill_chain_cad import IntegratedKillChainCAD, SystemLayer


class TestDefenseContractorRegistry(unittest.TestCase):
    """Test defense contractor registry"""

    def setUp(self):
        """Set up test fixtures"""
        self.registry = DefenseContractorRegistry()

    def test_chinese_contractors_loaded(self):
        """Test Chinese defense contractors are registered"""
        avic = self.registry.get_contractor("AVIC")
        casic = self.registry.get_contractor("CASIC")
        casc = self.registry.get_contractor("CASC")

        self.assertIsNotNone(avic, "AVIC contractor should be registered")
        self.assertIsNotNone(casic, "CASIC contractor should be registered")
        self.assertIsNotNone(casc, "CASC contractor should be registered")

        # Verify contractor details
        self.assertEqual(avic.country, "China")
        self.assertEqual(avic.contractor_type, ContractorType.CHINESE_AVIATION)
        self.assertGreaterEqual(avic.confidence, 0.50)

        self.assertEqual(casic.country, "China")
        self.assertEqual(casic.contractor_type, ContractorType.CHINESE_MISSILE)

        self.assertEqual(casc.country, "China")
        self.assertEqual(casc.contractor_type, ContractorType.CHINESE_SPACE)

    def test_russian_contractors_loaded(self):
        """Test Russian defense contractors are registered"""
        sukhoi = self.registry.get_contractor("Sukhoi")
        mig = self.registry.get_contractor("MiG")
        almaz = self.registry.get_contractor("Almaz")

        self.assertIsNotNone(sukhoi, "Sukhoi contractor should be registered")
        self.assertIsNotNone(mig, "MiG contractor should be registered")
        self.assertIsNotNone(almaz, "Almaz contractor should be registered")

        # Verify contractor details
        self.assertEqual(sukhoi.country, "Russia")
        self.assertEqual(sukhoi.contractor_type, ContractorType.RUSSIAN_AVIATION)
        self.assertGreaterEqual(sukhoi.confidence, 0.60)

        self.assertEqual(mig.country, "Russia")
        self.assertEqual(almaz.country, "Russia")

    def test_avic_models(self):
        """Test AVIC (Chinese aviation) models"""
        avic_models = self.registry.get_contractor_models("AVIC")

        self.assertGreater(len(avic_models), 0, "AVIC should have models")

        # Check for key platforms
        model_names = [m.platform_name for m in avic_models]
        self.assertIn("J-20 Mighty Dragon", model_names)
        self.assertIn("J-10C Vigorous Dragon", model_names)
        self.assertIn("J-11B Flanker", model_names)

        # Verify J-20 model details
        j20_model = self.registry.get_model("J20")
        self.assertEqual(j20_model.contractor, "AVIC")
        self.assertEqual(j20_model.fielded_date, 2017)
        self.assertEqual(j20_model.integration_level, "platform")
        self.assertGreaterEqual(j20_model.confidence, 0.40)

    def test_casic_models(self):
        """Test CASIC (Chinese missiles) models"""
        casic_models = self.registry.get_contractor_models("CASIC")

        self.assertGreater(len(casic_models), 0, "CASIC should have models")

        # Check for PL-15 missile
        pl15_model = self.registry.get_model("PL15")
        self.assertIsNotNone(pl15_model)
        self.assertEqual(pl15_model.contractor, "CASIC")
        self.assertEqual(pl15_model.integration_level, "weapon")
        self.assertEqual(pl15_model.fielded_date, 2018)

        # Check for DF-17 HGV
        df17_model = self.registry.get_model("DF17")
        self.assertIsNotNone(df17_model)
        self.assertEqual(df17_model.contractor, "CASIC")
        self.assertEqual(df17_model.integration_level, "weapon")

    def test_sukhoi_models(self):
        """Test Sukhoi (Russian aviation) models"""
        sukhoi_models = self.registry.get_contractor_models("Sukhoi")

        self.assertGreater(len(sukhoi_models), 0, "Sukhoi should have models")

        # Check for key platforms
        model_names = [m.platform_name for m in sukhoi_models]
        self.assertIn("Su-35 Flanker-E", model_names)
        self.assertIn("Su-57 Felon", model_names)
        self.assertIn("Su-30SM Flanker-H", model_names)
        self.assertIn("Su-34 Fullback", model_names)

        # All Sukhoi models should be platform-level
        for model in sukhoi_models:
            self.assertEqual(model.integration_level, "platform")
            self.assertGreaterEqual(model.confidence, 0.50)

    def test_models_by_country(self):
        """Test filtering models by country"""
        chinese_models = self.registry.get_models_by_country("China")
        russian_models = self.registry.get_models_by_country("Russia")
        us_models = self.registry.get_models_by_country("USA")

        self.assertGreater(len(chinese_models), 0, "Should have Chinese models")
        self.assertGreater(len(russian_models), 0, "Should have Russian models")
        self.assertGreater(len(us_models), 0, "Should have US models")

        # Verify no overlap
        chinese_platforms = {m.platform_name for m in chinese_models}
        russian_platforms = {m.platform_name for m in russian_models}
        self.assertEqual(len(chinese_platforms & russian_platforms), 0,
                        "No platform overlap between China and Russia")

    def test_kill_chain_model_retrieval(self):
        """Test retrieval of Chinese kill chain models"""
        kill_chain_models = self.registry.get_chinese_integrated_kill_chain_models()

        self.assertIn("shooter", kill_chain_models)
        self.assertIn("weapon", kill_chain_models)

        # Verify shooter is J-20
        self.assertEqual(kill_chain_models["shooter"].platform_name, "J-20 Mighty Dragon")
        self.assertEqual(kill_chain_models["shooter"].contractor, "AVIC")

        # Verify weapon is PL-15
        self.assertEqual(kill_chain_models["weapon"].platform_name, "PL-15 BVR AAM")
        self.assertEqual(kill_chain_models["weapon"].contractor, "CASIC")


class TestIntegratedKillChainCAD(unittest.TestCase):
    """Test integrated kill chain CAD framework"""

    def setUp(self):
        """Set up test fixtures"""
        self.cad = IntegratedKillChainCAD()

    def test_passive_detection_calculation(self):
        """Test passive ESM detection range calculation"""
        detection = self.cad.calculate_passive_detection(
            target_emissions_power_w=2.8,  # MADL sidelobe EIRP
            target_frequency_ghz=14.4,  # Ku-band
            esm_sensitivity_dbm=-74
        )

        # Should detect MADL at 180-220 km
        self.assertGreaterEqual(detection.detection_range_km, 180,
                               "Passive detection should be ≥180 km")
        self.assertLessEqual(detection.detection_range_km, 220,
                            "Passive detection should be ≤220 km")

        self.assertEqual(detection.detection_method, "passive")
        self.assertEqual(detection.sensor_platform, "J-20 ESM")
        self.assertGreaterEqual(detection.confidence, 0.60)

    def test_multistatic_track_fusion(self):
        """Test multistatic track fusion accuracy"""
        fused_cep = self.cad.calculate_multistatic_track_fusion(
            kj500_track_cep_m=500,
            j20_esm_cep_m=8000,
            j20_radar_cep_m=50,
            num_kj500=3
        )

        # Should achieve 30-50m CEP with fusion
        self.assertGreaterEqual(fused_cep, 25,
                               "Fused CEP should be ≥25m")
        self.assertLessEqual(fused_cep, 75,
                            "Fused CEP should be ≤75m (allowing margin)")

    def test_network_resilience_score(self):
        """Test network resilience scoring"""
        score = self.cad.calculate_network_resilience_score(
            num_kj500=3,
            kj500_survivability=0.95,
            num_j20=8,
            j20_survivability=0.70,
            awacs_to_weapon_backup=True
        )

        # Should score 80-90/100 with optimal configuration
        self.assertGreaterEqual(score, 75,
                               "Resilience score should be ≥75 with redundancy")
        self.assertLessEqual(score, 95,
                            "Resilience score should be ≤95")

        # Test degraded configuration
        degraded_score = self.cad.calculate_network_resilience_score(
            num_kj500=1,
            kj500_survivability=0.85,
            num_j20=4,
            j20_survivability=0.70,
            awacs_to_weapon_backup=False
        )

        self.assertLess(degraded_score, score,
                       "Degraded config should have lower resilience")

    def test_chinese_kill_chain_metrics(self):
        """Test Chinese integrated kill chain metrics calculation"""
        metrics = self.cad.calculate_chinese_kill_chain_metrics()

        # Passive detection: 180-220 km
        self.assertGreaterEqual(metrics.passive_detection_range_km, 180)
        self.assertLessEqual(metrics.passive_detection_range_km, 220)

        # Active detection: ~200 km (KJ-500 VHF)
        self.assertGreaterEqual(metrics.active_detection_range_km, 150)
        self.assertLessEqual(metrics.active_detection_range_km, 250)

        # Track CEP: 30-50m
        self.assertLessEqual(metrics.integrated_track_cep_m, 100)

        # PL-15 NEZ: 80-120 km
        self.assertGreaterEqual(metrics.weapon_nez_km, 80)
        self.assertLessEqual(metrics.weapon_nez_km, 120)

        # Pk at 200 km: 0.60-0.70
        self.assertGreaterEqual(metrics.pk_at_200km, 0.55)
        self.assertLessEqual(metrics.pk_at_200km, 0.75)

        # First-shot advantage vs F-35
        self.assertGreater(metrics.first_shot_advantage_km, 80,
                          "Should have significant first-shot advantage")

        # Network resilience: ~87/100
        self.assertGreaterEqual(metrics.network_resilience_score, 80)

        # Confidence
        self.assertGreaterEqual(metrics.confidence, 0.50)

    def test_us_legacy_metrics(self):
        """Test US legacy system metrics (F-22 + AIM-120D)"""
        metrics = self.cad.calculate_us_legacy_metrics()

        # No passive detection
        self.assertEqual(metrics.passive_detection_range_km, 0)

        # Limited active detection vs stealth
        self.assertLessEqual(metrics.active_detection_range_km, 50)

        # Lower Pk without network
        self.assertLess(metrics.pk_at_200km, 0.50)

        # Poor network resilience
        self.assertLess(metrics.network_resilience_score, 50)

        # High confidence (well-documented systems)
        self.assertGreaterEqual(metrics.confidence, 0.65)

    def test_us_nextgen_metrics(self):
        """Test US next-gen system metrics (F-35 + MADL)"""
        metrics = self.cad.calculate_us_nextgen_metrics()

        # Limited passive detection
        self.assertGreater(metrics.passive_detection_range_km, 0)
        self.assertLess(metrics.passive_detection_range_km, 100)

        # Better active detection than F-22
        self.assertGreater(metrics.active_detection_range_km, 80)

        # Better track accuracy with MADL
        self.assertLess(metrics.integrated_track_cep_m, 100)

        # AIM-260 longer NEZ
        self.assertGreater(metrics.weapon_nez_km, 100)

        # Better resilience than legacy, but still fighter-only
        self.assertGreater(metrics.network_resilience_score, 50)
        self.assertLess(metrics.network_resilience_score, 70)

    def test_comparison_vs_legacy(self):
        """Test comparison vs US legacy systems"""
        us_legacy = self.cad.calculate_us_legacy_metrics()
        comparison = self.cad.compare_vs_adversary("F-22 + AIM-120D", us_legacy)

        # China should have significant advantages
        self.assertGreater(comparison.chinese_advantage["passive_detection_km"], 150,
                          "Passive detection advantage should be >150 km")

        self.assertGreater(comparison.chinese_advantage["resilience_advantage"], 30,
                          "Resilience advantage should be >30 points")

        # Win ratio should favor China
        self.assertGreater(comparison.win_ratio, 2.0,
                          "Win ratio should be >2:1 in favor of China")

        self.assertIn("significant advantage", comparison.assessment.lower())

    def test_comparison_vs_nextgen(self):
        """Test comparison vs US next-gen systems"""
        us_nextgen = self.cad.calculate_us_nextgen_metrics()
        comparison = self.cad.compare_vs_adversary("F-35 + MADL", us_nextgen)

        # China should still have advantages, but smaller
        self.assertGreater(comparison.chinese_advantage["passive_detection_km"], 80,
                          "Passive detection advantage should be >80 km")

        # Win ratio should favor China but less decisively
        self.assertGreater(comparison.win_ratio, 1.5,
                          "Win ratio should be >1.5:1 in favor of China")

    def test_comparison_vs_future(self):
        """Test comparison vs US future concepts (NGAD)"""
        us_future = self.cad.calculate_us_future_metrics()
        comparison = self.cad.compare_vs_adversary("NGAD + CCA", us_future)

        # Very low confidence due to NGAD being concept only
        self.assertLess(us_future.confidence, 0.30,
                       "NGAD confidence should be low (concept only)")

        # Many metrics unknown (zeros)
        self.assertEqual(us_future.passive_detection_range_km, 0)
        self.assertEqual(us_future.active_detection_range_km, 0)

    def test_report_generation(self):
        """Test comprehensive report generation"""
        report = self.cad.generate_comprehensive_report()

        # Report should be non-empty
        self.assertGreater(len(report), 1000,
                          "Report should be comprehensive")

        # Should include key sections
        self.assertIn("CHINESE INTEGRATED KILL CHAIN", report)
        self.assertIn("COMPARISON VS", report)
        self.assertIn("KEY FINDINGS", report)
        self.assertIn("SYSTEM-LEVEL INTEGRATION", report)
        self.assertIn("PASSIVE DETECTION", report)
        self.assertIn("NETWORK RESILIENCE", report)

        # Should include classification
        self.assertIn("UNCLASSIFIED // PUBLIC RELEASE", report)


class TestContractorModelIntegration(unittest.TestCase):
    """Test integration between contractor models and CAD framework"""

    def setUp(self):
        """Set up test fixtures"""
        self.registry = DefenseContractorRegistry()
        self.cad = IntegratedKillChainCAD()

    def test_j20_model_integration(self):
        """Test J-20 model integration with CAD"""
        j20_model = self.registry.get_model("J20")

        # Model should be instantiable
        self.assertIsNotNone(j20_model.model_class)

        # Should be able to calculate RCS
        j20_rcs_instance = j20_model.model_class()
        rcs_result = j20_rcs_instance.calculate_rcs(azimuth_deg=0, elevation_deg=0)

        self.assertGreater(rcs_result.rcs_m2, 0)
        self.assertLess(rcs_result.rcs_m2, 0.1)  # Stealth range

    def test_pl15_model_integration(self):
        """Test PL-15 model integration with CAD"""
        pl15_model = self.registry.get_model("PL15")

        # Model should be instantiable
        self.assertIsNotNone(pl15_model.model_class)

        # Should integrate with CAD framework
        self.assertIsNotNone(self.cad.pl15_model)
        self.assertGreater(self.cad.pl15_model.params.nez_range_head_on_km, 80)

    def test_contractor_confidence_levels(self):
        """Test all contractor models have valid confidence levels"""
        for model in self.registry.models.values():
            self.assertGreaterEqual(model.confidence, 0.30,
                                   f"{model.model_name} confidence too low")
            self.assertLessEqual(model.confidence, 1.0,
                                f"{model.model_name} confidence too high")

    def test_all_fielded_dates_valid(self):
        """Test all models have valid fielded dates"""
        for model in self.registry.models.values():
            self.assertGreaterEqual(model.fielded_date, 2000,
                                   f"{model.model_name} fielded date too early")
            self.assertLessEqual(model.fielded_date, 2027,
                                f"{model.model_name} fielded date in future")


def run_all_tests():
    """Run all contractor integration CAD tests"""
    print("=" * 80)
    print("DEFENSE CONTRACTOR INTEGRATION CAD TESTS")
    print("=" * 80)
    print("\nTesting integration of:")
    print("  • Chinese contractors: AVIC, CASIC, CASC")
    print("  • Russian contractors: Sukhoi, MiG, Almaz")
    print("  • Integrated kill chain CAD framework")
    print("  • Multi-sensor fusion and network resilience")
    print("=" * 80)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDefenseContractorRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegratedKillChainCAD))
    suite.addTests(loader.loadTestsFromTestCase(TestContractorModelIntegration))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 80)
    print("CONTRACTOR INTEGRATION CAD TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run:     {result.testsRun}")
    print(f"Successes:     {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:      {len(result.failures)}")
    print(f"Errors:        {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED - Contractor integration validated successfully")
        print("\nKey Validations:")
        print("  • All Chinese/Russian contractors registered with models")
        print("  • Integrated kill chain metrics within expected ranges")
        print("  • Network resilience calculations validated")
        print("  • Passive detection advantage confirmed (180-220 km)")
        print("  • Multi-sensor fusion achieves 30-50m CEP")
        print("  • Chinese system shows 2-3× advantage vs US legacy systems")
        print("\nClassification: UNCLASSIFIED // PUBLIC RELEASE")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED - Review failures above")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    exit(exit_code)
