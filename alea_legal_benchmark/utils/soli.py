"""
Shared utilities for generating synthetic data using the SOLI ontology.
"""

# imports
import datetime

# packages
import numpy.random
from soli import SOLI, OWLClass

# get a module-level SOLI instance
G = SOLI()


def get_labels(cls: OWLClass) -> list[str]:
    """
    Get the set of labels for an OWL class.

    Args:
        cls (OWLClass): The OWL class.

    Returns:
        set[str]: A set of strings containing the labels.
    """
    labels = set()

    if cls.preferred_label:
        labels.add(cls.preferred_label)
    if cls.label:
        labels.add(cls.label)
    if len(cls.alternative_labels) > 0:
        labels.update(cls.alternative_labels)

    labels = {label for label in labels if not label.isupper()}

    return list(labels)


def sample_date() -> str:
    """
    Get a random date between 1975 and 2025.

    Returns:
        str: A string containing the date.
    """
    start_date = datetime.date(1975, 1, 1)

    # add a random number of days between 0 and 365.25 * 50
    max_days = int(365.25 * 50)
    days = numpy.random.randint(0, max_days)
    random_date = start_date + datetime.timedelta(days=days)

    return random_date.isoformat()


def sample_area_of_law() -> str:
    """
    Sample area of law for generating synthetic contract clauses based on Strategy 1.

    Returns:
        str: A string containing the area of law.
    """
    # get a random depth between 1-3
    depth = numpy.random.randint(1, 4)

    # get the areas of law up to the specified depth
    areas_of_law = G.get_areas_of_law(max_depth=depth)

    # sample one at random
    area_of_law: OWLClass = numpy.random.choice(areas_of_law)

    # get a random label
    labels = get_labels(area_of_law)

    # return a single label
    return str(numpy.random.choice(labels))


def sample_location() -> str:
    """
    Sample location for generating synthetic contract clauses based on Strategy 1.

    Returns:
        str: A string containing the location.
    """
    # get a random depth between 1-3
    depth = numpy.random.randint(1, 4)

    # get the locations up to the specified depth
    locations = G.get_locations(max_depth=depth)

    # sample one at random
    location: OWLClass = numpy.random.choice(locations)

    # get a random label
    labels = get_labels(location)

    # return a single label
    return str(numpy.random.choice(labels))


def sample_industry() -> str:
    """
    Sample industry for generating synthetic contract clauses based on Strategy 1.

    Returns:
        str: A string containing the industry.
    """
    # get a random depth between 1-3
    depth = numpy.random.randint(1, 4)

    # get the industries up to the specified depth
    industries = G.get_industries(max_depth=depth)

    # sample one at random
    industry: OWLClass = numpy.random.choice(industries)

    # get a random label
    labels = get_labels(industry)

    # return a single label
    return str(numpy.random.choice(labels))


def sample_clause_type() -> str:
    """
    Sample a child class from RDe0RKU39BlhcyACJW30ZLc to generate synthetic contract clauses based on Strategy 1.

    Returns:
        str: A string containing the clause type.
    """
    # depth
    depth = numpy.random.randint(1, 4)

    # get all clause types
    clause_types = G.get_children("RDe0RKU39BlhcyACJW30ZLc", max_depth=depth)

    # sample one at random
    clause_type: OWLClass = numpy.random.choice(clause_types)

    # get a random label
    labels = get_labels(clause_type)

    # return a single label
    return str(numpy.random.choice(labels))


def sample_doc_type() -> str:
    """
    Sample a child class from RBkL8I5saFF7mqpLTI7GxSh to generate synthetic documents based on Strategy 1.

    Returns:
        str: A string containing the clause type.
    """
    # depth
    depth = numpy.random.randint(1, 4)

    # get all document types
    doc_types = G.get_children("RBkL8I5saFF7mqpLTI7GxSh", max_depth=depth)

    # sample one at random
    doc_type: OWLClass = numpy.random.choice(doc_types)

    # get a random label
    labels = get_labels(doc_type)

    # return a single label
    return str(numpy.random.choice(labels))
