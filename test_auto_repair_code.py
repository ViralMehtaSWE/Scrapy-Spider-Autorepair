from auto_repair_code import Page
from auto_repair_code import equal
from auto_repair_api import get_prefix_path, get_paths, get_subtrees_to_be_extracted, auto_repair, auto_repair_lst
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

def test_get_repaired_xml():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    broken_xml = '<div id = "ID"> Hello World <div>'
    assert(obj.get_repaired_xml(broken_xml) == '<div id="ID"> Hello World <div/></div>')

def test_get_tree_without_attr_xml():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    code = '<div id = "ID"> Hello World <div>'
    tree = obj.get_tree_without_attr_xml(code)
    assert(tostring(tree) == b'<div> Hello World <div/></div>')

def test_get_repaired_html():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    broken_html = '<div id = "ID"> Hello World <div>'
    assert(obj.get_repaired_html(broken_html) ==
    '<html><body><div id="ID"> Hello World <div/></div></body></html>')

def test_get_tree_without_attr_html():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    code = '<div id = "ID"> Hello World <div>'
    tree = obj.get_tree_without_attr_html(code)
    assert(tostring(tree) == b'<html><body><div> Hello World <div/></div></body></html>')

def test_get_data():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    path = "Examples/1.html"
    broken_code = obj.get_data(path)
    assert(broken_code == 
    '<html>\n    <body>\n        <p>Browsers usually insert quotation marks around the q element.</p>\n        <q>Build a future where people live in harmony with nature.</q>\n    </body>\n</html>\n'
    )

def test_remove_br():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    s = '<br/><br />...<br     /></ br><br>....'
    assert(obj.remove_br(s) == '.......')

def test_remove_tag_attributes():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    code = '<div id = "ID"> Hello World </div>'
    assert(obj.remove_tag_attributes(code) == '<div> Hello World </div>')

def test_get_edit_distance():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    s1 = 'abcdef'
    s2 = 'cefg'
    assert(obj.get_edit_distance(s1, s2) == 4)

def test_retrieve_subtree():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>').getroottree()
    path = [1, 1]
    subtree = obj.retrieve_subtree(tree, path)
    assert(tostring(subtree) == b'<div>child3</div>')

def test_assign():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    xml_data_tree = '<div><div>child1</div><div>child2</div></div>'
    xml_data_subtree = '<div>subtree</div>'
    root_subtree = fromstring(xml_data_subtree)
    tree = fromstring(xml_data_tree).getroottree()
    path = [0]
    assert(tostring(obj.assign(tree, root_subtree, path)) == b'<div><div>subtree</div><div>child2</div></div>')

def test_dfs():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    str_subtree = ['<div>child2</div>']
    mn = [inf]
    obj.curr_path = []
    obj.path_to_subtree = []
    root = fromstring('<div><div>child1</div><div>child2</div></div>')
    obj.dfs(root, mn, str_subtree)
    assert(mn == [0])
    assert(obj.path_to_subtree == [1])

def test_get_subtree_path():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    root_subtree = fromstring('<div>child2</div>')
    root_tree = fromstring('<div><div>child1</div><div>child2</div></div>')
    assert(obj.get_subtree_path(root_subtree, root_tree) == ([1], 0))

def test_xpath_dfs():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    tree = fromstring('<div><div>child1</div><div>child2</div></div>')
    root = fromstring('<div><div>child3</div><div>child1</div></div>')
    xpaths = []
    obj.xpath_gen_path = []
    obj.xpath_dfs(root, tree, xpaths)
    assert(xpaths == [([1], [0])])

def test_generate_XPaths():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    tree = fromstring('<div><div>child1</div><div>child2</div></div>')
    subtree = fromstring('<div><div>child3</div><div>child1</div></div>')
    assert(obj.generate_XPaths(subtree, tree) == [([1], [0])])

def test_get_repaired_subtree():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    tree = fromstring('<div><div>child1</div><div>child2</div></div>').getroottree()
    query_tree = fromstring('<div><div>child3</div><div>child4</div></div>').getroottree()
    xpaths = [([0], [1]), ([1], [0])]
    repaired_subtree = obj.get_repaired_subtree(xpaths, query_tree, tree)
    assert(tostring(repaired_subtree) == b'<div><div>child2</div><div>child1</div></div>')

def test_compress_tree():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    tree = fromstring('<div><div><div><div>child1</div></div></div>\
                                        <div>child2</div></div>')
    orig_tree = fromstring('<div><div><div><div>child1</div></div></div>\
                                        <div>child2</div></div>')
    idx_of_child = 0
    parent = -1
    dic = {}
    compressed_tree = obj.compress_tree(tree, parent, idx_of_child, orig_tree, dic)
    assert(tostring(compressed_tree) == b'<div><div>child1</div><div>child2</div></div>')

def test_get_compressed_tree():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    tree = fromstring('<div><div><div><div>child1</div></div></div><div>child2</div></div>')
    compressed_tree, dic = obj.get_compressed_tree(tree)
    assert(tostring(compressed_tree) == b'<div><div>child1</div><div>child2</div></div>')

def test_get_k_nearest_leaves():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    ## Example 1:
    tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>')
    subtree = tree[1][0]
    assert(tostring(subtree) == b'<div>child2</div>')
    k_nearest_leaves = obj.get_k_nearest_leaves(subtree, 1)
    assert(k_nearest_leaves[0][1] == 2)
    assert(tostring(k_nearest_leaves[0][0])== b'<div>child3</div>')
    ## Example 2:
    k_nearest_leaves = obj.get_k_nearest_leaves(subtree, 2)
    assert(k_nearest_leaves[0][1] == 2)
    assert(k_nearest_leaves[1][1] == 3)
    assert(tostring(k_nearest_leaves[0][0]) == b'<div>child3</div>')
    assert(tostring(k_nearest_leaves[1][0]) == b'<div>child1</div>')

def test_get_all_occurences_helper():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>')
    subtree = fromstring('<div>child2</div>')
    lst_occurences = []
    path = []
    obj.get_all_occurences_helper(tree, subtree, lst_occurences, path)
    assert(tostring(lst_occurences[0][0]) == b'<div>child2</div>')
    assert(lst_occurences[0][1] == [1, 0])
    assert(len(lst_occurences) == 1)
    assert(path == [])

def test_get_all_occurences():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>')
    subtree = fromstring('<div>child2</div>')
    lst_occurences = obj.get_all_occurences(tree, subtree)
    assert(tostring(lst_occurences[0][0]) == b'<div>child2</div>')
    assert(lst_occurences[0][1] == [1, 0])
    assert(len(lst_occurences) == 1)

def test_get_k_nearest_leaves_for_all_subtrees():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>')
    lst_occurences = [tree[0]]
    features = obj.get_k_nearest_leaves_for_all_subtrees(lst_occurences, 2)
    assert(len(features) == 1)
    assert(tostring(features[0][0]) == b'<div>child1</div>')
    assert(tostring(features[0][1][0][0]) == b'<div>child2</div>')
    assert(tostring(features[0][1][1][0]) == b'<div>child3</div>')
    assert(features[0][1][0][1] == 3)
    assert(features[0][1][1][1] == 3)

def test_compute_cost():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>')
    subtree1 = tree[1][0]
    subtree2 = tree[1][1]
    features1 = obj.get_k_nearest_leaves(subtree1, 2)
    features2 = obj.get_k_nearest_leaves(subtree2, 2)
    cost = obj.compute_cost(features1, features2)
    assert((cost[0][0] - -0.5) <= 10**(-9))

def test_get_cost_matrix():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>')
    subtree1 = tree[1][0]
    subtree2 = tree[1][1]
    features1 = obj.get_k_nearest_leaves(subtree1, 2)
    features2 = obj.get_k_nearest_leaves(subtree2, 2)
    data1 = [('some subtree1', features1)]
    data2 = [('some subtree2', features2)]
    cost_matrix = obj.get_cost_matrix(data1, data1)
    assert(abs(cost_matrix[0][0] - -1) <= 10**(-9))

def test_get_min_cost_mapping():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    cost_matrix = array([[0.1, 0.2, 0.7],[0.4, 0.6, 0.1]])
    assert(obj.get_min_cost_mapping(cost_matrix)[0] == 0)
    assert(obj.get_min_cost_mapping(cost_matrix)[1] == 2)

def test_get_new_page_compressed_subtree_path():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    compressed_old_tree = fromstring('  <body>\
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
                                        </body>')
    compressed_new_tree = fromstring('  <body>\
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
                                        </body>')
    subtree = compressed_old_tree[0][0]
    assert(tostring(subtree).strip() == b'<p>Username</p>')
    assert(obj.get_new_page_compressed_subtree_path(subtree, compressed_old_tree, compressed_new_tree) == [2, 1, 0])

def test_get_path_in_compressed_tree():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    old_page = fromstring('<html>\
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
    new_page = fromstring('<html>\
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
    subtree = old_page[0][0][0]
    assert(tostring(subtree).strip() == b'<p>Username</p>')
    assert(obj.get_path_in_compressed_tree(subtree, old_page, new_page) == [2, 1, 0])

def test_get_path_in_uncompressed_tree_helper():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    tree = fromstring('<div><div><div><div>child1</div></div></div><div>child2</div></div>')
    compressed_tree, dic = obj.get_compressed_tree(tree)
    assert(tostring(compressed_tree) == b'<div><div>child1</div><div>child2</div></div>')
    path_compressed = [0]
    str_old_page_subtree = tostring(compressed_tree[0]).strip()
    path_in_new_tree = []
    temp_path = []
    obj.get_path_in_uncompressed_tree_helper(tree, str_old_page_subtree, path_compressed, path_in_new_tree, temp_path)
    assert(path_in_new_tree == [[0, 0, 0]])

def test_get_path_in_uncompressed_tree():
    path = 'Examples/Hello_World.html'
    obj = Page(path, 'html')
    old_page = fromstring('<html>\
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
    new_page = fromstring('<html>\
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
    subtree = old_page[0][0][0]
    assert(tostring(subtree).strip() == b'<p>Username</p>')
    assert(obj.get_path_in_uncompressed_tree(subtree, old_page, new_page) == [0, 2, 1, 0])

def test_equal():
    dic1 = {1:'1', 2: {'1': 5}}
    dic2 = {2: {'1': 5}, 1:'1'}
    assert(equal(dic1, dic2) == True)
    dic3 = {1:'1', 2: {'1': '5'}}
    assert(equal(dic1, dic3) == False)

def test_get_prefix_path():
    tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>')
    extracted_old_subtree = tree[1][1]
    assert(get_prefix_path(extracted_old_subtree) == [1, 1])
    extracted_old_subtree = tree[1][0]
    assert(get_prefix_path(extracted_old_subtree) == [1, 0])

def test_get_paths():
    xpaths = [([1, 0], [0, 0]), ([0], [1]), ([1, 1, 1], [1, 0]), ([], [0])]
    prefix_path = [1, 0]
    assert(get_paths(xpaths, prefix_path) == [[1, 0, 1, 0], [1, 0, 0], [1, 0, 1, 1, 1], [1, 0]])

def test_get_subtrees_to_be_extracted():
    old_page_path = 'Examples/Autorepair_Old_Page.html'
    old_page = Page(old_page_path, 'html')
    xpaths = [([0, 0], [0, 0, 0]), ([0, 1], [0, 0, 1])]
    extracted_old_subtree = old_page.tree.getroot()[0][1][0][0]
    subtrees_to_be_extracted = get_subtrees_to_be_extracted(xpaths, extracted_old_subtree, old_page)
    assert(len(subtrees_to_be_extracted) == 2)
    assert(tostring(subtrees_to_be_extracted[0]).strip() == b'<p>Username</p>')
    assert(tostring(subtrees_to_be_extracted[1]).strip() == b'<p>email</p>')

def test_auto_repair():
    old_page_path = 'Examples/Autorepair_Old_Page.html'
    new_page_path = 'Examples/Autorepair_New_Page.html'
    old_page = Page(old_page_path, 'html')
    new_page = Page(new_page_path, 'html')
    extracted_old_subtree = old_page.tree.getroot()[0][1][0][0]
    assert(tostring(extracted_old_subtree).strip() == 
            b'<div>\n                    <div>\n                        <p>Username</p>\n                        <p>email</p>\n                        <p>Captcha1</p>\n                        <p>Captcha2</p>\n                    </div>\n                </div>\n            '.strip()
        )
    xpaths, repaired_subtree = auto_repair(old_page, new_page, extracted_old_subtree, xpaths = None)
    assert(xpaths == [([0, 0], [0, 0, 0]), ([0, 1], [0, 0, 1])])
    assert(tostring(repaired_subtree).strip() == 
            b'<div>\n                    <div>\n                        <p>Username</p>\n            <p>email</p>\n        <p>Captcha1</p>\n                        <p>Captcha2</p>\n                    </div>\n                </div>\n            '
        .strip())

def test_auto_repair_lst():
    old_page_path = 'Examples/Autorepair_Old_Page.html'
    new_page_path = 'Examples/Autorepair_New_Page.html'
    old_page = Page(old_page_path, 'html')
    new_page = Page(new_page_path, 'html')
    lst_extracted_old_subtrees = [old_page.tree.getroot()[0][1][0][0]]
    lst_xpaths, lst_repaired_subtrees = auto_repair_lst(old_page_path, new_page_path, lst_extracted_old_subtrees)
    assert(lst_xpaths == [[([0, 0], [0, 0, 0]), ([0, 1], [0, 0, 1])]])
    assert(len(lst_repaired_subtrees) == 1)
    assert(tostring(lst_repaired_subtrees[0]).strip() == 
            b'<div>\n                    <div>\n                        <p>Username</p>\n            <p>email</p>\n        <p>Captcha1</p>\n                        <p>Captcha2</p>\n                    </div>\n                </div>\n            '.strip()
    )
