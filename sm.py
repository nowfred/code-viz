import os
import sys
import re
import json

# NODE -> {'name': FILENAME, 'group': TOP-LEVEL-DIRECTORY, 'id':#}
# LINK -> {'source': SOURCE_NODE_ID, 'target':TARGET_NODE_ID}
# IDS  -> each file gets an id

def should_not_ignore(filename):
    '''
    Set to ignore !*.py files, __init__.py files, .pyc, and '0' containing
    migrations
    '''
    ignore_strings = ['__init__', '.pyc', '0']
    if '.py' not in filename:
        return False
    for ignore in ignore_strings:
        if ignore in filename:
            return False
    return True

def get_nice_extension(walk_dir, file_path,with_extension=False):
    '''
    Pretty prints the relative file path without the .py extension
    '''
    extension = file_path.replace(walk_dir+'/', '').replace('/','.')
    if not with_extension:
        extension = extension[:-3]
    return extension

def print_full_filename(walk_dir, sliced, file_path):
    '''
    Pretty prints the full filename AND function
    '''
    extension = get_nice_extension(walk_dir, file_path)
    t = sliced.replace('def ','').replace('(','')
    if 'init' not in t:
        return extension+'.'+t

def main():
    '''
    Run to create the code.json needed to source the vis
    '''

    walk_dir = '/Users/fred/Projects/TrackMaven/trackmaven/apps'

    # walk_dir = sys.argv[1]

    print('starting directory: ' + walk_dir)

    written_functions_list = []
    
    written_id_dict = {}
    
    # pattern: {location: function}
    imported_functions_list = []


    file_id_map = {}

    print('walk_dir (absolute) = ' + os.path.abspath(walk_dir))

    written_id = 1
    file_id = 1

    for root, subdirs, files in os.walk(walk_dir):
        for subdir in subdirs:
            # print('\t- subdirectory ' + subdir)
            pass
        for filename in files:
            if should_not_ignore(filename):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r') as f:
                    fileblock = f.read()
                    id_path = get_nice_extension(walk_dir, file_path)

                    uuu = id_path.replace('.','')

                    file_id_map.update({uuu:file_id})
                    file_id += 1

                    # Regex blocks to extract functions
                    imported_functions = re.compile("(?:from )(.*)")
                    defined_functions = re.compile("(def .*\()")
                    used_functions = re.compile("(?<!def)(\s|\.)(\w+)(?:\()")

                    multiline_imported = re.findall('from(.*)(?:import)(?:\s+\()(.{0,60})(?:\))',fileblock,re.DOTALL)
                    
                    # String indexes of the functions
                    import_index = re.finditer(imported_functions, fileblock)
                    df_index = re.finditer(defined_functions, fileblock)
                    used_index = re.finditer(used_functions, fileblock)
                    
                    # String index pairs
                    defined_function_indicies = [(m.start(0), m.end()) for m in df_index]
                    used_function_indicies = [(m.start(0), m.end()) for m in used_index]
                    imported_function_indicies = [(m.start(0), m.end()) for m in import_index]
                    
                    for f in imported_function_indicies:
                        section = fileblock[f[0]:f[1]]
                        # 'From' also appears in docstrings...
                        try:
                            split = section.split(' import ')
                            start = split[0].replace('from ','')
                            ends = split[1].split(', ')
                            imported_functions = [start+'.'+end for end in ends]
                            for a in imported_functions:
                                #print a
                                if '(' in a:
                                    continue
                                else:
                                    if a is not None:
                                        nice = get_nice_extension(walk_dir, file_path)
                                        imported_functions_list.append({nice:a})
                        except:
                            pass

                    #for f in multiline_imported:
                    #    print f

                    # for f in defined_function_indicies:
                    #     section = fileblock[f[0]:f[1]]
                    #     name = print_full_filename(walk_dir, section, file_path)
                    #     new = {name:written_id}
                    #     written_id_dict.update(new)
                    #     written_functions_list.append(name)

                    # for f in used_function_indicies:
                    #     section = fileblock[f[0]:f[1]]
                    #     name = print_full_filename(walk_dir, section, file_path)

    unique_list = {}
    real_links = []
    real_nodes = []

    #print imported_functions_list

    for f in imported_functions_list:
        for f2 in written_functions_list:
            if f.values()[0] == f2:
                try:
                    to = f.values()[0].strip().rsplit('.',1)[0].replace('.','')
                    to_nice = f.values()[0].strip().rsplit('.',1)[0]
                    to_id = file_id_map.get(to)

                    frm = f.keys()[0].strip().replace('.','')
                    frm_nice = f.keys()[0].strip()
                    frm_id = file_id_map.get(frm)

                    unique_list.update({to_nice: to_id})
                    unique_list.update({frm_nice: frm_id})
                    print 'source: {}'.format(frm_nice)
                    print 'target: {}'.format(to_nice)

                    real_links.append({"source":frm_id, "target":to_id, "value":5})
                except:
                    pass
            elif f.keys()[0] == f2:
                try:
                    frm = f.values()[0].strip().rsplit('.',1)[0].replace('.','')
                    frm_nice = f.values()[0].strip().rsplit('.',1)[0]
                    frm_id = file_id_map.get(frm)

                    to = f.keys()[0].strip().replace('.','')
                    to_nice = f.keys()[0].strip()
                    to_id = file_id_map.get(to)

                    
                    unique_list.update({to_nice: to_id})
                    unique_list.update({frm_nice: frm_id})

                    print 'source: {}'.format(frm_nice)
                    print 'target: {}'.format(to_nice)

                    real_links.append({"source":frm_id, "target":to_id, "value":5})
                except:
                    pass
    
    for key, value in unique_list.iteritems():
        real_nodes.append({"name":key, "id": value})

    for node in real_nodes:
        count = 0
        for link in real_links:
            if node['id'] == link['source'] or node['id'] == link['target']:
                count += 1
        node['connections'] = count

    #print real_nodes



    complete = {"nodes": real_nodes, "links": real_links}

    #with open('code.json', 'w') as w:
    #    w.write(json.dumps(complete))