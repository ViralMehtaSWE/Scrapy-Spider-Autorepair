from lxml.etree import HTMLParser
from lxml.etree import XMLParser
from lxml.etree import HTML
from lxml.etree import XML
from lxml.etree import tostring
from lxml.etree import parse
from lxml.etree import fromstring
from copy import deepcopy
from io import StringIO
from string import whitespace
from math import inf
from re import sub
from enum import Enum
from sklearn.metrics.pairwise import cosine_similarity
from scipy.optimize import linear_sum_assignment
from numpy import zeros
from numpy import array
from pickle import load
from pickle import dump


class State(Enum):
    wait_for_open_angular_bracket = 0
    wait_for_non_whitespace = 1
    wait_for_whitespace_or_close_angular_bracket = 2
    wait_for_close_angular_bracket = 3


class ParsingAndProcessing:
    path_to_data = None
    broken_code = None
    code = None
    tree = None
    tree_without_attr = None
    def __init__(self, path_to_data, parser):
        """
            This function takes in path_to_data
            (passed as an argument) from where
            code is read and parsed according to
            the parser = parser(passed as an argument).
            Parameters:
                1. path_to_data(type = string)
                2. parser(type = string)
            Example:
                >>> path1 = 'Examples/Old_Page_Hungarian.html'
                >>> Page(path1, 'html')
                <__main__.Page object at 0x000002093135A160>
                >>> 
        """
        self.path_to_data = path_to_data
        self.broken_code = self.get_data(path_to_data)
        if parser.lower() == 'xml':
            self.code = self.get_repaired_xml(broken_xml=self.broken_code)
            self.tree_without_attr = self.get_tree_without_attr_xml(code=self.code)
        elif parser.lower() == 'html':
            self.code = self.get_repaired_html(broken_html=self.broken_code)
            self.tree_without_attr = self.get_tree_without_attr_html(code=self.code)
        else:
            assert(False), "Invalid parser!"

    def get_repaired_xml(self, broken_xml):
        """
            This function takes in possibly broken XML,
            parses it and returns the parsed code.
            Parameters:
                1. broken_xml(type = string)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> broken_xml = '<div id = "ID"> Hello World <div>'
                >>> obj.get_repaired_xml(broken_xml)
                '<div id="ID"> Hello World <div/></div>'
                >>>  
        """
        parser = XMLParser(recover=True, remove_blank_text=True)
        tree = parse(StringIO(broken_xml), parser)
        self.code = str(tostring(tree.getroot(),
                        pretty_print=False).decode('utf-8'))
        self.tree = tree
        return self.code

    def get_tree_without_attr_xml(self, code):
        """
            This function takes in possibly broken code,
            removes the XML tag attributes, parses it
            and returns the parsed code in the form of an
            lxml.etree._ElementTree object. 
            Parameters:
                1. code(type = string)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> code = '<div id = "ID"> Hello World <div>'
                >>> tree = obj.get_tree_without_attr_xml(code)
                >>> tostring(tree)
                b'<div> Hello World <div/></div>'
                >>> 
        """
        parser = XMLParser(recover=True, remove_blank_text=True)
        code_without_attr = self.remove_tag_attributes(code=code)
        self.tree_without_attr = XML(code_without_attr, parser=parser)
        return self.tree_without_attr

    def get_repaired_html(self, broken_html):
        """
            This function takes in possibly broken HTML,
            parses it and returns the parsed code.
            Parameters:
                1. broken_html(type = string)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> broken_html = '<div id = "ID"> Hello World <div>'
                >>> obj.get_repaired_html(broken_html)
                '<html><body><div id="ID"> Hello World <div/></div></body></html>'
        """
        parser = HTMLParser(remove_blank_text=True)
        tree = parse(StringIO(broken_html), parser)
        self.code = str(tostring(tree.getroot(),
                        pretty_print=False).decode('utf-8'))
        self.tree = tree
        return self.code

    def get_tree_without_attr_html(self, code):
        """
            This function takes in possibly broken code,
            removes the HTML tag attributes, parses it
            and returns the parsed code in the form of an
            lxml.etree._ElementTree object. 
            Parameters:
                1. code(type = string)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> code = '<div id = "ID"> Hello World <div>'
                >>> tree = obj.get_tree_without_attr_html(code)
                >>> tostring(tree)
                b'<html><body><div> Hello World <div/></div></body></html>'
                >>> 
        """
        parser = HTMLParser(recover=True, remove_blank_text=True)
        code_without_attr = self.remove_tag_attributes(code=code)
        self.tree_without_attr = HTML(code_without_attr, parser=parser)
        return self.tree_without_attr

    def get_data(self, path):
        """
            This function reads the code(which can be 
            broken HTML) from a file present at a path
            specified by path(passed as an argument).
            Parameters:
                1. path(type = string)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> path = "Examples/1.html"
                >>> broken_code = obj.get_data(path)
                >>> broken_code
                '<html>\n    <body>\n        <p>Browsers usually insert quotation marks around the q element.</p>\n        <q>Build a future where people live in harmony with nature.</q>\n    </body>\n</html>\n'
                >>> 
        """
        try:
            with open(path, 'r') as file:
                broken_code = file.read()
        except:
            broken_code = ''
        return broken_code

    def remove_br(self, code):
        """
            This function removes all occurences of 
            various patters of the <br/> tag.
            Parameters:
                1. code(type = string)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> s = '<br/><br />...<br     /></ br><br>....'
                >>> obj.remove_br(s)
                '.......'
                >>> 
        """
        code = sub(r"<\s*br\s*>|<\s*br\s*/\s*>|<\s*/\s*br\s*>", "", code)
        return code

    def remove_tag_attributes(self, code):
        """
            This function removes tag attributes from HTML tags.
            Parameters:
                1. code(type = string)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> code = '<div id = "ID"> Hello World </div>'
                >>> obj.remove_tag_attributes(code)
                '<div> Hello World </div>'
                >>> 
        """
        lst = []
        state = State.wait_for_open_angular_bracket
        for ch in code:
            if(state == State.wait_for_open_angular_bracket):
                lst.append(ch)
                if ch == '<':
                    state = State.wait_for_non_whitespace
            elif(state == State.wait_for_non_whitespace):
                if not ch.isspace():
                    lst.append(ch)
                    state = State.wait_for_whitespace_or_close_angular_bracket
            elif(state == State.wait_for_whitespace_or_close_angular_bracket):
                if ch == '>':
                    state = State.wait_for_open_angular_bracket
                    lst.append(ch)
                elif not ch.isspace():
                    lst.append(ch)
                else:
                    state = State.wait_for_close_angular_bracket
            elif(state == State.wait_for_close_angular_bracket):
                if ch == '>':
                    state = State.wait_for_open_angular_bracket
                    lst.append(ch)
        code = ''.join(lst)
        return code

    def get_edit_distance(self, s1, s2):
        """
            This function returns the edit distance between two strings s1 and s2.
            Edit distance between strings s1 and s2 is the number of additions, 
            deletions or replacement in characters of s1 to make s1 equal to s2.
            Parameters:
                1. s1(type = string)
                2. s2(type = string)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> s1 = 'abcdef'
                >>> s2 = 'cefg'
                >>> obj.get_edit_distance(s1, s2)
                4
                >>>
        """
        s1 = self.remove_br(s1)
        s2 = self.remove_br(s2)
        s1 = ''.join([i for i in list(s1) if i not in whitespace])
        s2 = ''.join([i for i in list(s2) if i not in whitespace])
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2+1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1],
                                      distances[i1 + 1], distances_[-1])))
            distances = distances_
        return distances[-1]


class HungarianHelperMethods:
    def compute_cost(self, features1, features2, method = 'cosine-similarity'):
        """
            This function returns the compressed tree
            and a dic whose the keys are nodes in the tree
            and values are corresponding nodes in the compressed tree.
            All the nodes having just one child in tree are compressed
            to return the compressed tree. See example below.
            Parameters:
                1. features1(type = list of tuples)
                2. features1(type = list of tuples)
                3. method(type = string)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>')
                >>> subtree1 = tree[1][0]
                >>> subtree2 = tree[1][1]
                >>> features1 = obj.get_k_nearest_leaves(subtree1, 2)
                >>> features2 = obj.get_k_nearest_leaves(subtree2, 2)
                >>> cost = obj.compute_cost(features1, features2)
                >>> cost
                array([[-0.5]])
        """
        if method == 'cosine-similarity':
            features1 = [tostring(leaf).strip() for leaf, distance in features1]
            features2 = [tostring(leaf).strip() for leaf, distance in features2]
            combined_set = list(set(features1 + features2))
            features1 = set(features1)
            features2 = set(features2)
            features1 = array([int(leaf_str in features1) for leaf_str in combined_set]).reshape(1, -1)
            features2 = array([int(leaf_str in features2) for leaf_str in combined_set]).reshape(1, -1)
            return -cosine_similarity(features1, features2)

    def get_cost_matrix(self, data1, data2):
        """
            This function returns the cost matrix. See example below.
            Parameters:
                1. data1(type = list of tuples)
                2. data2(type = list of tuples)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>')
                >>> subtree1 = tree[1][0]
                >>> subtree2 = tree[1][1]
                >>> features1 = obj.get_k_nearest_leaves(subtree1, 2)
                >>> features2 = obj.get_k_nearest_leaves(subtree2, 2)
                >>> data1 = [('some subtree1', features1)]
                >>> data2 = [('some subtree2', features2)]
                >>> cost_matrix = obj.get_cost_matrix(data1, data1)
                >>> cost_matrix
                array([[-1.]])
                >>> 
        """
        cost_matrix = zeros((len(data1), len(data2)))
        i = 0
        j = 0
        for subtree1, features1 in data1:
            for subtree2, features2 in data2:
                cost_matrix[i][j] = self.compute_cost(features1, features2)
                j += 1
            i += 1
            j = 0
        return cost_matrix
    
    def get_min_cost_mapping(self, cost_matrix):
        """
            This function uses the hungarian algorithm
            to compute the minimum cost alignment. See example below.
            Parameters:
                1. cost_matrix(type = numpy.array/matrix like)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> cost_matrix = array([[0.1, 0.2, 0.7],[0.4, 0.6, 0.1]])
                >>> obj.get_min_cost_mapping(cost_matrix)
                array([0, 2], dtype=int64)
        """
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        return col_ind


class Page(ParsingAndProcessing, HungarianHelperMethods):
    path_to_subtree = None
    curr_path = None
    xpath_gen_path = None
    
    def __init__(self, path_to_data, parser):
        ParsingAndProcessing.__init__(self, path_to_data, parser)
        
    def retrieve_subtree(self, tree, path, cpy = True):
        """
            This function returns the subtree of tree(passed as an argument)
            which is present at path = path(passed as an argument) in the tree.
            Parameters:
                1. tree(type = lxml.etree._ElementTree)
                2. path(type = list/list like)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>').getroottree()
                >>> path = [1, 1]
                >>> subtree = obj.retrieve_subtree(tree, path)
                >>> tostring(subtree)
                b'<div>child3</div>'
                >>>
        """
        n = len(path)
        tree = tree.getroot()
        for i in range(n):
            tree = tree[path[i]]
        if cpy:
            return deepcopy(tree)
        else:
            return tree

    def assign(self, tree, subtree, path):
        """
            This function replaces the subtree present 
            at a location in the tree given by the path
            argument with the subtree passed to this function as a argument.
            Parameters:
                1. tree(type = lxml.etree._ElementTree)
                2. subtree(type = lxml.etree._Element)
                3. path(type = list/list like)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> xml_data_tree = '<div><div>child1</div><div>child2</div></div>'
                >>> xml_data_subtree = '<div>subtree</div>'
                >>> root_subtree = fromstring(xml_data_subtree)
                >>> tree = fromstring(xml_data_tree).getroottree()
                >>> path = [0]
                >>> tostring(obj.assign(tree, root_subtree, path))
                b'<div><div>subtree</div><div>child2</div></div>'
                >>>
        """
        tree = deepcopy(tree)
        ptr = tree
        n = len(path)
        tree = tree.getroot()
        for i in range(n-1):
            tree = tree[path[i]]
        tree[path[n - 1]] = deepcopy(subtree)
        return ptr

    def dfs(self, root, mn, str_subtree):
        """
            This function modifies self.path_to_subtree such that after this
            function executes, it contains the path to that subtree of the
            tree(whose root is passed as an argument)which has the smallest edit
            distance to the subtree passed as a string in the argument str_subtree.
            It modifies mn such that mn[0] contains the smallest edit distance.
            Parameters:
                1. root(type = lxml.etree._Element)
                2. mn(type = list of size exactly 1)
                3. str_subtree(type = list of size exactly 1 and str_subtree[0] is a string)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> obj.curr_path = []
                >>> obj.path_to_subtree = []
                >>> str_subtree = ['<div>child2</div>']
                >>> mn = [inf]
                >>> root = fromstring('<div><div>child1</div><div>child2</div></div>')
                >>> obj.dfs(root_tree, mn, str_subtree)
                >>> print(mn, obj.path_to_subtree)
                [0] [1]
                >>>
        """
        edit_dis = self.get_edit_distance(str_subtree[0],
                                          tostring(root,
                                          pretty_print=False).decode('utf-8'))
        if(edit_dis < mn[0]):
            mn[0] = edit_dis
            self.path_to_subtree = self.curr_path[:]
        n = len(root)
        for i in range(n):
            self.curr_path.append(i)
            self.dfs(root[i], mn, str_subtree)
            self.curr_path.pop()

    def get_subtree_path(self, subtree, tree):
        """
            This function returns the path to a subtree of the tree(passed as argument)
            such that edit distance between its string representation and the string
            representation of subtree(passed as an argument) is minimum. This function
            also returns this minimum edit distance.
            Parameters:
                1. subtree(type = lxml.etree._Element)
                2. tree(type = lxml.etree._Element)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> root_subtree = fromstring('<div>child2</div>')
                >>> root_tree = fromstring('<div><div>child1</div><div>child2</div></div>')
                >>> obj.get_subtree_path(root_subtree, root_tree)
                ([1], 0)
                >>>
        """
        self.path_to_subtree = []
        self.curr_path = []
        mn = [inf]
        str_subtree = str(tostring(subtree,
                          pretty_print=False).decode('utf-8'))
        str_subtree = [str_subtree]
        self.dfs(tree, mn, str_subtree)
        self.curr_path = []
        return (self.path_to_subtree, mn[0])

    def xpath_dfs(self, root, tree, xpaths):
        """
            This function populates xpaths(passed as an argument)
            with tuples of the form (list_path1, list_path2) where
            list_path1 is a path in root(passed as an argument)
            and list_path2 is a path in tree(passed as an argument)
            such that the string representation of the subtree present
            on list_path1 is equal to the string representation of the
            subtree present on list_path2.
            Parameters:
                1. root(type = lxml.etree._Element)
                2. tree(type = lxml.etree._Element)
                3. xpaths(type = list/list like)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> tree = fromstring('<div><div>child1</div><div>child2</div></div>')
                >>> root = fromstring('<div><div>child3</div><div>child1</div></div>')
                >>> xpaths = []
                >>> obj.xpath_gen_path = []
                >>> obj.xpath_dfs(root, tree, xpaths)
                >>> print(xpaths)
                [([1], [0])]
                >>> 
        """
        path_to_subtree, mn = self.get_subtree_path(root, tree)
        if mn == 0:
            xpaths.append((self.xpath_gen_path[:], path_to_subtree[:]))
            return
        n = len(root)
        for i in range(n):
            self.xpath_gen_path.append(i)
            self.xpath_dfs(root[i], tree, xpaths)
            self.xpath_gen_path.pop()

    def generate_XPaths(self, subtree, tree):
        """
            This function returns a list of tuples of the form
            (list_path1, list_path2) where list_path1 is a path in
            subtree(passed as an argument) and list_path2 is a path
            in tree(passed as an argument) such that the string
            representation of the subtree present on list_path1 is equal
            to the string representation of the subtree present on list_path2.
            Parameters:
                1. subtree(type = lxml.etree._Element)
                2. tree(type = lxml.etree._Element)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> tree = fromstring('<div><div>child1</div><div>child2</div></div>')
                >>> subtree = fromstring('<div><div>child3</div><div>child1</div></div>')
                >>> obj.generate_XPaths(subtree, tree)
                [([1], [0])]
                >>> 
        """
        xpaths = []
        self.xpath_gen_path = []
        self.xpath_dfs(subtree, tree, xpaths)
        return xpaths

    def get_repaired_subtree(self, xpaths, query_tree, tree):
        """
            This function uses xpaths(passed as an argument) to
            repair query_tree(passed as an argument) and returns
            the repaired query_tree. To do this, for each tuple t
            in xpaths, it calls appropriate function to replace the
            subtree present at path t[0] in query_treewith the subtree
            present at path t[1] in tree(passed as an argument).
            Parameters:
                1. xpaths(type = list of tuples)
                2. query_tree(type = lxml.etree._ElementTree)
                3. tree(type = lxml.etree._ElementTree)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> tree = fromstring('<div><div>child1</div><div>child2</div></div>').getroottree()
                >>> query_tree = fromstring('<div><div>child3</div><div>child4</div></div>').getroottree()
                >>> xpaths = [([0], [1]), ([1], [0])]
                >>> repaired_subtree = obj.get_repaired_subtree(xpaths, query_tree, tree)
                >>> tostring(repaired_subtree)
                b'<div><div>child2</div><div>child1</div></div>'
                >>> 
        """
        for xpath in xpaths:
            retrieved_subtree = self.retrieve_subtree(tree, xpath[1])
            query_tree = self.assign(query_tree, retrieved_subtree, xpath[0])
        return query_tree

    def compress_tree(self, tree, parent, idx_of_child, orig_tree, dic):
        """
            This function returns the compressed tree and populates the dic in
            such a way that the keys are nodes in the tree
            and values are corresponding nodes in the compressed tree.
            All the nodes having just one child in tree are compressed
            to return the compressed tree. See example below.
            Parameters:
                1. tree(type = lxml.etree._Element)
                2. parent(type = lxml.etree._Element)
                3. idx_of_child(type = int)
                4. orig_tree(type = lxml.etree._Element)
                5. dic(type = dict)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> tree = fromstring('<div><div><div><div>child1</div></div></div>\
                                      <div>child2</div></div>')
                >>> orig_tree = fromstring('<div><div><div><div>child1</div></div></div>\
                                      <div>child2</div></div>')
                >>> idx_of_child = 0
                >>> parent = -1
                >>> dic = {}
                >>> compressed_tree = obj.compress_tree(tree, parent, idx_of_child, orig_tree, dic)
                >>> tostring(compressed_tree)
                b'<div><div>child1</div><div>child2</div></div>'
                >>> 
        """
        dic[orig_tree] = tree
        n = len(tree)
        for i in range(n):
            self.compress_tree(tree[i], tree, i, orig_tree[i], dic)
        
        if parent != -1:
            if len(tree) == 1: 
                parent[idx_of_child] = tree[0]
        else:
            if len(tree) == 1:
                return tree[0]
            else:
                return tree

    def get_compressed_tree(self, tree):
        """
            This function returns the compressed tree
            and a dic whose the keys are nodes in the tree
            and values are corresponding nodes in the compressed tree.
            All the nodes having just one child in tree are compressed
            to return the compressed tree. See example below.
            Parameters:
                1. tree(type = lxml.etree._Element)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> tree = fromstring('<div><div><div><div>child1</div></div></div><div>child2</div></div>')
                >>> compressed_tree, dic = obj.get_compressed_tree(tree)
                >>> tostring(compressed_tree)
                b'<div><div>child1</div><div>child2</div></div>'
                >>> 
        """
        dic = dict()
        compressed_tree = deepcopy(tree)
        compressed_tree = self.compress_tree(compressed_tree, -1, 0, tree, dic)
        return compressed_tree, dic
    
    def get_k_nearest_leaves(self, subtree, k):
        """
            This function returns a list of tuples of type (leaf, distance_from_subtree).
            The leaves returned by this function are the k nearest leaves to the subtree.
            This function does a Breadth First Search from the root of the subtree until
            the  k nearest leaves are found.
            Parameters:
                1. subtree(type = lxml.etree._Element)
                2. k(type = int)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> ## Example 1:
                >>> tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>')
                >>> subtree = tree[1][0]
                >>> tostring(subtree)
                b'<div>child2</div>'
                >>> k_nearest_leaves = obj.get_k_nearest_leaves(subtree, 1)
                >>> print(k_nearest_leaves)
                [(<Element div at 0x1bc352c1308>, 2)]
                >>> print(tostring(k_nearest_leaves[0][0]))
                b'<div>child3</div>'
                >>>
                >>>## Example 2:
                >>> k_nearest_leaves = obj.get_k_nearest_leaves(subtree, 2)
                >>> print(k_nearest_leaves)
                [(<Element div at 0x1bc352c1308>, 2), (<Element div at 0x1bc352c11c8>, 3)]
                >>> print(tostring(k_nearest_leaves[0][0]))
                b'<div>child3</div>'
                >>> print(tostring(k_nearest_leaves[1][0]))
                b'<div>child1</div>'
        """
        queue = []
        visited = set([subtree])
        distances = dict()
        if subtree.getparent() is not None:
            queue.append(subtree.getparent())
            distances[subtree.getparent()] = 1
        k_nearest_leaves = []
        while len(queue) > 0 and len(k_nearest_leaves) < k:
            front = queue[0]
            parent = front.getparent()
            n = len(front)
            for i in range(n):
                if front[i] not in visited:
                    queue.append(front[i])
                    visited.add(front[i])
                    distances[front[i]] = distances[front] + 1
            if parent is not None and parent not in visited:
                queue.append(parent)
                visited.add(parent)
                distances[parent] = distances[front] + 1
            if len(front) == 0:
                k_nearest_leaves.append((front, distances[front]))
            queue.pop(0)
        return k_nearest_leaves
    
    def get_all_occurences_helper(self, tree, subtree, lst_occurences, path):
        """
            This function populates lst_occurences(passed as an argument)
            with tuples of the form, (subtree, path), where the
            first element of each tuple is a node N in tree(passed as an argument)
            such that the string representation of that node is equal
            to the string representation of subtree(passed as an argument)
            and the second element of each tuple is the path of the node N
            (described above) in tree.
            Parameters:
                1. tree(type = lxml.etree._Element)
                2. subtree(type = lxml.etree._Element)
                3. lst_occurences(type = list)
                4. path(type = list)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>')
                >>> subtree = fromstring('<div>child2</div>')
                >>> lst_occurences = []
                >>> path = []
                >>> get_all_occurences_helper(tree, subtree, lst_occurences, path)
                >>> print(tostring(lst_occurences[0][0]))
                b'<div>child2</div>'
                >>> print(lst_occurences[0][1])
                [1, 0]
                >>> print(len(lst_occurences))
                1
                >>> path
                []
                >>> 
        """
        if tostring(tree).strip() == tostring(subtree).strip():
            lst_occurences.append((tree, path[:]))
            return
        n = len(tree)
        for i in range(n):
            path.append(i)
            self.get_all_occurences_helper(tree[i], subtree, lst_occurences, path)
            path.pop()

    def get_all_occurences(self, tree, subtree):
        """
            This function returns a list of tuples of the form,
            (lxml.etree._Element, []), where the first element
            of each tuple is a node N in tree(passed as an argument)
            such that the string representation of that node is equal
            to the string representation of subtree(passed as an argument)
            and the second element of each tuple is the path of the node N
            (described above) in tree.
            Parameters:
                1. tree(type = lxml.etree._Element)
                2. subtree(type = lxml.etree._Element)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>')
                >>> subtree = fromstring('<div>child2</div>')
                >>> lst_occurences = obj.get_all_occurences(tree, subtree)
                >>> print(tostring(lst_occurences[0][0]))
                b'<div>child2</div>'
                >>> print(lst_occurences[0][1])
                [1, 0]
                >>> print(len(lst_occurences))
                1
                >>> 
        """
        lst_occurences = []
        path = []
        self.get_all_occurences_helper(tree, subtree, lst_occurences, path)
        return lst_occurences
    
    def get_k_nearest_leaves_for_all_subtrees(self, lst_occurences, k):
        """
            This function returns a list of tuples of the form
            ((subtree, (leaf, distance_from_subtree))). To do this,
            for each subtree in lst_occurences(passed as an argument),
            this function calls other appropriate functions to get
            the k(passed as an argument) nearest leaves and their
            distances from the subtree.
            Parameters:
                1. lst_occurences(type = list)
                2. k(type = int)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>')
                >>> lst_occurences = [tree[0]]
                >>> features = obj.get_k_nearest_leaves_for_all_subtrees(lst_occurences, 2)
                >>> print(features)
                [(<Element div at 0x1bc352a2748>, [(<Element div at 0x1bc352a2808>, 3), (<Element div at 0x1bc352a2648>, 3)])]
                >>> print(len(features))
                1
                >>> tostring(features[0][0])
                b'<div>child1</div>'
                >>> tostring(features[0][1][0][0])
                b'<div>child2</div>'
                >>> tostring(features[0][1][1][0])
                b'<div>child3</div>'
                >>> 
        """
        features = []
        for subtree in lst_occurences:
            features.append((subtree, self.get_k_nearest_leaves(subtree, k)))
        return features
    

    
    def get_new_page_compressed_subtree_path(self,
                                        compressed_subtree,
                                        compressed_old_tree,
                                        compressed_new_tree):
        """
            This function returns the path of the subtree
            S in compressed form of new_tree(passed as an
            argument) such that S is the most probable match
            for compressed_subtree (passed as an argument).
            See example below.
            Parameters:
                1. compressed_subtree(type = lxml.etree._Element)
                2. compressed_old_tree(type = lxml.etree._Element)
                3. compressed_new_tree(type = lxml.etree._Element)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> compressed_old_tree = fromstring('<html>\
                    <body>\
                        <div>\
                            <p>Username</p>\
                            <p>Password</p>\
                            <div>Submit</div>\
                        </div>\
                        <div>\
                        <div>\
                                <div>\
                                    <div>\
                                        <p>Username</p>\
                                        <p>Captcha1</p>\
                                        <p>Captcha2</p>\
                                    </div>\
                                </div>\
                            </div>\
                        </div> \
                        <p>This should not be extracted</p>\
                    </body>\
                </html>')
                >>> compressed_new_tree = fromstring('<html>\
                    <body>\
                        <div>\
                            <p>Username</p>\
                            <p>email</p>\
                        </div>\
                        <p>This should not be extracted</p>\
                        <div>\
                            <p>Hello World</p>\
                            <div>\
                                <p>Username</p>\
                                <p>Password</p>\
                            </div>\
                        </div>\
                    </body>\
                </html>')
                >>> subtree = compressed_old_tree[0][0][0]
                >>> tostring(subtree)
                b'<p>Username</p>            '
                >>> obj.get_new_page_compressed_subtree_path(subtree, compressed_old_tree, compressed_new_tree)
                [2, 1, 0]
        """
        lst_occurences_old, paths_old = zip(*self.get_all_occurences(compressed_old_tree, compressed_subtree))
        lst_occurences_new, paths_new = zip(*self.get_all_occurences(compressed_new_tree, compressed_subtree))
        features_old = self.get_k_nearest_leaves_for_all_subtrees(lst_occurences_old,
                                                                  k=2)
        features_new = self.get_k_nearest_leaves_for_all_subtrees(lst_occurences_new,
                                                                  k=2)
        cost_matrix = self.get_cost_matrix(data1=features_old, data2=features_new)
        mapping = self.get_min_cost_mapping(cost_matrix)
        idx = 0
        for subtree, _ in features_old:
            if subtree == compressed_subtree:
                break
            idx += 1
        assert(idx < len(features_old)), (idx, len(features_old))
        new_page_subtree_path = paths_new[mapping[idx]]
        return new_page_subtree_path
    
    def get_path_in_compressed_tree(self, subtree, old_tree, new_tree):
        """
            This function returns the path of the subtree
            (different from subtree argument) S in compressed
            form of new_tree(passed as an argument) such that 
            S is the most probable match for the compressed form
            of subtree(passed as an argument). See example below.
            Parameters:
                1. subtree(type = lxml.etree._Element)
                2. old_tree(type = lxml.etree._Element)
                3. new_tree(type = lxml.etree._Element)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> old_page = fromstring('<html>\
                    <body>\
                        <div>\
                            <p>Username</p>\
                            <p>Password</p>\
                            <div>Submit</div>\
                        </div>\
                        <div>\
                        <div>\
                                <div>\
                                    <div>\
                                        <p>Username</p>\
                                        <p>Captcha1</p>\
                                        <p>Captcha2</p>\
                                    </div>\
                                </div>\
                            </div>\
                        </div> \
                        <p>This should not be extracted</p>\
                    </body>\
                </html>')
                >>> new_page = fromstring('<html>\
                    <body>\
                        <div>\
                            <p>Username</p>\
                            <p>email</p>\
                        </div>\
                        <p>This should not be extracted</p>\
                        <div>\
                            <p>Hello World</p>\
                            <div>\
                                <p>Username</p>\
                                <p>Password</p>\
                            </div>\
                        </div>\
                    </body>\
                </html>')
                >>> subtree = old_page[0][0][0]
                >>> tostring(subtree)
                b'<p>Username</p>            '
                >>> obj.get_path_in_compressed_tree(subtree, old_page, new_page)
                [2, 1, 0]
        """
        compressed_old_tree, dic = self.get_compressed_tree(old_tree)
        compressed_new_tree, _ = self.get_compressed_tree(new_tree)
        while(len(subtree) == 1):
            subtree = subtree[0]
        compressed_old_subtree = dic[subtree]
        path_of_compressed_new_subtree = self.get_new_page_compressed_subtree_path(compressed_old_subtree,
                                                                      compressed_old_tree,
                                                                      compressed_new_tree)
        return path_of_compressed_new_subtree
    
    def get_path_in_uncompressed_tree_helper(self,
                                             tree,
                                             path_compressed,
                                             idx_compressed,
                                             path_in_new_tree,
                                             temp_path):
        """
            path_compressed(passed as an argument) is
            the path of a compressed subtree S in a compressed tree.
            This function populates path_in_new_tree
            (passed as an argument) with the path of the uncompressed
            form of subtree S in the uncompressed tree(passed as an argument).
            See example below.
            Parameters:
                1. tree(type = lxml.etree._Element)
                2. path_compressed(type = list)
                3. idx_compressed(type = int)
                4. path_in_new_tree(type = list)
                5. temp_path(type = list)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> tree = fromstring('<div><div><div><div>child1</div></div></div><div>child2</div></div>')
                >>> compressed_tree, dic = obj.get_compressed_tree(tree)
                >>> tostring(compressed_tree)
                b'<div><div>child1</div><div>child2</div></div>'
                >>> path_compressed = [0]
                >>> idx_compressed = 0
                >>> path_in_new_tree = []
                >>> temp = []
                >>> obj.get_path_in_uncompressed_tree_helper(tree, path_compressed, idx_compressed, path_in_new_tree, temp)
                >>> path_in_new_tree
                [[0]]
                >>> 
        """
        if idx_compressed == len(path_compressed):
            path_in_new_tree.append(deepcopy(temp_path))
            return
        n = len(tree)
        for i in range(n):
            if(n == 1):
                temp_path.append(i)
                self.get_path_in_uncompressed_tree_helper(tree[i],
                                                          path_compressed,
                                                          idx_compressed,
                                                          path_in_new_tree,
                                                          temp_path)
                temp_path.pop()
            else:
                if path_compressed[idx_compressed] == i:
                    temp_path.append(i)
                    self.get_path_in_uncompressed_tree_helper(tree[i],
                                                              path_compressed,
                                                              idx_compressed + 1,
                                                              path_in_new_tree,
                                                              temp_path)
                    temp_path.pop()

    def get_path_in_uncompressed_tree(self, subtree, old_tree, new_tree):
        """
            This function returns the path of the subtree
            (different from subtree argument) S new_tree
            (passed as an argument) such that S is the mos
            probable match for the subtree(passed as an
            argument). See example below.
            Parameters:
                1. subtree(type = lxml.etree._Element)
                2. old_tree(type = lxml.etree._Element)
                3. new_tree(type = lxml.etree._Element)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> old_page = fromstring('<html>\
                    <body>\
                        <div>\
                            <p>Username</p>\
                            <p>Password</p>\
                            <div>Submit</div>\
                        </div>\
                        <div>\
                        <div>\
                                <div>\
                                    <div>\
                                        <p>Username</p>\
                                        <p>Captcha1</p>\
                                        <p>Captcha2</p>\
                                    </div>\
                                </div>\
                            </div>\
                        </div> \
                        <p>This should not be extracted</p>\
                    </body>\
                </html>')
                >>> new_page = fromstring('<html>\
                    <body>\
                        <div>\
                            <p>Username</p>\
                            <p>email</p>\
                        </div>\
                        <p>This should not be extracted</p>\
                        <div>\
                            <p>Hello World</p>\
                            <div>\
                                <p>Username</p>\
                                <p>Password</p>\
                            </div>\
                        </div>\
                    </body>\
                </html>')
                >>> subtree = old_page[0][0][0]
                >>> tostring(subtree)
                b'<p>Username</p>            '
                >>> obj.get_path_in_compressed_tree(subtree, old_page, new_page)
                [2, 1, 0]
        """
        path_of_compressed_new_subtree = self.get_path_in_compressed_tree(subtree,
                                                                          old_tree,
                                                                          new_tree)
        path_in_new_tree = []
        self.get_path_in_uncompressed_tree_helper(new_tree,
                                                  path_of_compressed_new_subtree,
                                                  0,
                                                  path_in_new_tree,
                                                  [])
        return path_in_new_tree[0]

    def print_tree(self, tree):
        """
            This function prints the string representation
            of tree(passed as an argument)
            Parameters:
                1. tree(type = lxml.etree._Element or type = lxml.etree._ElementTree)
            Example:
                >>> path = 'Examples/Hello_World.html'
                >>> obj = Page(path, 'html')
                >>> tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>')
                >>> obj.print_tree(tree)
                <div>
                  <div>child1</div>
                  <div>
                    <div>child2</div>
                    <div>child3</div>
                  </div>
                </div>

                >>> 
        """
        print(tostring(tree, pretty_print=True).decode('utf-8'))


def equal(obj1, obj2):
    """
        This function checks if the contents of
        the two given objects are equal.
        Parameters:
            1. obj1(type = object)
            2. obj1(type = object)
        Example:
            >>> dic1 = {1:'1', 2: {'1': 5}}
            >>> dic2 = {2: {'1': 5}, 1:'1'}
            >>> equal(dic1, dic2)
            True
            >>> dic3 = {1:'1', 2: {'1': '5'}}
            >>> equal(dic1, dic3)
            False
            >>> 
    """
    if type(obj1) != type(obj2):
        return False
    primitive_types = [str, int, float, bool, None]
    if type(obj1) in primitive_types:
        return obj1 == obj2
    if type(obj1) is list or type(obj1) is tuple:
        if len(obj1) != len(obj2):
            return False
        for ch_obj1, ch_obj2 in zip(obj1, obj2):
            if not equal(ch_obj1, ch_obj2):
                return False
        return True
    elif type(obj1) is dict:
        keys1 = list(obj1.keys())
        keys2 = list(obj2.keys())
        keys1.sort()
        keys2.sort()
        if not equal(keys1, keys2):
            return False
        for key1, key2 in zip(keys1, keys2):
            if not equal(obj1[key1], obj2[key2]):
                return False
        return True
    else:
        attr1 = [getattr(obj1, str_attr1) for str_attr1 in dir(obj1) if not str_attr1.startswith('__')]
        attr2 = [getattr(obj2, str_attr2) for str_attr2 in dir(obj2) if not str_attr2.startswith('__')]
        return equal(attr1, attr2)


def detect_spider_failure(file_curr_extracted_data, file_old_extracted_data):
    try:
        with open(file_curr_extracted_data, 'rb') as file:
            curr_data = load(file)
    except Exception as e:
        print("Error occured while unpickling data", e)
        curr_data = []
    try:
        with open(file_old_extracted_data, 'rb') as file:
            old_data = load(file)
    except Exception as e:
        print("Error occured while unpickling data", e)
        old_data = []
    return equal(curr_data, old_data)


def show_demo():
    for i in range(1, 4):
        print('#'*50)
        print("\nBEGINNING OF EXAMPLE " + str(i) + "\n")
        path1 = "Examples/" + str(i) + ".html"
        path2 = "Examples/" + "query" + str(i) + ".html"
        tree_old_page = Page(path1,'html')
        query_tree_obj = Page(path2,'xml')
        print('Testing subtree extraction for example ' + str(i) + ' ...')
        path, mn = tree_old_page.get_subtree_path(query_tree_obj.
                                                  tree_without_attr,
                                                  tree_old_page.
                                                  tree_without_attr)
        subtree_retrieved = tree_old_page.retrieve_subtree(tree_old_page.tree,
                                                           path)
        print("Path is:", path, 'edit_distance:', mn)
        print("subtree found is:")
        print(tostring(subtree_retrieved, pretty_print=False).decode('utf-8'))
        print("-"*20)
        print('Testing XPath Generation for example ' + str(i) + ' ...')
        xpaths = tree_old_page.generate_XPaths(query_tree_obj.
                                               tree_without_attr,
                                               tree_old_page.tree_without_attr)
        print('xpaths =', xpaths)
        print("\nEND OF EXAMPLE " + str(i) + "\n")
        print('#'*50)


def show_auto_repair():
    print('#'*50)
    print("\nBEGINNING OF AUTO-REPAIR EXAMPLE\n")
    tree_obj1 = Page("Examples/New Layout Page1.html", 'html')
    tree_obj2 = Page("Examples/New Layout Page2.html", 'html')
    query_tree_obj = Page("Examples/Extracted Subtree from Old Layout.html", 'xml')
    xpaths = tree_obj1.generate_XPaths(query_tree_obj.tree_without_attr,
                                       tree_obj1.tree_without_attr)
    repaired_query_tree = tree_obj2.get_repaired_subtree(xpaths,
                                                         query_tree_obj.tree,
                                                         tree_obj2.tree)
    print("xpaths =", xpaths)
    print("repaired_query_tree =", tostring(repaired_query_tree,
          pretty_print=True).decode('utf-8'))
    print("\nEND OF AUTO-REPAIR EXAMPLE\n")
    print('#'*50)


def show_subtree_extraction_hungarian():
    print('#'*50)
    print('\nBEGINNING OF SUBTREE EXTRACTION DEMO BY MAXIMIZING JOINT PROBABILITY OF ALIGNMENT\n')
    path1 = 'Examples/Old_Page_Hungarian.html'
    path2 = 'Examples/New_Page_Hungarian.html'
    old_page = Page(path1, 'html')
    new_page = Page(path2, 'html')
    root_old_page = old_page.tree.getroot()
    root_new_page = new_page.tree.getroot()
    subtree = root_old_page[0][0][0]
    print("Sub-tree to be extracted:")
    old_page.print_tree(subtree)
    print("Path of subtree in new page:", old_page.get_path_in_uncompressed_tree(subtree, root_old_page, root_new_page))
    print('\nEND OF SUBTREE EXTRACTION DEMO BY MAXIMIZING JOINT PROBABILITY OF ALIGNMENT\n')
    print('#'*50)


class Demo:
    attr1 = 1
    attr2 = 2


def show_spider_failure_detection():
    print('#'*50)
    print('\nBEGINNING OF SPIDER FAILURE DETECTION\n')
    path = 'C:/Users/Viral Mehta/Desktop/Scrapy-Spider-Autorepair/Examples/'
    path1 = path + 'pickled_data1'
    path2 = path + 'pickled_data2'
    obj1 = Demo()
    obj2 = Demo()
    obj3 = Demo()
    obj4 = Demo()
    #Example 1
    l1 = [obj1, obj2]
    l2 = [obj3, obj4]
    with open(path1, 'wb') as f:
        dump(l1, f)
    with open(path2, 'wb') as f:
        dump(l2, f)
    print("When the extracted data and old data are the same, failure detector output:", detect_spider_failure(path1, path2))
    #Example 2
    l1[0].attr1=5
    with open(path1, 'wb') as f:
        dump(l1, f)
    print("When the extracted data and old data are different, failure detector output:", detect_spider_failure(path1, path2))
    print('\nBEGINNING OF SPIDER FAILURE DETECTION\n')
    print('#'*50)
    
show_demo()
show_auto_repair()
show_subtree_extraction_hungarian()
show_spider_failure_detection()
#path1 = 'Examples/Old_Page_Hungarian.html'
#obj = Page(path1, 'html')
