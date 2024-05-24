# The code in this file originally comes from the following article:
#
# IFC-graph for facilitating building information access and query
#
# Junxiang Zhu, Peng Wu *, Xiang Lei
#
# School of Design and the Built Environment, Curtin University,
# Bentley 6102, Western Australia, Australia
#
# The article was made available online 13 February 2023 in the journal
# Automation in Construction 148 (2023) 104778
#
# 0926-5805/© 2023 The Authors.
# Published by Elsevier B.V.
#
# This is an open access article under the CC BY license (http://creativecommons.org/licenses/by/4.0/).
#
# Some modifications have been made to the code.
#

import networkx as nx
from uuid import uuid4

def create_pure_node_from_ifc_entity(ifc_entity, ifc_file, hierarchy=True):
    node = {
        'id': ifc_entity.id() if ifc_entity.id() != 0 else str(uuid4()),
        'name': ifc_entity.is_a()
    }
    if hierarchy:
        labels = []
        for label in ifc_file.wrapped_data.types_with_super():
            if ifc_entity.is_a(label):
                labels.append(label)
        node['labels'] = labels
    else:
        node['labels'] = [ifc_entity.is_a()]
    
    attributes_type = ['ENTITY INSTANCE', 'AGGREGATE OF ENTITY INSTANCE', 'DERIVED']
    for i in range(ifc_entity.__len__()):
        if not ifc_entity.wrapped_data.get_argument_type(i) in attributes_type:
            name = ifc_entity.wrapped_data.get_argument_name(i)
            name_value = ifc_entity.wrapped_data.get_argument(i)
            node[name] = name_value
    return node

def create_graph_from_ifc_entity_all(graph, ifc_entity, ifc_file):
    node_id = ifc_entity.id() if ifc_entity.id() != 0 else str(uuid4())
    node_data = create_pure_node_from_ifc_entity(ifc_entity, ifc_file)
    graph.add_node(node_id, **node_data)
    for i in range(ifc_entity.__len__()):
        if ifc_entity[i]:
            if ifc_entity.wrapped_data.get_argument_type(i) == 'ENTITY INSTANCE':
                if ifc_entity[i].is_a() in ['IfcOwnerHistory'] and ifc_entity.is_a() != 'IfcProject':
                    continue
                else:
                    sub_node_id = ifc_entity[i].id() if ifc_entity[i].id() != 0 else str(uuid4())
                    sub_node_data = create_pure_node_from_ifc_entity(ifc_entity[i], ifc_file)
                    graph.add_node(sub_node_id, **sub_node_data)
                    graph.add_edge(node_id, sub_node_id, type=ifc_entity.wrapped_data.get_argument_name(i))
            elif ifc_entity.wrapped_data.get_argument_type(i) == 'AGGREGATE OF ENTITY INSTANCE':
                for sub_entity in ifc_entity[i]:
                    sub_node_id = sub_entity.id() if sub_entity.id() != 0 else str(uuid4())
                    sub_node_data = create_pure_node_from_ifc_entity(sub_entity, ifc_file)
                    graph.add_node(sub_node_id, **sub_node_data)
                    graph.add_edge(node_id, sub_node_id, type=ifc_entity.wrapped_data.get_argument_name(i))
    for rel_name in ifc_entity.wrapped_data.get_inverse_attribute_names():
        if ifc_entity.wrapped_data.get_inverse(rel_name):
            inverse_relations = ifc_entity.wrapped_data.get_inverse(rel_name)
            for wrapped_rel_entity in inverse_relations:
                rel_entity = ifc_file.by_id(wrapped_rel_entity.id())
                sub_node_id = rel_entity.id() if rel_entity.id() != 0 else str(uuid4())
                sub_node_data = create_pure_node_from_ifc_entity(rel_entity, ifc_file)
                graph.add_node(sub_node_id, **sub_node_data)
                graph.add_edge(node_id, sub_node_id, type=rel_name)
    return

def create_full_graph(graph, ifc_file):
    idx = 1
    length = len(ifc_file.wrapped_data.entity_names())
    for entity_id in ifc_file.wrapped_data.entity_names():
        entity = ifc_file.by_id(entity_id)
        print(idx, '/', length, entity)
        create_graph_from_ifc_entity_all(graph, entity, ifc_file)
        idx += 1
    return
