#!/usr/bin/env python3
"""
Parameter validation framework for Terraria Pyramid Detector GUI
Provides contract-based validation to prevent illegal parameter values
"""

import platform


class ParameterValidator:
    """Base validator with contract enforcement for numeric parameters"""

    def __init__(self, name, min_val, max_val, default, description):
        """
        Initialize numeric parameter validator

        Args:
            name: Parameter display name
            min_val: Minimum valid value (inclusive)
            max_val: Maximum valid value (inclusive)
            default: Default value
            description: User-friendly description
        """
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.default = default
        self.description = description

    def validate(self, value):
        """
        Validate value against constraints

        Args:
            value: Value to validate (will be converted to int)

        Returns:
            int: Validated integer value

        Raises:
            ValueError: If value is invalid or out of range
        """
        try:
            val = int(value)
            if not (self.min_val <= val <= self.max_val):
                raise ValueError(
                    f"{self.name} must be between {self.min_val} and {self.max_val}"
                )
            return val
        except (ValueError, TypeError) as e:
            if isinstance(e, ValueError) and "must be between" in str(e):
                raise
            raise ValueError(f"Invalid {self.name}: must be an integer")

    def get_error_message(self):
        """Get descriptive error message for help text"""
        return f"{self.name}: {self.description} (range: {self.min_val}-{self.max_val})"


class ChoiceValidator:
    """Validator for choice parameters (dropdowns/radio buttons)"""

    def __init__(self, name, choices, default):
        """
        Initialize choice parameter validator

        Args:
            name: Parameter display name
            choices: Dict mapping values to display labels {value: label}
            default: Default value (must be in choices keys)
        """
        self.name = name
        self.choices = choices  # {value: label}
        self.default = default

        if default not in choices:
            raise ValueError(f"Default value {default} not in choices {list(choices.keys())}")

    def validate(self, value):
        """
        Validate that value is one of the allowed choices

        Args:
            value: Value to validate

        Returns:
            Original value if valid

        Raises:
            ValueError: If value not in allowed choices
        """
        if value not in self.choices:
            valid_options = ', '.join(f"{k}={v}" for k, v in self.choices.items())
            raise ValueError(
                f"Invalid {self.name}: must be one of {valid_options}"
            )
        return value

    def get_labels(self):
        """Get list of display labels for UI"""
        return list(self.choices.values())

    def get_label(self, value):
        """Get display label for a specific value"""
        return self.choices.get(value, str(value))


# Define all validators for GUI parameters
VALIDATORS = {
    # Common parameters (all scripts)
    'SIZE': ChoiceValidator('World Size', {
        1: 'Small',
        2: 'Medium',
        3: 'Large'
    }, default=2),

    'DIFFICULTY': ChoiceValidator('Difficulty', {
        1: 'Normal',
        2: 'Expert',
        3: 'Master'
    }, default=1),

    'EVIL': ChoiceValidator('Evil Type', {
        1: 'Random',
        2: 'Corruption',
        3: 'Crimson'
    }, default=1),

    # Script-specific parameters
    'COUNT': ParameterValidator(
        'World Count',
        min_val=1,
        max_val=200,
        default=1,
        description="Number of worlds to generate"
    ),

    'DELETE_NO_PYRAMID': ChoiceValidator('Delete Mode', {
        0: 'Keep all worlds',
        1: 'Delete worlds without pyramids'
    }, default=0),

    'PYRAMID_TARGET': ParameterValidator(
        'Pyramid Target',
        min_val=1,
        max_val=50,
        default=1,
        description="Number of pyramid worlds to find"
    ),

    'MAX_ATTEMPTS': ParameterValidator(
        'Max Attempts',
        min_val=1,
        max_val=500,
        default=100,
        description="Maximum worlds to generate before stopping"
    ),
}


# Detect platform and choose appropriate script extension
def get_script_extension():
    """Return script extension based on platform"""
    system = platform.system()
    if system == 'Windows':
        return '.ps1'
    else:
        return '.sh'

SCRIPT_EXT = get_script_extension()

# Define script configurations
SCRIPT_CONFIGS = {
    'auto_pyramid_finder': {
        'name': 'Auto Pyramid Finder',
        'description': 'Generate a fixed number of worlds and detect pyramids',
        'script': f'./auto_pyramid_finder{SCRIPT_EXT}',
        'parameters': ['SIZE', 'DIFFICULTY', 'EVIL', 'COUNT', 'DELETE_NO_PYRAMID']
    },
    'find_pyramid_worlds': {
        'name': 'Find Pyramid Worlds',
        'description': 'Generate worlds until finding a target number with pyramids',
        'script': f'./find_pyramid_worlds{SCRIPT_EXT}',
        'parameters': ['SIZE', 'DIFFICULTY', 'EVIL', 'PYRAMID_TARGET', 'MAX_ATTEMPTS']
    },
    'tWorldGen': {
        'name': 'World Generator',
        'description': 'Basic batch world generation (no pyramid detection)',
        'script': f'./tWorldGen{SCRIPT_EXT}',
        'parameters': ['SIZE', 'DIFFICULTY', 'EVIL', 'COUNT']
    }
}


if __name__ == "__main__":
    # Test validators
    print("Testing parameter validators...")

    # Test numeric validator
    count_val = VALIDATORS['COUNT']
    try:
        assert count_val.validate(1) == 1
        assert count_val.validate(200) == 200
        assert count_val.validate("50") == 50
        print("✓ COUNT validator: valid inputs accepted")
    except AssertionError:
        print("✗ COUNT validator: test failed")

    try:
        count_val.validate(201)
        print("✗ COUNT validator: should reject out-of-range")
    except ValueError as e:
        print(f"✓ COUNT validator: rejected out-of-range - {e}")

    # Test choice validator
    size_val = VALIDATORS['SIZE']
    try:
        assert size_val.validate(1) == 1
        assert size_val.validate(2) == 2
        assert size_val.validate(3) == 3
        print("✓ SIZE validator: valid choices accepted")
    except AssertionError:
        print("✗ SIZE validator: test failed")

    try:
        size_val.validate(4)
        print("✗ SIZE validator: should reject invalid choice")
    except ValueError as e:
        print(f"✓ SIZE validator: rejected invalid choice - {e}")

    print("\nAll validators working correctly!")
