#-*- coding: utf-8 -*-

"""
rawrr2graph transforms data from a RAWRR JSON report into another JSON file
appropriate for importing into [GraphCommons](https://graphcommons.com).

Last tested using RAWRR v1.2.5 in english. Different languages require tweaking `SECTIONS_DATA`.

Usage:

    python3 rawrr2graph.py report.json > import_to_graphcommons.json
"""

import sys
import uuid
import datetime
import codecs
import json



# Unique IDs (automatic) and RGB colors (customizable) attributed to
# each section

SECTIONS_DATA = {
    u'RAWRR': {
        'uuid': str(uuid.uuid4()),
        'color': u'#5c5c00',
    },
    u'Assets': {
        'uuid': str(uuid.uuid4()),
        'color': u'#0000ff',
    },
    u'Activities': {
        'uuid': str(uuid.uuid4()),
        'color': u'#ff00ff',
    },
    u'Threats': {
        'uuid': str(uuid.uuid4()),
        'color': u'#005c5c',
    },
    u'Vulnerabilities': {
        'uuid': str(uuid.uuid4()),
        'color': u'#ff0000',
    },
    u'Recommendations': {
        'uuid': str(uuid.uuid4()),
        'color': u'#005c00',
    },
}

# ID and color of graph edges

EDGE_DATA = {
    'uuid': str(uuid.uuid4()),
    'color': u'#000000',
}


def rawrr2graph(rawrr_json):
    """
    Returns a string containing valid GraphCommons JSON data representing a RAWRR database.

    Parameters:

    - `rawrr_data`: string containing a JSON report of a RAWRR database
    """

    rawrr_data = json.loads(rawrr_json)

    # Adapted from a "reverse engineered" GraphCommons export

    graph = {
        'id': u'9a1fa433-0d37-4e6e-a035-90df3d09a7af',
        'name': u'RAWRR',
        'subtitle': None,
        'description': None,
        'updated_at': str(datetime.datetime.now()),
        'created_at': str(datetime.datetime.now()),
        'status': 0,
        'image': {
         'path': None,
         'ref_name': None,
         'ref_url': None,
        },
        # To be filled below
        'nodes': [
        ],
        # To be filled below
        'edges': [
        ],
        # To be filled below
        'nodeTypes': [],
        'edgeTypes': [
         {
            'id': EDGE_DATA['uuid'],
            'name': u'Edge',
            'name_alias': None,
            'description': None,
            'weighted': 1,
            'directed': 0,
            'durational': None,
            'color': EDGE_DATA['color'],
            'properties': [
            ]
         },
        ]
    }

    # Fills graph.nodeTypes through SECTIONS_DATAA

    for entry_type, entry_type_data in SECTIONS_DATA.items():
        graph['nodeTypes'] += [{
            'id': entry_type_data['uuid'],
            'name': entry_type,
            'name_alias': None,
            'description': None,
            'image': None,
            'color': entry_type_data['color'],
            'image_as_icon': False,
            'properties': [
            ],
            'hide_name': None,
            'size': u'metric_degree',
            'size_limit': 48
         }]

    # Intermediary storage for recording relations references

    rawrr = {
        u'RAWRR': {},
        u'Assets': {},
        u'Activities': {},
        u'Threats': {},
        u'Vulnerabilities': {},
        u'Recommendations': {},
    }


    # Central node; connects to all assets to prevent all graph from
    # fragmenting in clusters who move away from each other

    section_name = 'RAWRR'
    node = {
        'id': str(uuid.uuid4()),
        'type': section_name,
        'section_data': SECTIONS_DATA[section_name]['uuid'],
        'name': 'RAWRR',
        'description': '',
        'image': None,
        'reference': None,
        'properties': {
            'id': section_name + " " + 'RAWRR',
        },
    }
    rawrr[section_name]['RAWRR'] = node
    graph['nodes'].append(node)

    # Populates graph with section names as nodes

    for section in rawrr_data['sections']:
        section_name = section['sectionName']

        for entry in section['entries']:
            node = {
                'id': str(uuid.uuid4()),
                'type': section_name,
                'section_data': SECTIONS_DATA[section_name]['uuid'],
                'name': entry['title'],
                'description': entry['description'],
                'image': None,
                'reference': None,
                'properties': {
                    'id': section_name + " " + entry['title'],
                },
            }
            rawrr[section_name][entry['title']] = node
            graph['nodes'].append(node)



    # Links nodes which relate to each other among RAWRR sections

    for section in rawrr_data['sections']:
        section_name = section['sectionName']

        for entry in section['entries']:

            if section_name == 'Assets':
                # Links assets to "RAWRR" central node
                edge = {
                    'to': rawrr['RAWRR']['RAWRR']['id'],
                    'from': rawrr[section_name][entry['title']]['id'],
                    'name': u'Edge',
                    'section_data': EDGE_DATA['uuid'],
                    'id': str(uuid.uuid4()),
                    'user_id': u'e8bb1f96-5d22-4bc3-96d5-afc6af7940d0',
                    'weight': 1,
                    'directed': 1,
                    'properties': {
                    },
                }
                graph['edges'].append(edge)

            if section_name == 'Activities':
                # links each Activity to all its possible related Assets
                if entry['relatedAssets'] != 'None':
                    for asset in entry['relatedAssets']:
                        edge = {
                            'to': rawrr['Assets'][asset['assetName']]['id'],
                            'from': rawrr[section_name][entry['title']]['id'],
                            'name': u'Edge',
                            'section_data': EDGE_DATA['uuid'],
                            'id': str(uuid.uuid4()),
                            'user_id': u'e8bb1f96-5d22-4bc3-96d5-afc6af7940d0',
                            'weight': 1,
                            'directed': 1,
                            'properties': {
                            },
                        }
                        graph['edges'].append(edge)


            if section_name == 'Threats':
                # links each Threat to its possible related Asset
                if entry['relatedAsset'] != 'None':
                    edge = {
                        'to': rawrr['Assets'][entry['relatedAsset']]['id'],
                        'from': rawrr[section_name][entry['title']]['id'],
                        'name': u'Edge',
                        'section_data': EDGE_DATA['uuid'],
                        'id': str(uuid.uuid4()),
                        'user_id': u'e8bb1f96-5d22-4bc3-96d5-afc6af7940d0',
                        'weight': 1,
                        'directed': 1,
                        'properties': {
                        },
                    }
                    graph['edges'].append(edge)

            if section_name == 'Vulnerabilities':
                # Links each Vulnerability to its possible related Asset
                if entry['relatedAsset'] != 'None':
                    edge = {
                        'to': rawrr['Assets'][entry['relatedAsset']]['id'],
                        'from': rawrr[section_name][entry['title']]['id'],
                        'name': u'Edge',
                        'section_data': EDGE_DATA['uuid'],
                        'id': str(uuid.uuid4()),
                        'user_id': u'e8bb1f96-5d22-4bc3-96d5-afc6af7940d0',
                        'weight': 1,
                        'directed': 1,
                        'properties': {
                        },
                    }
                    graph['edges'].append(edge)

                # Links each Vulnerability to its possible related Activity
                #
                # "Acivity" is a typo that is in the source code
                if entry['relatedAcivity'] != 'None':
                    edge = {
                        'to': rawrr['Activities'][entry['relatedAcivity']]['id'],
                        'from': rawrr[section_name][entry['title']]['id'],
                        'name': u'Edge',
                        'section_data': EDGE_DATA['uuid'],
                        'id': str(uuid.uuid4()),
                        'user_id': u'e8bb1f96-5d22-4bc3-96d5-afc6af7940d0',
                        'weight': 1,
                        'directed': 1,
                        'properties': {
                        },
                    }
                    graph['edges'].append(edge)

                # Links each Vulnerability to its possible related Threats
                if entry['relatedThreats'] != 'None':
                    for threat in entry['relatedThreats']:
                        edge = {
                            'to': rawrr['Threats'][threat['threatName']]['id'],
                            'from': rawrr[section_name][entry['title']]['id'],
                            'name': u'Edge',
                            'section_data': EDGE_DATA['uuid'],
                            'id': str(uuid.uuid4()),
                            'user_id': u'e8bb1f96-5d22-4bc3-96d5-afc6af7940d0',
                            'weight': 1,
                            'directed': 1,
                            'properties': {
                            },
                        }
                        graph['edges'].append(edge)

            if section_name == 'Recommendations':
                # Links each Recommendation to its possible related Vulnerabilities
                if entry['relatedVulnerabilities'] != 'None':
                    for vulnerability in entry['relatedVulnerabilities']:
                        edge = {
                            'to': rawrr['Vulnerabilities'][vulnerability['vulnerabilityName']]['id'],
                            'from': rawrr[section_name][entry['title']]['id'],
                            'name': u'Edge',
                            'section_data': EDGE_DATA['uuid'],
                            'id': str(uuid.uuid4()),
                            'user_id': u'e8bb1f96-5d22-4bc3-96d5-afc6af7940d0',
                            'weight': 1,
                            'directed': 1,
                            'properties': {
                            },
                        }
                        graph['edges'].append(edge)

    return json.dumps({ 'graph': graph })

if __name__ == '__main__':
    with open(sys.argv[1], encoding='utf-8') as rawrr_file:
        rawrr_json = rawrr_file.read()
        graph_json = rawrr2graph(rawrr_json)
        print(graph_json)
