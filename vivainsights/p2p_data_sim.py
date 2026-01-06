
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Generate an person-to-person query / edgelist based on the graph according to the Watts-Strogatz
small-world network model. Organizational data fields are also simulated for `Organization`, `LevelDesignation`, and `City`
data frame with the same column structure as a person-to-person flexible query.
This has an edgelist structure and can be used directly as an input to `network_p2p()`.
"""

__all__ = ['p2p_data_sim']

import igraph
import pandas as pd

def p2p_data_sim(dim=1, size=300, nei=5, p=0.05):
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