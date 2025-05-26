import warnings

from scipy.stats import pearsonr


def preprocess_java_test_files(t_files_list):
    """Preprocess test files into a dictionary for O(1) lookups."""
    test_files_map = {}
    test_keywords = ["Test", "Tests", "TestCase", "MockTest", "StubTest", "IT", "IntegrationTest"]

    for t_file in t_files_list:
        test_file_name = t_file.path.rpartition("/")[-1].replace(".java", "")

        # Extract the base name by removing test keywords
        base_name = test_file_name
        for keyword in test_keywords:
            if test_file_name.endswith(keyword):
                base_name = test_file_name[:-len(keyword)]
                test_files_map[base_name] = t_file
                break
            elif test_file_name.startswith(keyword):
                base_name = test_file_name[len(keyword):]
                test_files_map[base_name] = t_file
                break

    return test_files_map

def match_java_test_file_optimized(p_file_item, test_files_map):
    """Match production file to test file using dictionary lookup."""
    if p_file_item.language != "Java":
        return None

    production_file_name = p_file_item.path.rpartition("/")[-1].replace(".java", "")
    return test_files_map.get(production_file_name, None)

def match_javascript_test_file(p_file_item, t_files_list):
    """
    Match JavaScript production file to test file based on naming conventions.
    :param p_file_item:
    :param t_files_list:
    :return:
    """
    if p_file_item.language != "JavaScript":
        return False

    production_file_name = p_file_item.path.rpartition("/")[-1].replace(".js", "").replace(".ts", "")
    test_patterns = [
        f"{production_file_name}.test.js", f"{production_file_name}.spec.js",
        f"{production_file_name}.test.ts", f"{production_file_name}.spec.ts",
        f"{production_file_name}Tests.js", f"{production_file_name}Tests.ts",
        f"test_{production_file_name}.js", f"test_{production_file_name}.ts"
    ]

    for t_file in t_files_list:
        test_file_name = t_file.path.rpartition("/")[-1]
        if test_file_name in test_patterns:
            return t_file

    return False

def match_typescript_test_file(p_file_item, t_files_list):
    """
    Match TypeScript production file to test file based on naming conventions.
    :param p_file_item:
    :param t_files_list:
    :return:
    """
    if p_file_item.language != "TypeScript":
        return False

    production_file_name = p_file_item.path.rpartition("/")[-1].replace(".ts", "")
    test_patterns = [
        f"{production_file_name}.test.ts", f"{production_file_name}.spec.ts",
        f"{production_file_name}.test.js", f"{production_file_name}.spec.js"
    ]

    for t_file in t_files_list:
        test_file_name = t_file.path.rpartition("/")[-1]
        if test_file_name in test_patterns:
            return t_file

    return False

def match_python_test_file(p_file_item, t_files_list):
    """
    Match Python production file to test file based on naming conventions.
    :param p_file_item:
    :param t_files_list:
    :return:
    """
    if p_file_item.language != "Python":
        return False

    production_file_name = p_file_item.path.rpartition("/")[-1].replace(".py", "")
    test_patterns = [f"test_{production_file_name}.py", f"{production_file_name}_test.py"]

    for t_file in t_files_list:
        test_file_name = t_file.path.rpartition("/")[-1]
        if test_file_name in test_patterns:
            return t_file

    return False

def match_php_test_file(p_file_item, t_files_list):
    """
    Match PHP production file to test file based on naming conventions.
    :param p_file_item:
    :param t_files_list:
    :return:
    """
    if p_file_item.language != "PHP":
        return False

    production_file_name = p_file_item.path.rpartition("/")[-1].replace(".php", "")
    test_patterns = [f"{production_file_name}Test.php"]

    for t_file in t_files_list:
        test_file_name = t_file.path.rpartition("/")[-1]
        if test_file_name in test_patterns:
            return t_file

    return False

def match_c_sharp_test_file(p_file_item, t_files_list):
    """
    Match C# production file to test file based on naming conventions.
    :param p_file_item:
    :param t_files_list:
    :return:
    """
    if p_file_item.language != "C#":
        return False

    production_file_name = p_file_item.path.rpartition("/")[-1].replace(".cs", "")
    test_patterns = [f"{production_file_name}Tests.cs", f"{production_file_name}Test.cs"]

    for t_file in t_files_list:
        test_file_name = t_file.path.rpartition("/")[-1]
        if test_file_name in test_patterns:
            return t_file

    return False

def get_status_evolution(current_file, previous_files_list):
    """
    Determine the status of a file based on its current and previous versions.
    :param current_file:
    :param previous_files_list:
    :return:
    """
    if not current_file:
        return ""

    previous_file = next((f for f in previous_files_list if f.path == current_file.path), None)
    if not previous_file:
        return "Added"

    if current_file.loc != previous_file.loc:
        return "Modified"

    return "Clean"

def get_code_co_evolution(p_status, t_status):
    """
    Check if both production and test files have co-evolution statuses.
    :param p_status:
    :param t_status:
    :return:
    """
    co_evolution_statuses = ["Added", "Modified", "Deleted"]
    return p_status in co_evolution_statuses and t_status in co_evolution_statuses

def check_coevolution(series1, series2):
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("error", category=RuntimeWarning)
            return pearsonr(series1, series2)[0]
    except ValueError as e:
        print(f"ValueError: {e}")
        return -1
    except RuntimeWarning as e:
        print(f"RuntimeWarning: {e}")
        return -1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return -1