# -*- coding: utf-8 -*-
import logging 
import logging.handlers as handlers
import os, os.path
import unittest
import sys

from ws4py import configure_logger

def clean_logger():
    logger = logging.getLogger('ws4py')
    for handler in list(logger.handlers):
        try:
            handler.close()
        except KeyError:
            pass
        logger.removeHandler(handler)
            
class WSTestLogger(unittest.TestCase):
    def tearDown(self):
        clean_logger()
        
    def test_named_logger(self):
        logger = configure_logger(stdout=False, filepath='./my.log')

        logger = logging.getLogger('ws4py')
        self.assertEqual(logger.getEffectiveLevel(), logging.INFO)
        
    def test_level(self):
        logger = configure_logger(stdout=True, filepath='./my.log',
                                  level=logging.DEBUG)

        self.assertEqual(logger.getEffectiveLevel(), logging.DEBUG)
        for handler in logger.handlers:
            self.assertEqual(handler.level, logging.DEBUG)
        
    def test_file_logger(self):
        filepath = os.path.abspath('./my.log')
        logger = configure_logger(stdout=False, filepath=filepath)
        for handler in logger.handlers:
            if isinstance(handler, handlers.RotatingFileHandler):
                self.assertEqual(handler.baseFilename, filepath)
                self.assertEqual(handler.stream.name, filepath)
                break
        else:
            self.fail("File logger not configured")

    def test_stdout_logger(self):
        logger = configure_logger()
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not\
              isinstance(handler, handlers.RotatingFileHandler):
                self.assertTrue(handler.stream is sys.stdout)
                break
        else:
            self.fail("Stream logger not configured")

if __name__ == '__main__':
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for testcase in [WSTestLogger]:
        tests = loader.loadTestsFromTestCase(testcase)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
