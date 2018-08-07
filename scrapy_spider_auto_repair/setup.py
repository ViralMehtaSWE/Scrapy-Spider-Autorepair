# !/usr/bin/env python

from distutils.core import setup
import setuptools
setup(
    name='scrapy_spider_auto_repair',
    packages=setuptools.find_packages(exclude=('tests',
                                               'tests.*',
                                               'src.data_extractor_scrapy.py',
                                               'Data Extractor.py',
                                               'Link to Dataset.txt',
                                               'top500domains.csv',
                                               'README.pdf')),
    version='0.1.2',
    description='Spiders can become broken due to changes\
                 on the target site, which lead to different\
                 page layouts (therefore, broken XPath and\
                 CSS extractors). Often however, the information\
                 content of a page remains roughly similar, just\
                 in a different form or layout. This tool that can,\
                 in some fortunate cases, automatically infer\
                 extraction rules to keep a spider up-to-date\
                 with site changes.',
    author='Viral Paresh Mehta',
    license='BSD',
    author_email='virmht@gmail.com',
    url='https://github.com/virmht/Scrapy-Spider-Autorepair',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
    ],
    install_requires=[
        'lxml',
        'numpy',
        'sklearn',
        'scipy'
    ],
)
