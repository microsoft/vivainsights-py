
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Simulate a person-to-person network using the Watts-Strogatz model.

Organizational data fields are also simulated for `Organization`, `LevelDesignation`, and `City`
data frame with the same column structure as a person-to-person flexible query.
This has an edgelist structure and can be used directly as an input to `network_p2p()`.
"""

__all__ = ['p2p_data_sim']

import igraph
import pandas as pd

def p2p_data_sim(dim=1, size=300, nei=5, p=0.05):
    """Simulate a person-to-person network dataset.

    Generate a synthetic person-to-person edgelist using the Watts-Strogatz
    small-world model.  Organizational attributes (``Organization``,
    ``LevelDesignation``, ``City``) are simulated for both primary and
    secondary collaborators.  The output can be passed directly to
    ``network_p2p()``.

    Parameters
    ----------
    dim : int, default 1
        Dimension of the Watts-Strogatz lattice.
    size : int, default 300
        Number of nodes in the network.
    nei : int, default 5
        Number of neighbours each node is connected to in the lattice.
    p : float, default 0.05
        Rewiring probability.

    Returns
    -------
    pandas.DataFrame
        An edgelist DataFrame with columns for person IDs, organizational
        attributes, and a ``StrongTieScore`` column.

    Examples
    --------
    Generate a small simulated network:

    >>> import vivainsights as vi
    >>> sim = vi.p2p_data_sim(size=50)

    Customize the Watts-Strogatz parameters:

    >>> sim = vi.p2p_data_sim(size=100, dim=2, nei=3, p=0.1)
    """
    graph = igraph.Graph.Watts_Strogatz(dim=dim, size=size, nei=nei, p=p)
    edgelist = graph.get_edgelist()
    df = pd.DataFrame(edgelist, columns=["PrimaryCollaborator_PersonId", "SecondaryCollaborator_PersonId"])

    def add_cat(x, type):
        if type == "Organization":
            if x % 7 == 0:
                return "Org A"
            elif x % 6 == 0:
                return "Org B"
            elif x % 5 == 0:
                return "Org C"
            elif x % 4 == 0:
                return "Org D"
            elif x % 3 == 0:
                return "Org E"
            elif x < 100:
                return "Org F"
            elif x % 2 == 0:
                return "Org G"
            else:
                return "Org H"
        elif type == "LevelDesignation":
            return "Level " + str(x)[0]
        elif type == "City":
            if x % 3 == 0:
                return "City A"
            elif x % 2 == 0:
                return "City B"
            else:
                return "City C"

    df["PrimaryCollaborator_Organization"] = df["PrimaryCollaborator_PersonId"].apply(lambda x: add_cat(x, "Organization"))
    df["SecondaryCollaborator_Organization"] = df["SecondaryCollaborator_PersonId"].apply(lambda x: add_cat(x, "Organization"))
    df["PrimaryCollaborator_LevelDesignation"] = df["PrimaryCollaborator_PersonId"].apply(lambda x: add_cat(x, "LevelDesignation"))
    df["SecondaryCollaborator_LevelDesignation"] = df["SecondaryCollaborator_PersonId"].apply(lambda x: add_cat(x, "LevelDesignation"))
    df["PrimaryCollaborator_City"] = df["PrimaryCollaborator_PersonId"].apply(lambda x: add_cat(x, "City"))
    df["SecondaryCollaborator_City"] = df["SecondaryCollaborator_PersonId"].apply(lambda x: add_cat(x, "City"))
    df["PrimaryCollaborator_PersonId"] = df["PrimaryCollaborator_PersonId"].apply(lambda x: f"SIM_ID_{x}")
    df["SecondaryCollaborator_PersonId"] = df["SecondaryCollaborator_PersonId"].apply(lambda x: f"SIM_ID_{x}")
    df["StrongTieScore"] = 1

    return df