"""状态转移图，测试用"""

from .process_monitor import CallCategory

'''
1. a graph calls edges in different ways;
2. a state transfers to another state through an edge;
3. an edge may be expanded to a sub-graph;
'''

state_graph = {
    "main": {
        "parent": None,
        "nodes": [(0, 0, 'main_s0'), (1, 1, 'main_s1'), (2, 2, 'main_s2'), (3, 3, 'main_s3')],  # (index,group,node_tag)
        'edges': [(0, 1, "A", CallCategory.normal), (1, 2, "B", CallCategory.normal), (2, 3, "C", CallCategory.normal)],  # (from,
        # to,edge_tag, how edge is called)
    },
    "B": {
        "parent": ("main", "B", CallCategory.normal),  # (parent_graph, node_name_in_parent_graph, how_sub_graph_is_called)
        "nodes": [(0, 0, 'B_s0'), (1, 1, 'B_s1')],
        "edges": [(0, 1, "D", CallCategory.loop)],
    },
    "C": {
            "parent": ("main", "C"),
            "nodes": [(0, 0, 'C_s0'), (1, 1, 'C_s1')],
            "edges": [(0, 1, "E", CallCategory.concurrent)],
        }
}


status_graph = {
    "root": {
        "parent": None,
        "nodes": [(0, 0, 'root_s0'), (1, 1, 'root_s1')],
        'edges': [(0, 1, "main", CallCategory.cross_process)],
    },
    "main": {
        "name": "语义算法v 1.0.0",
        "parent": ("root", "main", CallCategory.cross_process),
        "nodes": [(0, 0, 'main_s0'), (1, 1, 'main_s1'), (2, 2, 'main_s2'), (3, 3, 'main_s3')],
        'edges': [(0, 1, "A", CallCategory.normal), (1, 2, "B", CallCategory.normal),
                  (2, 3, "C", CallCategory.normal)],  # (from,to,edge_tag, how edge is called)
    },
    "B": {
        "parent": ("main", "B", CallCategory.normal),
        # (parent_graph, node_name_in_parent_graph, how_sub_graph_is_called)
        "nodes": [(0, 0, 'B_s0'), (1, 1, 'B_s1')],
        "edges": [(0, 1, "D", CallCategory.normal)],
    },
    "C": {
        "parent": ("main", "C", CallCategory.normal),
        "nodes": [(0, 0, 'C_s0'), (1, 1, 'C_s1')],
        "edges": [(0, 1, "E", CallCategory.cross_process)],
    }
}

dependence_graph_2 = {
    "main": {
        "parent": None,
        "nodes": [(0, 0, 'A'), (1, 1, 'B'), (2, 2, 'C'), (3, 3, 'D'), (4, 1, 'E')],  # (index,group,node_tag)
        'edges': [(0, 1, "A_B"), (1, 2, "B_C"), (2, 3, "C_D"), (0, 4, "A_E"), (2, 3, "C_D"), (4, 3, "E_D")],
    },
}

state_graph_2 = {
    "main": {
        "parent": None,
        "nodes": [(0, 0, 'main_s0'), (1, 1, 'main_s1'), (2, 2, 'main_s2'), (3, 3, 'main_s3')],  # (index,group,node_tag)
        'edges': [(0, 1, "A", CallCategory.normal), (1, 2, "BCE", CallCategory.normal), (2, 3, "D", CallCategory.normal)],
    },
    "BCE": {
            "parent": ("main", "BCE", CallCategory.normal),
            "nodes": [(0, 0, 'BCE_s0'), (1, 1, 'BCE_1')],
            "edges": [(0, 1, "BCE_1", CallCategory.branch), (0, 1, "BCE_2", CallCategory.branch)],
    },
    "BCE_1": {
            "parent": ("BCE", "BCE_1", CallCategory.branch),
            "nodes": [(0, 0, 'BCE_1_s0'), (1, 1, 'BCE_1_s1'), (2, 2, 'BCE_1_s2')],
            "edges": [(0, 1, "B", CallCategory.normal), (1, 2, "C", CallCategory.normal)],
    },
    "BCE_2": {
            "parent": ("BCE", "BCE_2", CallCategory.branch),
            "nodes": [(0, 0, 'BCE_2_s0'), (1, 1, 'BCE_2_s1')],
            "edges": [(0, 1, "E", CallCategory.normal)],
    },
}
