# Vervanging van Runestones unittest.gui om de tests onder node te kunnen draaien (tools/check_toetsen.py).
from unittest import TestCase
import document

class TestCaseGui(TestCase):
    def __init__(self):
        TestCase.__init__(self)
    def main(self):
        for func in self.tlist:
            try:
                self.setUp()
                func()
                self.tearDown()
            except Exception as e:
                self.appendResult("Error", None, None, str(e))
                self.numFailed += 1
        print("SUMMARY passed=%d failed=%d" % (self.numPassed, self.numFailed))
    def getEditorText(self):
        return document.getCurrentEditorValue()
    def getOutput(self):
        return ""
    def appendResult(self, res, actual, expected, param):
        if res == "Error":
            print("RESULT ERROR", param)
        elif res:
            self.numPassed += 1
            print("RESULT PASS", param)
        else:
            self.numFailed += 1
            print("RESULT FAIL", repr(actual), repr(expected), param)
