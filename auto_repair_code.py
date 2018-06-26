from lxml.etree import HTMLParser
from lxml.etree import XMLParser
from lxml.etree import HTML
from lxml.etree import XML
from lxml.etree import tostring
from lxml.etree import parse
from copy import deepcopy
from io import StringIO
from string import whitespace
from math import inf
from re import sub
from enum import Enum
from sklearn.metrics.pairwise import cosine_similarity
from scipy.optimize import linear_sum_assignment


class State(Enum):
    wait_for_open_angular_bracket = 0
    wait_for_non_whitespace = 1
    wait_for_whitespace_or_close_angular_bracket = 2
    wait_for_close_angular_bracket = 3


class Page:
    path_to_data = None
    path_to_subtree = None
    curr_path = None
    broken_code = None
    code = None
    xpath_gen_path = None

    def __init__(self, path_to_data):
        self.path_to_data = path_to_data

    def get_data(self, path):
        file = open(path)
        broken_code = file.read()
        return broken_code

    def remove_br(self, code):
        code = sub(r"<\s*br\s*>|<\s*br\s*/\s*>|<\s*/\s*br\s*>", "", code)
        return code

    def remove_tag_attributes(self, code):
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

    def retrieve_subtree(self, tree, path):
        n = len(path)
        tree = tree.getroot()
        for i in range(n):
            tree = tree[path[i]]
        return deepcopy(tree)

    def assign(self, tree, subtree, path):
        tree = deepcopy(tree)
        ptr = tree
        n = len(path)
        tree = tree.getroot()
        for i in range(n-1):
            tree = tree[path[i]]
        tree[path[n - 1]] = deepcopy(subtree)
        return ptr

    def dfs(self, root, mn, str_subtree):
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
        xpaths = []
        self.xpath_gen_path = []
        self.xpath_dfs(subtree, tree, xpaths)
        return xpaths

    def get_repaired_subtree(self, xpaths, query_tree, tree):
        for xpath in xpaths:
            retrieved_subtree = self.retrieve_subtree(tree, xpath[1])
            query_tree = self.assign(query_tree, retrieved_subtree, xpath[0])
        return query_tree

    def compress_tree(self, tree, parent, idx_of_child):
        n = len(root)
        for i in range(n):
            compress_tree(self, root[i], root, i)
        
        if parent != -1:
            if len(tree) == 1: 
                parent[idx_of_child] = tree[0]
        else:
            if len(tree) == 1:
                return tree[0]
            else:
                return tree

    def get_compressed_tree(self, tree):
        compressed_tree = deepcopy(tree)
        return compress_tree(compressed_tree, -1, 0)
    
    def get_k_nearest_leaves(self, subtree, k):
        # need to do BFS from subtree until the k nearest leaves are found.
        """This function returns a list of tuples of type (leaf, distance_from_subtree)."""
        queue = []
        visited = set([])
        distances = dict()
        distances[subtree] = 0
        if subtree.getparent is not None:
            queue.append(subtree.getparent())
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
                distances[front[i]] = distances[front] + 1
            if len(front) == 0:
                k_nearest_leaves.append((front, distances[front]))
            queue.pop(0)
        return k_nearest_leaves
    
    def get_all_occurences_recursive(self, tree, subtree, lst_occurences):
        if tostring(tree) == tostring(subtree):
            lst_occurences.append(tree)
        n = len(tree)
        for i in range(n):
            get_all_occurences_recursive(self, tree[i], subtree, lst_occurences)

    def get_all_occurences(self, tree, subtree):
        lst_occurences = []
        get_all_occurences_recursive(self, tree, subtree, lst_occurences)
        return lst_occurences
    
    def get_k_nearest_leaves_for_all_subtrees(self, lst_occurences, k):
        features = []
        for subtree in lst_occurences:
            features.append((subtree, get_k_nearest_leaves(self, subtree, k)))
        return features
    
    def compute_cost(self, features1, features2, method = 'cosine-similarity'):
        if method == 'cosine-similarity':
            features1 = [leaf for leaf, distance in features1]
            features2 = [leaf for leaf, distance in features2]
            combined_set = set(features1 + features2)
            features1 = np.array([int(leaf in combined_set) for leaf in features1]).reshape(1, -1)
            features2 = np.array([int(leaf in combined_set) for leaf in features2]).reshape(1, -1)
            return cosine_similarity(features1, features2)

    def get_cost_matrix(self, data1, data2):
        cost_matrix = np.zeros((len(data1), len(data2)))
        i = 0
        j = 0
        for subtree1, features1 in data1:
            for subtree2, features2 in data2:
                cost_matrix[i][j] = compute_cost(self, features1, features2)
                j += 1
            i += 1
        return cost_matrix
    
    def get_min_cost_mapping(self, cost_matrix):
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        return col_ind
    
    def get_new_page_compressed_subtree(self, compressed_subtree, compresses_old_tree, compressed_new_tree):
        lst_occurences_old = get_all_occurences(self, compresses_old_tree, subtree)
        lst_occurences_new = get_all_occurences(self, compresses_old_tree, subtree)
        features_old = get_k_nearest_leaves_for_all_subtrees(self, lst_occurences_old, k = 3)
        features_new = get_k_nearest_leaves_for_all_subtrees(self, lst_occurences_new, k = 3)
        cost_matrix = get_cost_matrix(self, data1 = features_old, data2 = features_new)
        mapping = get_min_cost_mapping(self, cost_matrix)
        idx = 0
        for subtree, _ in features_old:
            if subtree == compressed_subtree:
                break
            idx += 1
        new_page_subtree = features_new[mapping[idx][0]]
        return new_page_subtree
    
    def get_path_in_compressed_tree(self, subtree, old_tree, new_tree):
        compressed_old_subtree = get_compressed_tree(self, subtree)
        compresses_old_tree = get_compressed_tree(self, old_tree)
        compressed_new_tree = get_compressed_tree(self, new_tree)
        compressed_new_subtree = get_new_page_compressed_subtree(self, compressed_old_subtree, compresses_old_tree, compressed_new_tree)
        path_of_compressed_new_subtree = get_subtree_path(self, subtree = compressed_new_tree, tree = compressed_new_tree)
        return path_of_compressed_new_subtree
    
    def get_path_in_uncompressed_tree_helper(self, tree, path_compressed, idx_compressed, path_uncompressed, temp_path):
        if idx_compressed == len(path_compressed):
            path_uncompressed = temp_path[:]
            return
        n = len(tree)
        for i in range(n):
            if(n == 1):
                temp_path.append(i)
                get_path_in_uncompressed_tree_helper(self, tree[i], path_compressed, idx_compressed, path_uncompressed, temp_path)
                temp_path.pop()
            else:
                if path_compressed[idx_compressed] == i:
                    temp_path.append(i)
                    get_path_in_uncompressed_tree_helper(self, tree[i], path_compressed, idx_compressed + 1, path_uncompressed, temp_path)
                    temp_path.pop()

    def get_path_in_uncompressed_tree(self, subtree, old_tree, new_tree):
        path_of_compressed_new_subtree = get_path_in_compressed_tree(self, subtree, old_tree, new_tree)
        path_in_new_tree = []
        get_path_in_uncompressed_tree_helper(self, tree=new_tree,
                                             path_compressed=path_of_compressed_new_subtree,
                                             idx_compressed=0, path_uncompressed=path_in_new_tree,
                                             temp_path=[])
        return path_in_new_tree


class OldPage(Page):
    tree = None
    tree_without_attr = None

    def __init__(self, path_to_data):
        Page.__init__(self, path_to_data)
        self.broken_code = self.get_data(path_to_data)
        self.code = self.get_repaired_html(broken_html=self.broken_code)
        self.tree_without_attr = self.get_tree_without_attr(code=self.code)

    def get_repaired_html(self, broken_html):
        parser = HTMLParser(remove_blank_text=True)
        tree = parse(StringIO(broken_html), parser)
        self.code = str(tostring(tree.getroot(),
                        pretty_print=False).decode('utf-8'))
        self.tree = tree
        return self.code

    def get_tree_without_attr(self, code):
        parser = HTMLParser(recover=True, remove_blank_text=True)
        code_without_attr = self.remove_tag_attributes(code=self.code)
        self.tree_without_attr = HTML(code_without_attr, parser=parser)
        return self.tree_without_attr


class Sub_Tree(Page):
    tree = None
    tree_without_attr = None

    def __init__(self, path_to_data):
        Page.__init__(self, path_to_data)
        self.broken_code = self.get_data(path_to_data)
        self.code = self.get_repaired_xml(broken_xml=self.broken_code)
        self.tree_without_attr = self.get_tree_without_attr(code=self.code)

    def get_repaired_xml(self, broken_xml):
        parser = XMLParser(recover=True, remove_blank_text=True)
        tree = parse(StringIO(broken_xml), parser)
        self.code = str(tostring(tree.getroot(),
                        pretty_print=False).decode('utf-8'))
        self.tree = tree
        return self.code

    def get_tree_without_attr(self, code):
        parser = XMLParser(recover=True, remove_blank_text=True)
        code_without_attr = self.remove_tag_attributes(code=self.code)
        self.tree_without_attr = XML(code_without_attr, parser=parser)
        return self.tree_without_attr


def show_demo():
    for i in range(1, 4):
        print('#'*50)
        print("\nBEGINNING OF EXAMPLE " + str(i) + "\n")
        path1 = "Examples/" + str(i) + ".html"
        path2 = "Examples/" + "query" + str(i) + ".html"
        tree_old_page = OldPage(path1)
        query_tree_obj = Sub_Tree(path2)
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
    tree_obj1 = OldPage("Examples/New Layout Page1.html")
    tree_obj2 = OldPage("Examples/New Layout Page2.html")
    query_tree_obj = Sub_Tree(
                              "Examples/Extracted Subtree from Old Layout.html"
                              )
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


show_demo()
show_auto_repair()
