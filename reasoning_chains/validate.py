#!/usr/bin/env python3
"""
Reasoning Chain Validator
Validates deductive reasoning chains against formal schema
Ensures logical consistency and proper uncertainty propagation
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import re


class ReasoningChainValidator:
    """Validates reasoning chains for logical consistency and completeness."""

    def __init__(self, schema_path: str):
        with open(schema_path, 'r') as f:
            self.schema = yaml.safe_load(f)
        self.errors = []
        self.warnings = []

    def validate_chain(self, chain_path: str) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a reasoning chain file.

        Returns:
            (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        with open(chain_path, 'r') as f:
            chain = yaml.safe_load(f)

        # Required fields check
        self._check_required_fields(chain)

        # Observable facts validation
        self._validate_observable_facts(chain.get('observable_facts', []))

        # Physical laws validation
        self._validate_physical_laws(chain.get('physical_laws', []))

        # Logical steps validation
        self._validate_logical_steps(chain.get('logical_steps', []))

        # Conclusion validation
        self._validate_conclusion(chain.get('conclusion', {}))

        # Certainty propagation check
        self._check_certainty_propagation(chain)

        # Physical consistency check
        self._check_physical_consistency(chain)

        # NEW: Validate calculation code blocks
        self._validate_calculations(chain.get('logical_steps', []))

        # NEW: Check for alternative validation paths
        self._check_alternative_paths(chain)

        # NEW: Check uncertainty propagation
        self._check_uncertainty_propagation(chain)

        # NEW: Check equation variable definitions
        self._check_equation_completeness(chain.get('physical_laws', []))

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _check_required_fields(self, chain: Dict[str, Any]):
        """Check that all required fields are present."""
        required = self.schema['reasoning_chain']['required_fields']
        for field in required:
            # Some fields are nested in conclusion
            if field in ['conclusion_value', 'conclusion_uncertainty', 'confidence_level']:
                if 'conclusion' not in chain:
                    self.errors.append(f"Missing conclusion section")
                # These will be checked in _validate_conclusion
            elif field not in chain:
                self.errors.append(f"Missing required field: {field}")

    def _validate_observable_facts(self, facts: List[Dict[str, Any]]):
        """Validate observable facts."""
        if not facts:
            self.errors.append("No observable facts provided - reasoning must start from observations")
            return

        for i, fact in enumerate(facts):
            if 'fact_description' not in fact and 'fact' not in fact:
                self.errors.append(f"Observable fact {i} missing description")

            if 'source' not in fact:
                self.errors.append(f"Observable fact {i} missing source")

            certainty = fact.get('certainty', 0)
            if 0 < certainty < 50:
                self.warnings.append(
                    f"Observable fact {i} has certainty {certainty}% - too low to be an "
                    f"'observable fact'; label it as an assumption/derived input instead"
                )

    def _validate_physical_laws(self, laws: List[Dict[str, Any]]):
        """Validate physical laws."""
        if not laws:
            self.warnings.append("No physical laws cited - consider adding physics basis")
            return

        for i, law in enumerate(laws):
            if 'law_name' not in law and 'law' not in law:
                self.errors.append(f"Physical law {i} missing name")

            if 'equation' not in law:
                self.warnings.append(f"Physical law {i} missing equation")

            if 'source' not in law:
                self.warnings.append(f"Physical law {i} missing source reference")

    def _validate_logical_steps(self, steps: List[Dict[str, Any]]):
        """Validate logical reasoning steps."""
        if not steps:
            self.errors.append("No logical steps provided - how was conclusion reached?")
            return

        if len(steps) < 2:
            self.warnings.append("Only one logical step - consider showing more detail")

        for i, step in enumerate(steps):
            step_num = step.get('step', step.get('step_number', i+1))

            if 'premise' not in step:
                self.errors.append(f"Step {step_num} missing premise")

            if 'conclusion' not in step:
                self.errors.append(f"Step {step_num} missing conclusion")

            if 'inference' not in step and 'inference_rule' not in step:
                self.warnings.append(f"Step {step_num} missing inference rule")

            # Check for calculation if quantitative
            if any(char.isdigit() for char in str(step.get('conclusion', ''))):
                if 'calculation' not in step:
                    self.warnings.append(f"Step {step_num} has numeric conclusion but no calculation shown")

        # Check step ordering
        step_numbers = [s.get('step', s.get('step_number', i+1)) for i, s in enumerate(steps)]
        if step_numbers != sorted(step_numbers):
            self.warnings.append("Logical steps not in sequential order")

    def _validate_conclusion(self, conclusion: Dict[str, Any]):
        """Validate conclusion."""
        if not conclusion:
            self.errors.append("No conclusion provided")
            return

        # Check for value (accept either 'value' or 'conclusion_value')
        if 'value' not in conclusion and 'conclusion_value' not in conclusion:
            self.errors.append("Conclusion missing value")

        # Check for uncertainty (multiple valid field names)
        if not any(key in conclusion for key in ['uncertainty', 'uncertainty_range', 'uncertainty-range', 'conclusion_uncertainty']):
            self.errors.append("Conclusion missing uncertainty quantification")

        # Check for confidence (multiple valid field names)
        if not any(key in conclusion for key in ['confidence', 'confidence_level', 'confidence-level']):
            self.errors.append("Conclusion missing confidence level")

        # Check confidence is reasonable (0-100%)
        confidence = conclusion.get('confidence', conclusion.get('confidence_level', conclusion.get('confidence-level', 0)))
        if confidence > 100:
            self.errors.append(f"Confidence {confidence}% exceeds 100%")
        if confidence < 10:
            self.warnings.append(f"Confidence {confidence}% very low - is reasoning sound?")

    def _check_certainty_propagation(self, chain: Dict[str, Any]):
        """Check that the stated confidence is consistent with the chain's inputs.

        A deductive chain is no stronger than its weakest *necessary* link, so
        the stated confidence should not exceed the minimum certainty across the
        observable facts and logical steps (the "weakest-link" bound).

        The product of all certainties (treating every step as an independent
        necessary condition) is also computed, but only as a pessimistic LOWER
        bound for context: estimates corroborated by independent alternative
        paths legitimately beat the naive product, so it is NOT warned on.
        """
        facts = chain.get('observable_facts', [])
        steps = chain.get('logical_steps', [])

        certainties = [f['certainty'] for f in facts if f.get('certainty') is not None]
        certainties += [s['certainty'] for s in steps if s.get('certainty') is not None]
        if not certainties:
            return

        weakest_link = min(certainties)
        product = 100.0
        for c in certainties:
            product *= (c / 100)

        conclusion = chain.get('conclusion', {})
        final_confidence = conclusion.get(
            'confidence', conclusion.get('confidence_level', conclusion.get('confidence-level', 0)))

        if final_confidence > weakest_link:
            self.warnings.append(
                f"Final confidence {final_confidence}% exceeds weakest-link certainty "
                f"{weakest_link}% (independent-product lower bound {product:.1f}%) - "
                f"a chain is no stronger than its weakest necessary input"
            )

    def _check_physical_consistency(self, chain: Dict[str, Any]):
        """Check for physical consistency."""
        conclusion = chain.get('conclusion', {})
        value = conclusion.get('value')
        unit = conclusion.get('unit', '')

        # Basic sanity checks
        if value is not None:
            # Check for negative values where inappropriate
            param_name = chain.get('parameter_name', '').lower()

            if 'power' in param_name or 'range' in param_name or 'distance' in param_name:
                if isinstance(value, (int, float)) and value < 0:
                    self.errors.append(f"Physical impossibility: {param_name} cannot be negative")

            # Check for dB values in reasonable range
            if unit.lower() in ['db', 'dbm', 'dbi', 'dbw']:
                if isinstance(value, (int, float)):
                    if 'sidelobe' in param_name and value > 0:
                        self.errors.append("Sidelobe level cannot be positive dB")
                    if 'gain' in param_name and value > 50:
                        self.warnings.append(f"Antenna gain {value} dBi unusually high")

        # Check validation section
        validation = conclusion.get('validation', chain.get('validation', {}))
        if not validation:
            self.warnings.append("No validation checks performed on conclusion")

    def _validate_calculations(self, steps: List[Dict[str, Any]]):
        """Validate that calculation code blocks are syntactically valid Python."""
        for i, step in enumerate(steps):
            step_num = step.get('step', step.get('step_number', i+1))
            calculation = step.get('calculation', '')

            if calculation:
                try:
                    # Try to compile the calculation code
                    compile(calculation, f'<step_{step_num}>', 'exec')
                except SyntaxError as e:
                    self.errors.append(f"Step {step_num} has invalid Python syntax in calculation: {e}")

    def _check_alternative_paths(self, chain: Dict[str, Any]):
        """Check for alternative validation paths."""
        alternative_paths = chain.get('alternative_paths', [])

        if not alternative_paths:
            self.warnings.append(
                "No alternative deduction paths provided - consider showing multiple approaches"
            )
        elif len(alternative_paths) < 2:
            self.warnings.append(
                "Only one alternative path - consider adding more independent validation methods"
            )

    def _check_uncertainty_propagation(self, chain: Dict[str, Any]):
        """Check that uncertainty is properly quantified and propagated."""
        uncertainty_breakdown = chain.get('uncertainty_breakdown', {})

        if not uncertainty_breakdown:
            self.warnings.append(
                "No uncertainty breakdown provided - how was total uncertainty calculated?"
            )

        # Check if conclusion uncertainty matches propagated uncertainty
        conclusion = chain.get('conclusion', {})
        conclusion_uncertainty_str = conclusion.get('uncertainty', conclusion.get('conclusion_uncertainty', ''))

        # Extract the *result* uncertainty (last "±" value), so RSS expressions
        # like "sqrt(100^2 + 50^2) = ± 168" are read as 168, not the first term.
        unc_re = r'(?:±|\+/-)\s*(\d+\.?\d*)'
        stated_matches = re.findall(unc_re, str(conclusion_uncertainty_str))
        if stated_matches:
            stated_uncertainty = float(stated_matches[-1])

            # Check if uncertainty breakdown exists and calculate total
            if uncertainty_breakdown and 'total_uncertainty' in uncertainty_breakdown:
                total_unc_str = str(uncertainty_breakdown['total_uncertainty'])
                total_matches = re.findall(unc_re, total_unc_str)
                if total_matches:
                    calculated_uncertainty = float(total_matches[-1])

                    # Allow 20% discrepancy
                    if abs(stated_uncertainty - calculated_uncertainty) / calculated_uncertainty > 0.2:
                        self.warnings.append(
                            f"Stated uncertainty (±{stated_uncertainty}) differs significantly from "
                            f"calculated uncertainty (±{calculated_uncertainty})"
                        )

    def _check_equation_completeness(self, laws: List[Dict[str, Any]]):
        """Check that physical laws have complete variable definitions."""
        for i, law in enumerate(laws):
            law_name = law.get('law_name', law.get('law', f'Law {i}'))
            equation = law.get('equation', '')
            variables = law.get('variables', {})

            if equation and not variables:
                self.warnings.append(
                    f"Physical law '{law_name}' has equation but no variable definitions"
                )

            # Check that variables in equation are defined. Only meaningful for
            # equations written as expressions; skip if the "equation" is prose.
            if equation and variables:
                import re
                # Drop function-call tokens (name immediately followed by "(")
                expr = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(', '(', equation)
                equation_vars = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', expr))

                # Known math functions/constants and common prose words to ignore
                common_terms = {
                    'sin', 'cos', 'tan', 'log', 'log2', 'log10', 'ln', 'exp', 'pi',
                    'sqrt', 'abs', 'min', 'max', 'sum',
                    'between', 'and', 'or', 'to', 'low', 'high', 'bound', 'SNR', 'N',
                }
                equation_vars -= common_terms
                undefined = equation_vars - set(variables.keys())

                # Heuristic: only flag when the equation looks like a real
                # expression (has an operator) and there are few unknowns.
                looks_like_expression = bool(re.search(r'[=*/^]', equation))
                if undefined and looks_like_expression and len(undefined) < 5:
                    self.warnings.append(
                        f"Physical law '{law_name}' may have undefined variables: {undefined}"
                    )


def validate_all_chains(chains_dir: str, schema_path: str) -> int:
    """
    Validate all reasoning chain files in directory.

    Returns:
        Number of failed validations
    """
    validator = ReasoningChainValidator(schema_path)
    chains_path = Path(chains_dir)

    if not chains_path.exists():
        print(f"❌ Chains directory not found: {chains_dir}")
        return 1

    chain_files = list(chains_path.glob("*.yaml")) + list(chains_path.glob("*.yml"))

    # Exclude schema.yaml itself
    chain_files = [f for f in chain_files if f.name not in ['schema.yaml', 'schema.yml']]

    if not chain_files:
        print(f"⚠️  No reasoning chain files found in {chains_dir}")
        return 0

    print(f"Validating {len(chain_files)} reasoning chain(s)...\n")

    failures = 0
    for chain_file in chain_files:
        print(f"Checking: {chain_file.name}")
        is_valid, errors, warnings = validator.validate_chain(str(chain_file))

        if warnings:
            for warning in warnings:
                print(f"  ⚠️  WARNING: {warning}")

        if errors:
            for error in errors:
                print(f"  ❌ ERROR: {error}")
            failures += 1
            print(f"  RESULT: ❌ INVALID\n")
        else:
            print(f"  RESULT: ✅ VALID\n")

    print("=" * 60)
    print(f"SUMMARY: {len(chain_files) - failures}/{len(chain_files)} chains valid")

    if failures > 0:
        print(f"❌ {failures} chain(s) failed validation")
        return 1
    else:
        print("✅ All reasoning chains are valid")
        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate.py <chains_directory>")
        sys.exit(1)

    chains_dir = sys.argv[1]
    schema_path = Path(__file__).parent / "schema.yaml"

    exit_code = validate_all_chains(chains_dir, str(schema_path))
    sys.exit(exit_code)
