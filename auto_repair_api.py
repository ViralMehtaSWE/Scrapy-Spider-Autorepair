from auto_repair_code import Page
from lxml.etree import HTMLParser
from lxml.etree import XMLParser
from lxml.etree import HTML
from lxml.etree import XML
from lxml.etree import tostring
from lxml.etree import parse
from lxml.etree import fromstring
from lxml.etree import ElementTree
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
def get_prefix_path(extracted_old_subtree):
    """
        This function returns the path of extracted_old_subtree
        (passed as an argument) in the tree containing this subtree.
        See example below.
        Parameters:
            1. extracted_old_subtree(type = lxml.etree._Element)
        Example:
            >>> tree = fromstring('<div><div>child1</div><div><div>child2</div><div>child3</div></div></div>')
            >>> extracted_old_subtree = tree[1][1]
            >>> tostring(extracted_old_subtree)
            b'<div>child3</div>'
            >>> get_prefix_path(extracted_old_subtree)
            [1, 1]
            >>> extracted_old_subtree = tree[1][0]
            >>> tostring(extracted_old_subtree)
            b'<div>child2</div>'
            >>> get_prefix_path(extracted_old_subtree)
            [1, 0]
            >>> 
    """
    ptr = extracted_old_subtree
    prefix_path = []
    while(ptr.getparent() is not None):
        parent = ptr.getparent()
        n = len(parent)
        for i in range(n):
            if parent[i] == ptr:
                prefix_path.append(i)
                break
        ptr = parent
    prefix_path.reverse()
    return prefix_path

def get_paths(xpaths, prefix_path):
    """
        This function appends prefix_path(passed as an argument)
        to each path where path is the first element of each tuple
        in the list called xpaths(passed as an argument). The path
        (described above) is a relative path, i.e., it is a path in
        a subtree and prefix_path(passed as an argument) is the path
        of the subtree in its tree, so, by appending path to prefix_path,
        we get the absolute path. See example below.
        Parameters:
            1. xpaths(type = list of tuples)
            2. prefix_path(type = list)
        Example:
            >>> xpaths = [([1, 0], [0, 0]), ([0], [1]), ([1, 1, 1], [1, 0]), ([], [0])]
            >>> prefix_path = [1, 0]
            >>> get_paths(xpaths, prefix_path)
            [[1, 0, 1, 0], [1, 0, 0], [1, 0, 1, 1, 1], [1, 0]]
            >>> 
    """
    paths = []
    for xpath in xpaths:
        path, _ = xpath
        path = prefix_path + path
        paths.append(path)
    return paths

def get_subtrees_to_be_extracted(xpaths, extracted_old_subtree, old_page):
    """
        This function returns a list containing subtrees
        which are retrieved from old_page,
        present at paths in old_page.tree
        specified by the absolute path derived from
        xpaths, extracted_old_subtree and old_page
        (passed as arguments). See example below.
        Parameters:
            1. xpaths(type = list of tuples)
            2. extracted_old_subtree(type = lxml.etree._Element)
            3. old_page(type = Page Object)
        Example:
            >>> xpaths = [([0, 0], [0, 0, 0]), ([0, 1], [0, 0, 1])]
            >>> extracted_old_subtree = old_page.tree.getroot()[0][1][0][0]
            >>> subtrees_to_be_extracted = get_subtrees_to_be_extracted(xpaths, extracted_old_subtree, old_page)
            >>> len(subtrees_to_be_extracted)
            2
            >>> tostring(subtrees_to_be_extracted[0])
            b'<p>Username</p>\n                        '
            >>> tostring(subtrees_to_be_extracted[1])
            b'<p>email</p>\n                        '
            >>> 
    """
    prefix_path = get_prefix_path(extracted_old_subtree)
    paths = get_paths(xpaths, prefix_path)
    subtrees_to_be_extracted = []
    for path in paths:
        subtrees_to_be_extracted.append(old_page.retrieve_subtree(old_page.tree,
                                                                  path, cpy = False))
    return subtrees_to_be_extracted

def auto_repair(old_page, new_page, extracted_old_subtree, xpaths = None):
    """
        This function is used to repair the incorrect
        data extracted by the broken spider from the new
        page. extracted_old_subtree(passed as an argument)
        is the correct data extracted by the unbroken
        spider from the old page. This data must be a
        subtree in the HTML code of the old page. This
        function repairs the spider to return the rules,
        called xpaths, and it also returns the correct
        data, called repaired_subtree. If xpaths or the
        rules are passed to this function, then, it uses
        the rules to find the correct data to be
        extracted from old_page, otherwise, it first
        generates the rules and then, corrects the spider
        and outputs rules(called xpaths, so that they can be
        used directly on pages having similar layout) as well
        as the repaired_subtree. See example below.
        Parameters:
            1. old_page(type = Page Object)
            2. new_page(type = Page Object)
            3. extracted_old_subtree(type = lxml.etree._Element)
        Example:
            >>> old_page_path = 'Examples/Autorepair_Old_Page.html'
            >>> new_page_path = 'Examples/Autorepair_New_Page.html'
            >>> old_page = Page(old_page_path, 'html')
            >>> new_page = Page(new_page_path, 'html')
            >>> extracted_old_subtree = old_page.tree.getroot()[0][1][0][0]
            >>> tostring(extracted_old_subtree)
            b'<div>\n                    <div>\n                        <p>Username</p>\n                        <p>email</p>\n                        <p>Captcha1</p>\n                        <p>Captcha2</p>\n                    </div>\n                </div>\n            '
            >>> xpaths, repaired_subtree = auto_repair(old_page, new_page, extracted_old_subtree, xpaths = None)
            >>> xpaths
            [([0, 0], [0, 0, 0]), ([0, 1], [0, 0, 1])]
            >>> tostring(repaired_subtree)
            b'<div>\n                    <div>\n                        <p>Username</p>\n            <p>email</p>\n        <p>Captcha1</p>\n                        <p>Captcha2</p>\n                    </div>\n                </div>\n            '
            >>> 
    """
    if xpaths is not None:
        repaired_subtree = new_page.get_repaired_subtree(xpaths,
                                                         ElementTree(extracted_old_subtree),
                                                         new_page.tree)
        return xpaths, repaired_subtree
    xpaths = new_page.generate_XPaths(extracted_old_subtree,
                                       new_page.tree_without_attr)
    subtrees_to_be_extracted = get_subtrees_to_be_extracted(xpaths,
                                                            extracted_old_subtree,
                                                            old_page)
    root_old_page = old_page.tree.getroot()
    root_new_page = new_page.tree.getroot()
    final_xpaths = []
    for subtree, xpath in zip(subtrees_to_be_extracted, xpaths):
        final_xpaths.append((xpath[0], old_page.get_path_in_uncompressed_tree(subtree, 
                                                                   root_old_page,
                                                                   root_new_page)))
    return auto_repair(old_page, new_page, extracted_old_subtree, xpaths = final_xpaths)

def auto_repair_lst(old_page_path, new_page_path, lst_extracted_old_subtrees, xpaths = None):
    """
        This function is used to repair the incorrect
        data extracted by the broken spider from the new
        page. lst_extracted_old_subtree(passed as an
        argument) is the correct data extracted by the
        unbroken spider from the old page. This data must
        be a list of subtrees in the HTML code of the old
        page. This function repairs the spider to return
        the list of rules, called xpaths, and it also returns
        the correct data, called lst_repaired_subtrees.
        If xpaths or the rules are passed to this function,
        then, it uses the rules to find the correct data
        to be extracted from old_page, otherwise, it first
        generates the rules and then, corrects the spider
        and outputs rules(called xpaths, so that they can be
        used directly on pages having similar layout) as well
        as the lst_repaired_subtrees. See example below.
        Parameters:
            1. old_page_path(type = string)
            2. new_page_path(type = string)
            3. lst_extracted_old_subtree(type = list of lxml.etree._Element objects)
            4. xpaths(type = list)
        Example:
            >>> old_page_path = 'Examples/Autorepair_Old_Page.html'
            >>> new_page_path = 'Examples/Autorepair_New_Page.html'
            >>> old_page = Page(old_page_path, 'html')
            >>> new_page = Page(new_page_path, 'html')
            >>> lst_extracted_old_subtrees = [old_page.tree.getroot()[0][1][0][0]]
            >>> lst_xpaths, lst_repaired_subtrees = auto_repair_lst(old_page_path, new_page_path, lst_extracted_old_subtrees)
            >>> lst_xpaths
            [[([0, 0], [0, 0, 0]), ([0, 1], [0, 0, 1])]]
            >>> len(lst_repaired_subtrees)
            1
            >>> tostring(lst_repaired_subtrees[0])
            b'<div>\n                    <div>\n                        <p>Username</p>\n            <p>email</p>\n        <p>Captcha1</p>\n                        <p>Captcha2</p>\n                    </div>\n                </div>\n            '
            >>> 
    """
    new_page = Page(new_page_path, 'html')
    old_page = Page(old_page_path, 'html')
    lst_xpaths = []
    lst_repaired_subtrees = []
    if xpaths is None:
        xpaths = [None]*len(lst_extracted_old_subtrees)
    idx = 0
    for extracted_old_subtree in lst_extracted_old_subtrees:
        final_xpaths, repaired_subtree = auto_repair(old_page, new_page, extracted_old_subtree, xpaths = xpaths[idx])
        lst_xpaths.append(final_xpaths)
        lst_repaired_subtrees.append(repaired_subtree)
        idx += 1
    return lst_xpaths, lst_repaired_subtrees


def show_demo():
    old_page_path = 'C:/Users/Viral Mehta/Desktop/Scrapy-Spider-Autorepair/Examples/Autorepair_Old_Page.html'
    new_page_path = 'C:/Users/Viral Mehta/Desktop/Scrapy-Spider-Autorepair/Examples/Autorepair_New_Page.html'
    new_page = Page(new_page_path, 'html')
    old_page = Page(old_page_path, 'html')
    extracted_old_subtree = old_page.tree.getroot()[0][1][0][0]
    old_page.print_tree(extracted_old_subtree)
    print(auto_repair(old_page, new_page, extracted_old_subtree, xpaths = None))
    return old_page, auto_repair(old_page_path, new_page_path, extracted_old_subtree, xpaths = None)

#obj, (xpaths, subtree) = show_demo()
#path = 'Examples/Hello_World.html'
#obj = Page(path, 'html')
old_page_path = 'Examples/Autorepair_Old_Page.html'
new_page_path = 'Examples/Autorepair_New_Page.html'
old_page = Page(old_page_path, 'html')
new_page = Page(new_page_path, 'html')
extracted_old_subtree = old_page.tree.getroot()[0][1][0][0]
xpaths, repaired_subtree = auto_repair(old_page, new_page, extracted_old_subtree, xpaths = None)

