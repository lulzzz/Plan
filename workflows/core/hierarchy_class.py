import sys
import copy
import numpy as np
import pandas as pd
from slugify import slugify
from xml.etree.ElementTree import Element, SubElement


class PropagationTree:

    def __init__(self, data, levels):
        r'''Get tree out of pandas Data Frame
        self.levels: a list of field names in hierarchical order (root -> leaf)
        '''
        # global self.parent_map # children to parent nodes map of the tree
        self.parent_map = dict()
        self.levels = levels

        # Internal to class only
        self.level_map = dict() # node.find(string) has some issues with '.' string, therefore we have to slugify all that
        self.level_code_map = dict() # reverse key value of the self.level_map

        self.root = Element("root")

        # Init level elements mappings to their slugified counterparts
        for level in self.levels:
            self.level_map.update({level_elem:slugify(level_elem) for level_elem in data[level].unique()})
            self.level_code_map.update({tag:level_elem for level_elem, tag in self.level_map.items()})

        # Create root children based on data entries
        for __, entry in data.iterrows():

            # Append subnodes for every level of a given entry
            parent = self.root
            for level in self.levels:
                level_elem_tag = self.level_map[entry[level]]
                node = parent.find(level_elem_tag)
                if node is None:
                    node = Element(level_elem_tag)
                    parent.append(node)

                parent = node

            # Append leaf node with data
            parent.attrib['value'] = entry['value']
            parent.attrib['index'] = 1

        # Calculate tree values based on tree logic
        self.init_tree(self.root)

        # Get parent_map to get parent for each node
        self.parent_map = dict((c, p) for p in self.root.getiterator() for c in p)

    def init_tree(self, node):
        r'''Calculate values and mix for every node bottom up'''
        self.init_tree_value(node)
        self.init_tree_mix(node)
        self.init_tree_index(node)

    def init_tree_value(self, node):
        r'''Calculate values for every node bottom up'''
        if len(node) != 0:
            # Get node value with sum of subnodes
            s = 0
            for subnode in node:
                if subnode.get('value') is None:
                    s += self.init_tree_value(subnode)
                else:
                    s += subnode.attrib['value']

            node.attrib['value'] = s

        return node.attrib['value']

    def init_tree_mix(self, node):
        r'''Calculate mix (ratio) for every node bottom up'''
        node.attrib['mix'] = 1
        if len(node) != 0:
            # Get node mix
            values = list()
            for subnode in node:
                self.init_tree_mix(subnode)
                subnode.attrib['mix'] = subnode.attrib['value'] / self.root.attrib['value']
#                 subnode.attrib['mix'] = subnode.attrib['value'] / node.attrib['value']
                subnode.attrib['is_new_mix'] = False

    def init_tree_index(self, node):
        r'''Calculate index for every node bottom up'''
        if len(node.getchildren()) == 0:
            return

        # Init all subnodes
        for subnode in node:
            if subnode.get('index') is None:
                self.init_tree_index(subnode)

        self.update_node_index(node)

    def update_node_index(self, node):
        r'''Update node index based on children index'''
        if len(node.getchildren()) == 0:
            return

        different_index_flag = False
        prev_index = node.getchildren()[0].get('index')
        for subnode in node:
            if subnode.get('index') != prev_index:
                different_index_flag = True
                break
            prev_index = subnode.get('index')

        if different_index_flag:
            node.attrib['index'] = -1
        else:
            node.attrib['index'] = node.getchildren()[0].get('index')

    def get_sum(self, parent):
        r'''Compute sum of subnodes'''
        # if leaf
        if len(parent) == 0:
            return parent.attrib['value']

        s = 0
        for child in parent:
            s += child.attrib['value']
        return s

    def get_node(self, tags):

        if isinstance(tags, str):
            tags = [tags]

        node = self.root
        for tag in tags:
            node = node.find(tag)

        return node


    def value(self, tags, new_value=None):
        r'''Handle: Update a value of a given node and update linked nodes'''

        node = self.get_node(tags)
        if new_value is not None:
            self.update_value(node, new_value)

        return node.get('value')

    def update_value(self, node, new_value):
        r'''Handle: Update a value of a given node and update linked nodes'''
        node.attrib['value'] = new_value

        # Update parents
        self.update_parents(node)

        # Update children
        self.update_children(node)

        # Update mix on whole tree
        self.update_mix(self.root.getchildren())

    def update_children(self, parent):
        r'''Update all children value top down
        20
        10 10

        40
        20 (=40*mix) 20 (=40*mix)
        '''
        if len(parent) == 0:
            return

        # Get children updated values and clean them
        values = list()
        sum_local_mix = sum([child.get('mix') for child in parent])
        for child in parent:
            values.append(parent.get('value') * child.get('mix') / sum_local_mix)

        clean_values = self.largest_remainder_method(values, total=parent.get('value'))

        # Store children values
        for i, child in enumerate(parent):
            child.attrib['value'] = clean_values[i]

            # Update child index only if parent's index is existing
            # This allows to transmit an index modification at parent level to children
            if parent.get('index') is not None and parent.get('index') > -1:
                child.attrib['index'] = parent.get('index')

            self.update_children(child)

    def update_parents(self, node):
        # Get node's parent
        parent = self.parent_map.get(node)
        if parent is None:
            return

        # Update parent value
        parent.attrib['value'] = self.get_sum(parent)

        # Update parent index
        self.update_node_index(parent)

        self.update_parents(parent)

    def update_mix(self, level_nodes):
        r"""Update MIX of children top down"""

        if len(level_nodes) == 0:
            return

        for level_node in level_nodes:
            level_node.attrib['mix'] = level_node.get('value') / self.root.get('value')

        # Next level
        sublevel_nodes = list()
        for parent in level_nodes:
            sublevel_nodes.extend(parent.getchildren())
        self.update_mix(sublevel_nodes)

    def index(self, tags, index=None):
        r'''Modify index for a given node
        tags = a list of node tags'''

        node = self.get_node(tags)

        if index is not None:
            self.update_index(node, index)

        return node.attrib['index']

    def update_index(self, node, new_index):
        r'''Handle: Update index of a given node and update linked nodes
        relative to previous value'''
        if new_index == node.attrib['index'] or new_index == 1:
            return

        if node.attrib['index'] == -1 or node.attrib['index'] is None:
            multiplier = float(new_index)
        else:
            # Maybe no need this anymore
            # this takes into account the past value
            multiplier = float(new_index / node.attrib['index'])

        # Calculate new value with respect to new index
        new_value = node.attrib['value']*multiplier

        node.attrib['index'] = new_index
        self.update_value(node, new_value)




    def mix(self, node_tags, mix_list=None):
        r'''Handle: Update a mix of a given node and update linked nodes
        relative to previous value'''

        #     from [0.2, 0.2, [0.6]] (total remain: 0.4)
        #     we change 0.6 to 0.8
        #     we have [0.1, 0.1, [0.8]] (total remain: 0.2)
        #     the transformation is x0.5 (0.2/0.4) for the other mix

        # At level where modification takes place 1: insert new mix and update siblings' mix accordingly,
        # At level where modification takes place 2: calculate new values for all
        # At child level: update mix
        # At child level: update value

        # Insert new mix values at the right nodes
        for tags, new_mix in zip(node_tags, mix_list):

            # Find node
            node = self.get_node(tags)

            # Update new_mix flag
            if not self.is_different(node.attrib['mix'] - new_mix):
                continue

            node.attrib['mix'] = new_mix
            node.attrib['is_new_mix'] = True

        # Calculate mix of siblings
        self.calculate_mix(self.root.getchildren())

    def is_different(self, value):
        if -1e-4 < value < 1e-4:
            return 0
        return 1

    def calculate_mix(self, level_nodes):
        r"""Update non modified MIX of children and update values top down"""

        if len(level_nodes) == 0:
            return

        new_modified = 0 # Sum of modified mix values
        old_remain = 0 # Sum of mix not modified
        for child in level_nodes:
            if child.get('is_new_mix'):
                new_modified += child.get('mix')
            else:
                old_remain += child.get('mix')

        if new_modified > 0:
            if old_remain != 0:
                ratio_new_old = (1 - new_modified) / old_remain
            else:
                ratio_new_old = 1

            # Update old mix
            for child in level_nodes:
                if child.get('is_new_mix'):
                    # Consume flag
                    child.attrib['is_new_mix'] = False
                else:
                    child.attrib['mix'] = ratio_new_old * child.attrib['mix']

        else:
            # Recompute new mix according to parent and values
            new_mix = list()
            need_update = False
            for node in level_nodes:
                parent = self.parent_map.get(node)
                new_mix_sum = parent.get('mix')
                old_mix_sum = sum([node.get('mix') for node in parent])

                ratio = new_mix_sum / old_mix_sum
                if self.is_different(ratio - 1):
                    need_update = True
                    new_mix.append(ratio*node.get('mix'))

            if need_update:
                for i, node in enumerate(level_nodes):
                    node.attrib['mix'] = new_mix[i]

        # Get values relative to newly calculated mix and clean them
        values = list()
        for child in level_nodes:
            values.append(self.root.attrib['value'] * child.attrib['mix'])
        clean_values = self.largest_remainder_method(values, total=self.root.attrib['value'])

        for i, child in enumerate(level_nodes):
            # Update level node values
            child.attrib['value'] = clean_values[i]

        # Next level
        sublevel_nodes = list()
        for parent in level_nodes:
            sublevel_nodes.extend(parent.getchildren())
        self.calculate_mix(sublevel_nodes)

        # Update Parents
        for level_node in level_nodes:
            self.update_parents(level_node)

        self.update_mix(self.root.getchildren())



    # Get tree into pandas dataframe
    def get_row(self, node, target_level=-1, _d=dict(), _current_level=0):
        r'''Transform tree into list of dict representing rows'''

        _d['level_{}'.format(_current_level)] = node.tag

        if len(node) == 0 or target_level==_current_level:
            _d['mix'] = node.attrib['mix']
            _d['index'] = node.attrib['index']
            _d['value'] = node.attrib['value']
            return [_d.copy()]

        rows = list()
        for subnode in node:
            rows.extend(self.get_row(subnode, target_level, _d, _current_level+1))

        return rows

    def get_df(self, level=-1):
        r"""Returns Data Frame representing the tree"""
        node = self.root
        output = self.get_row(node, target_level=level, _d={})
        df_db = pd.DataFrame(output)
        del df_db['level_0']
        if level > -1:
            valid_levels = self.levels[:level]
        else:
            valid_levels = self.levels
        level_map = {'level_{}'.format(i+1): label for i, label in enumerate(valid_levels)}
        return df_db.rename(columns=level_map)

    def largest_remainder_method(self, numbers, total=100, ndigits=0):
        pad = 10**ndigits
        output = [round(number*pad, 0) for number in numbers]
        remainders = [number*pad - round(number*pad, 0) for number in numbers]
        to_distribute = int(total*pad - sum(output))
        for i in range(to_distribute):
            idx = np.argmax(remainders)
            output[idx] += 1
            remainders[idx] = 0

        output = [number / pad for number in output]
        return output

    def print_tree(self, node, level=-2, pad=1, counter=1):
        if level == -1:
            return ''

        s = '{}, {}, {:.2f}, {}'.format(node.tag, node.attrib['value'], node.attrib['mix'], node.get('index'))
        s += '\n' + ' '*pad*counter

        for subnode in node:
            s += self.print_tree(subnode, level-1, pad, counter+1)

        return s

    def show(self, level=-2, pad=1):
        s = self.print_tree(self.root, level=level, pad=pad)
        print(s)

    def __str__(self):
        return self.print_tree(self.root)
