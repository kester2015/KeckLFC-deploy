import pytest
from KeckLFC import parse_xml, KeckLFC

# Get the class
kecklfc = KeckLFC()
function_names = kecklfc.keywords
print(function_names)

# Define a test for each function name
@pytest.mark.parametrize("function_name", function_names)
def test_class_functions(function_name):
    assert hasattr(kecklfc, function_name), f"Function {function_name} is not defined in MyClass"