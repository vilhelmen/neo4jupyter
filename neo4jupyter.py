import uuid
import json
from IPython.display import HTML, Javascript, display
from collections.abc import Iterable

# Pull in vis.js
def initialize():
    display(Javascript(data="""
    require.config({
      paths: {
        vis: '//LOCAL_HOST_STRING_AAAAAAAAAA/static/vis_js/4.8.2/vis.min'
      }
    });
    require(['vis'], function(vis) {
      window.vis = vis;
    });""",css='https://LOCAL_HOST_STRING_AAAAAAAAAA/static/vis_js/4.8.2/vis.css'))


def vis_network(nodes, edges, options):
    base = \
"""
<div id="{id}" style="height: 600px;"></div>
<script type="text/javascript">
var nodes = {nodes};
var edges = {edges};

var container = document.getElementById("{id}");

var data = {{
    nodes: nodes,
    edges: edges
}};

var options = {options};

var network = new vis.Network(container, data, options);

</script>
"""

    unique_id = str(uuid.uuid4())
    html = base.format(id=unique_id, nodes=json.dumps(nodes), edges=json.dumps(edges), options=json.dumps(options))

    return HTML(html)


def get_node_vis_info(node, label_map):
    node_label = list(node.labels)[0]
    prop_key = label_map.get(node_label, '')
    vis_label = node.get(prop_key, '')

    # Title is mouseover text (change to object label by default?)
    # Label is printed text
    # Value is (optionally) used to node size.
    node_data = {'id': node.identity, 'group': node_label, 'value': 0}
    if vis_label:
        node_data['label'] = vis_label
        node_data['title'] = vis_label
    else:
        node_data['label'] = node_label
        node_data['title'] = node_label

    return node_data


def get_edge_vis_info(edge, node_map, label_map):
    #edge_label = list(edge.labels)[0] # WHY DOES THIS NOT WORK
    edge_label = next(iter(edge.types()))
    prop_key = label_map.get(edge_label, '')
    vis_label = edge.get(prop_key, '')

    # Title is mouseover text (change to object label by default?)
    # Label is printed text
    # ooh, could title labels [x] -> [y] and use the node label! I like it!
    edge_data = {'from': edge.start_node.identity, 'to': edge.end_node.identity}

    title = node_map[edge.start_node.identity]['label'] + " -[" + edge_label + "]-> " + node_map[edge.end_node.identity]['label']

    if vis_label:
        edge_data['label'] = vis_label
    if title: # I do realize this will always trigger in this version
        edge_data['title'] = title
    return edge_data

# Ellipses, pretty basic. Looks nice for small graphs
small_options = {
    "nodes": {
        "shape": "ellipse",
        "size": 25,
        "font": {
            "size": "14"
        }
    },
    "edges": {
        "font": {
            "size": 14,
            "align": "middle"
        },
        "color": {
            "color":"grey",
            "highlight": "#404040"
        },
        "arrows": {
            "to": {
                "enabled": True,
                "scaleFactor": 0.5
            }
        },
        "smooth": {
            "enabled": True,
            "type": "dynamic"
        }
    },
    "physics": {
        "enabled": False,
        "solver": "repulsion"
    }
}

# Dots. Unfortunately, labels are under the object, not within
#  so label backgrounds are turned on, though they look a bit gross.
# Dots scale with their value, with settings for pretty large graphs
# Looks absolutely terrible with small graphs.
large_options = {
    "nodes": {
        "scaling" : {
            "min": 10,
            "max": 800,
            "label": {
                "enabled": True,
                "min": 14,
                "max": 250
            },
        },
        "shape": "dot",
        "size": 25,
        "font": {
            "size": "14",
            "background": "white"
        }
    },
    "edges": {
        "font": {
            "size": 14,
            "align": "middle"
        },
        "color": {
            "color":"grey",
            "highlight":"#404040",
        },
        "arrows": {
            "to": {
                "enabled": True,
                "scaleFactor": 0.5
            }
        },
        "smooth": {
            "enabled": True,
            "type": "dynamic"
        }
    },
    "physics": {
        "enabled": False,
        "solver": "repulsion"
    }
}

def draw_mrn(data, label_map, physics=True, options=None):
    """
    Draw a graph of relationships m<-[r]->n

    Data: something iterable containing objects of form [m,r,n]
        Direction of r will be correctly detected. Duplicate edges are elided.
        M and n are really just a formality, take a look at draw_r to draw from relationships only.
    
    Physics: bool, whether to enable physics or not. Usually comes out as a big lump with physics off
    
    label_map: dict of naming settings. Maps the label to the property used to name it (ex: {"Page": "title"})
        Works for nodes and edges. Unresolved properties or labels will default to the empty string.
        Entities are named by their first label.

    Options: JS configuration dictionary. None to select a default
    """

    nodes = {}
    edges = {}

    for row in data:
        m_node = row[0]
        rel = row[1]
        n_node = row[2]

        if m_node.identity not in nodes:
                nodes[m_node.identity] = get_node_vis_info(m_node, label_map)
        else:
            nodes[m_node.identity]['value'] += 1

        if n_node.identity not in nodes:
            nodes[n_node.identity] = get_node_vis_info(n_node, label_map)
        else:
            nodes[m_node.identity]['value'] += 1

        # A reasonable check, why remove it I guess?
        if rel is not None:
            if rel.identity not in edges:
                edges[rel.identity] = get_edge_vis_info(rel, nodes, label_map)
            #edges.append({"from": source_info["id"], "to": target_info["id"], "label": next(iter(r.types()))})
            #edges.append({"from": rel.start_node.identity, "to": rel.end_node.identity, "label": ''})

    if options is None:
        options = small_options;
    options['physics']['enabled'] = physics
    return vis_network(list(nodes.values()), list(edges.values()), options)

def draw_nr(node_list, relationship_list, label_map, physics=True, options=None):
    """
    Draw a graph of nodes and their relationships.

    Node_list: something iterable containing nodes
    
    relationship_list: something iterable containing relationships
    
    Physics: bool, whether to enable physics or not. Usually comes out as a big lump with physics off
    
    label_map: dict of naming settings. Maps the label to the property used to name it (ex: {"Page": "title"})
        Works for nodes and edges. Unresolved properties or labels will default to the empty string.
        Entities are named by their first label.

    Options: JS configuration dictionary. None to select a default
    """

    nodes = {}
    edges = {}

    for n_node in node_list:
        if n_node.identity not in nodes:
            nodes[n_node.identity] = get_node_vis_info(n_node, label_map)

    for rel in relationship_list:
        if rel.start_node.identity not in nodes:
            nodes[rel.start_node.identity] = get_node_vis_info(rel.start_node, label_map)
        else:
            nodes[rel.start_node.identity]['value'] += 1

        if rel.end_node.identity not in nodes:
            nodes[rel.end_node.identity] = get_node_vis_info(rel.end_node, label_map)
        else:
            nodes[rel.end_node.identity]['value'] += 1

        if rel.identity not in edges:
            edges[rel.identity] = get_edge_vis_info(rel, nodes, label_map)

    if options is None:
        options = small_options;
    options['physics']['enabled'] = physics
    return vis_network(list(nodes.values()), list(edges.values()), options)

def draw_r(data, label_map, physics=True, options=None):
    """
    Draw a graph of relationships from edges

    Data: something iterable containing either a single edge per element or a list/tuple of edges.
        Duplicate edges are elided. Different functions return different layouts, this tries to make sense of them.
    
    label_map: dict of naming settings. Maps the label to the property used to name it (ex: {"Page": "title"})
        Works for nodes and edges. Unresolved properties or labels will default to the empty string.
        Entities are named by their first label.
    
    Physics: bool, whether to enable physics or not. Usually comes out as a big lump with physics off
    
    Options: JS configuration dictionary. None to select the default
    """

    nodes = {}
    edges = {}

    def extract_edge_data(rel):
        if rel.identity not in edges:
            
            m_node = rel.start_node
            n_node = rel.end_node
            
            if m_node.identity not in nodes:
                nodes[m_node.identity] = get_node_vis_info(m_node, label_map)
            else:
                nodes[m_node.identity]['value'] += 1

            if n_node.identity not in nodes:
                nodes[n_node.identity] = get_node_vis_info(n_node, label_map)
            else:
                nodes[m_node.identity]['value'] += 1
            
            edges[rel.identity] = get_edge_vis_info(rel, nodes, label_map)
            #edges.append({"from": source_info["id"], "to": target_info["id"], "label": next(iter(r.types()))})
            #edges.append({"from": rel.start_node.identity, "to": rel.end_node.identity, "label": ''})
    
    for row in data:
        # Edges identify themselves as iterable but they contain nothing. Cool. Whatever.
        # Everyone loves hardcoded types
        # to_table gives tuples, which either contains a single element or a list. Probably gets more complex, too.
        # data() returns something logical but complex so that's the user's problem
        
        # I'm going to try to parse at least the first level of craziness.
        # Anything more complex and the user can preprocess it >:C
        if isinstance(row,tuple):
            for elem in row:
                if isinstance(elem,list):
                    for rel in elem:
                        extract_edge_data(rel)
                else:
                    extract_edge_data(elem)
        else:
            extract_edge_data(row)

    if options is None:
        options = small_options;
    options['physics']['enabled'] = physics
    
    return vis_network(list(nodes.values()), list(edges.values()), options)