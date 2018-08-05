#
# Introduction

Spiders can become broken due to changes on the target site, which lead to different page layouts (therefore, broken XPath and CSS extractors). Often however, the information content of a page remains, roughly, the same, just in a different form or layout.

This tool is used to repair broken spiders and output extraction rules which can then be used to correctly extract data even when the layout has changed.

#
# How It Works?

All you need to do is import one function, auto\_repair\_lst.

To do this, you can type,

\&gt;\&gt;\&gt; from scrapy\_spider\_auto\_repair import auto\_repair\_lst

 This function, auto\_repair\_lst takes 4 parameters:

1. old\_page\_path(type = string)
2. new\_page\_path(type = string)
3. lst\_extracted\_old\_subtree(type = list of lxml.etree.\_Element objects)
4. rules(type = list)(OPTIONAL)

old\_page\_path is the path to a file containing the old HTML page on which the spider worked and correctly extracted the required data.

new\_page\_path is the path to a file containing the new HTML page on which the spider fails to extract the correct data and it is this file from which you would like the repaired spider to extract the data.

lst\_extracted\_old\_subtree is a list of objects of type lxml.etree.\_Element.  Each object in this list is a subtree of the old\_page HTML tree which was extracted from the old page when the spider was not broken.

If rules(the fourth parameter) is given, the function will use these rules to correctly extract the relevant information from the new page.



This function takes the above arguments and returns two things:

1. Rules for data extraction
2. List of repaired subtrees. Each subtree in this list is an object of type lxml.etree.\_Element.

Let&#39;s take a simple example.

Suppose the old page contains the following HTML code:

```html
<html>
    <body>
        <div>
            <p>Username</p>
            <p>Password</p>
            <div>Submit</div>
        </div>
        <div>
           <div>
                <div>
                    <div>
                        <p>Username</p>
                        <p>email</p>
                        <p>Captcha1</p>
                        <p>Captcha2</p>
                    </div>
                </div>
            </div>
        </div> 
        </p>This should not be extracted</p>
    </body>
</html>
```









And the new page contains the following HTML code:

```html
<html>
    <body>
        <div>
            <p>Username</p>
            <p>email</p>
        </div> 
        </p>This should not be extracted</p>
        <div>
            <p>Hello World</p>
            <div>
                <p>Username</p>
                <p>Password</p>
            </div>
            <div>Submit</div>
        </div>
    </body>
</html>
```

Now you can run the following code to correctly extract data.

```python
>>> old_page_path = 'Examples/Autorepair_Old_Page.html'
>>> new_page_path = 'Examples/Autorepair_New_Page.html'
>>> old_page = Page(old_page_path, 'html')
>>> new_page = Page(new_page_path, 'html')
>>> lst_extracted_old_subtrees = [old_page.tree.getroot()[0][1][0][0]]
>>> lst_rules, lst_repaired_subtrees = auto_repair_lst(old_page_path,new_page_path, lst_extracted_old_subtrees)
>>> lst_rules
[[([0, 0], [0, 0, 0]), ([0, 1], [0, 0, 1])]]
>>> len(lst_repaired_subtrees)
1
>>> tostring(lst_repaired_subtrees[0])
b'<div>\n                    <div>\n                        <p>Username</p>\n            <p>email</p>\n        <p>Captcha1</p>\n                        <p>Captcha2</p>\n                    </div>\n                </div>\n            '
>>> 
```

From the above example, you can see that since captcha1 and captcha2 could not be found in the new\_page, it keeps it untouched.

Now, whenever you encounter a webpage having layout similar to the new page layout, you can directly use the rules returned when trying to repair the spider to correctly extract data from new\_page.

To do this, simply pass the variable rules to the auto\_repair\_lst function in the following manner:

Extending the above example, suppose a webpage having layout similar to the new\_page layout is the following:

```html
<html>
    <body>
        <div>
            <p>Google</p>
            <p>Microsoft</p>
        </div> 
        </p>This should not be extracted</p>
        <div>
            <p>Hello World</p>
            <div>
                <p>foop>
                <p>bar</p>
            </div>
            <div>blah...</div>
        </div>
    </body>
</html>
```

You can write the following extra code:

```python
>>> new_page_similar_path = 'C:/Users/Viral Mehta/Desktop/Scrapy-Spider-Autorepair/Examples/Autorepair_New_page_similar.html'
>>> rules, lst_repaired_subtrees = auto_repair_lst(old_page_path, new_page_similar_path, lst_extracted_old_subtrees, rules)
>>> tostring(lst_repaired_subtrees[0])
b'<div>\n                    <div>\n                        <p>Google</p>\n            <p>Microsoft</p>\n        <p>Captcha1</p>\n                        <p>Captcha2</p>\n                    </div>\n                </div>\n            '
>>> 
```

#
# Contributions and Further Readings:

If you are interested in finding out more about the algorithm behind this, feel free to visit my blog:

[https://blogs.python-gsoc.org/viral-mehta/](https://blogs.python-gsoc.org/viral-mehta/)

I am openly looking for contributors. Pull requests are welcome :)