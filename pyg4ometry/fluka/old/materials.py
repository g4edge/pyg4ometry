import warnings
import itertools
import subprocess
import re



def map_materials_to_bdsim(materials):
    pass

def get_region_material_strings(ordered_regions, cards):
    """Given an ordered list of region names and a series of cards, map
    the region names to the material names.  Does not support
    index-based assignment.

    """
    # Map of region names to their Fluka material names.
    region_material_map = dict()
    for card in cards:
        if card.keyword != "ASSIGNMA":
            continue
        _warn_assignma(card)
        material_name = card.what1
        region_lower = card.what2
        region_upper = card.what3
        if region_lower not in ordered_regions:
            msg = ("At least one material is assigned to a region"
                   " that is not defined.  This is not necessarily a problem.")
            warnings.warn(msg)
            continue
        if region_upper is not None and region_upper not in ordered_regions:
            msg = ("In ASSIGNMA (material assignment):  Lower bound, \"{}\""
                   " corresponds to a defined region but upper, \"{}\""
                   " does not!  This is" " undefined behaviour.").format(
                       region_lower, region_upper)
            raise NameError(msg)

        # Steps must be ints or None, not merely floats with integer value.
        step = int(card.what4) if card.what4 is not None else None
        # Get the start and stop indices.
        # Slicing is exclusive on the upper bound so we have to add 1
        start_index = ordered_regions.index(region_lower)
        if region_upper != region_lower and region_upper != None:
            stop_index = ordered_regions.index(region_upper) + 1
        else:
            stop_index = start_index + 1

        for region_name in ordered_regions[start_index:stop_index:step]:
            region_material_map[region_name] = material_name

    return region_material_map


def _warn_assignma(card):
    material_name = card.what1
    lower_bound = card.what2
    upper_bound = card.what3
    field_present = card.what5
    if field_present is not None:
        msg = "Fields present in at least one region according to ASSIGNMA cards."
        warnings.warn(msg)

    def any_indices(columns):
        return any([is_index(column) for column in columns])

    if any_indices([lower_bound, upper_bound, material_name]):
        msg = "Index-based input not supported for material assignment."
        raise RuntimeError(msg)
    return _warn_assignma


def is_index(column):
    """Check if the column is an index (i.e coercable to int)."""
    # Do not necessarily support index-based input.  Best to warn than silently
    # and mysteriously fail.
    try:
        int(column)
        return True
    except:
        return False


def get_bdsim_materials():
    """Get the material name strings from the output of calling
    ``bdsim --materials".  This relies on there being a standard form
    of this output:
    - Between the two lines of asterisks there are the
    defined BDSIM materials.
    - Everywhere else, anything beginning with "G4_" is a material.

    """
    output = subprocess.check_output(["bdsim", "--materials"])
    g4_materials = re.findall('(G4_[A-Za-z0-9]+)', output)
    output = output.splitlines()
    # +1 to get past the line starting with '*', and +1 again to get
    # past the line starting with "Available materials are:"
    start_bdsim_materials = (i + 2
                             for i, line in enumerate(output)
                             if line.startswith('*')).next()
    # Take materials from the beginning of the BDSIM material
    # definitions until we reach a line starting with '*', where the
    # BDSIM material definitions are assumed to end.
    bdsim_materials = [material
                       for material
                       in itertools.takewhile(
                           lambda line: line.startswith('*') is False,
                           output[start_bdsim_materials:])]
    return set(bdsim_materials + g4_materials)
