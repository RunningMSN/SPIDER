import os

def parse_list(list):
    """
    Parses individual assemblies from a provided list.

    Arguments:
        list -- Text file where each assembly is specified on a new line

    Return:
        lines -- List of individual assemblies
        errors -- List of assemblies that coudl not be found
    """
    with open(list, "r") as assembly_list:
        lines = assembly_list.readlines()
        lines = [line.strip() for line in lines]
    return lines

def list_exists(list):
    """
    Checks to make sure all assemblies in the provided list exist.

    Arguments:
        list -- List of assemblies from parse_list function.

    Return:
        True/False -- Returns true if all files in list exist.
    """
    errors = []
    for item in list:
        if not os.path.exists(item):
            errors.append(item)
    if len(errors) > 0:
        return False, errors
    else:
        return True, errors