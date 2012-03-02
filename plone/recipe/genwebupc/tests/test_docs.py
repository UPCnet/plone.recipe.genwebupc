# -*- coding: utf-8 -*-
"""
Doctest runner for 'plone.recipe.genwebupc'.
"""
__docformat__ = 'restructuredtext'

import unittest
import zc.buildout.tests
import zc.buildout.testing
from zc.buildout.testing import install
from zc.buildout.testing import buildoutTearDown

import pkg_resources
import shutil
from zope.testing import doctest, renormalizing


optionflags = (doctest.ELLIPSIS |
                doctest.NORMALIZE_WHITESPACE |
                doctest.REPORT_ONLY_FIRST_FAILURE)


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)

    # Install the recipe in develop mode
    zc.buildout.testing.install_develop('plone.recipe.genwebupc', test)

    # Install any other recipes that should be available in the tests
    #zc.buildout.testing.install('collective.recipe.foobar', test)
    install('zc.recipe.egg', test)
    install('mailinglogger', test)
    install('zope.mkzeoinstance', test)
    install('ZopeUndo', test)
    install('plone.recipe.zeoserver', test)
    install('plone.recipe.zope2instance', test)
    dependencies = pkg_resources.working_set.require('Zope2')
    for dep in dependencies:
        try:
            install(dep.project_name, test)
        except OSError:
            # Some distributions are installed multiple times, and the
            # underlying API doesn't check for it
            pass


def tearDown(test):
    buildoutTearDown(test)
    sample_buildout = test.globs['sample_buildout']
    shutil.rmtree(sample_buildout, ignore_errors=True)


def test_suite():
    suite = unittest.TestSuite((
            doctest.DocFileSuite(
                'testconfs.txt',
                setUp=setUp,
                tearDown=zc.buildout.testing.buildoutTearDown,
                optionflags=optionflags,
                checker=renormalizing.RENormalizing([
                        # If want to clean up the doctest output you
                        # can register additional regexp normalizers
                        # here. The format is a two-tuple with the RE
                        # as the first item and the replacement as the
                        # second item, e.g.
                        # (re.compile('my-[rR]eg[eE]ps'), 'my-regexps')
                        zc.buildout.testing.normalize_path,
                        ]),
                ),
            ))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
