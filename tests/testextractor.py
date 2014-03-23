"""
Tests for structureextractor.py.
"""

from document import metadata, sentence
import unittest
from structureextractor import *
import tokenizer
import json
from lxml import etree

t = tokenizer.Tokenizer()

class CommonTests(object):
    """Functionality common to all extractor test cases.
    """
    def setUp(self, path, structure_file, input_file):
        """Set up some common variables.

        :param str path: The path that contains both the structure_file and
        input_file.
        :param str structure_file: The file with a JSON description of the
        XML structure.
        :param str input_file: The XML file to test.
        """
        self.structure_file = path + structure_file
        self.input_file = path + input_file
        with open(self.structure_file) as f:
            self.json = json.load(f)
        self.xml = etree.parse(self.input_file)
        self.extractor = StructureExtractor(t, self.structure_file)

class PostTests(CommonTests, unittest.TestCase):
    """Run tests based on a single post from the articles directory.
    """
    def setUp(self):
        """Set up variables for the PostTests."""
        self.xpaths = ["./author/text()",
            "./title/text()",
            "./time/text()",
            "./number/text()",
            "./tags/tag/text()",
            "   "]
        super(PostTests, self).setUp(
            "tests/data/articles/", "structure.json", "post1.xml")

    @unittest.skip("Depends on extract_unit_information()")
    def test_extract(self):
        """Tests for extract().
        """
        with open(self.input_file) as f:
            documents = self.extractor.extract(f)

    def test_extract_unit_information(self):
        """Tests for extract_unit_information.
        """
        a = self.extractor.extract_unit_information(self.json,
            self.xml.getroot())
        b = self.extractor.extract_unit_information(self.json, self.xml)
        doc_info = a[0]
        # Make sure that root and file are the same
        self.failUnless(a == b)
        # Should only be one unit present
        self.failUnless(len(a) == 1)
        # It should be named correctly
        self.failUnless(doc_info.name == self.json["structureName"])
        # It should have no sentences
        self.failUnless(doc_info.sentences == [])
        # It should have metadata
        for meta in doc_info.metadata:
            self.failUnless(isinstance(meta, metadata.Metadata))
        # It should only contain one other unit
        self.failUnless(len(doc_info.units) == 1)
        sent_info = doc_info.units[0]
        # The sentence should be named correctly
        self.failUnless(sent_info.name ==
            self.json["units"][0]["structureName"])
        # It should have two sentences
        self.failUnless(len(sent_info.sentences) == 2)
        # And the sentences should have the right text
        for sent in sent_info.sentences:
            self.failUnless(isinstance(sent, sentence.Sentence))
            self.failUnless(sent.text in
                "This is the text of post 1. I love clouds.")

    def test_get_metadata(self):
        """Tests for get_metadata
        """
        meta = {"Time": "2012-02-23",
            "Author": "rachel",
            "Title": "Post 1",
            "Number": "1",
            "Tag": ["Tag 0", "Tag 3"]}
        results = get_metadata(self.json, self.xml.getroot())
        for result in results:
            self.failUnless(result.property_name in meta.keys())
            self.failUnless(result.value in meta[result.property_name])

    @unittest.skip("Need example code")
    def test_get_xpath_attribute(self):
        """Test get_xpath_attribute.
        """
        pass

    def test_get_xpath_text(self):
        """Tests for get_xpath_text
        """
        texts = [["rachel"],
            ["Post 1"],
            ["2012-02-23"],
            ["1"],
            ["Tag 0", "Tag 3"],
            ["\n2012-02-23\nPost 1\nrachel\n\n Tag 0\n Tag " +\
                "3\n\n1\n\n\tThis is the text of post 1. I love clouds.\n\n"]]
        key = dict(zip(self.xpaths, texts))
        for xpath, text in key.items():
            result = get_xpath_text(xpath, self.xml.getroot())
            self.failUnless(result == text)

class PlayTests(CommonTests, unittest.TestCase):
    """Tests based on an abbreviated version of a play.
    """
    def setUp(self):
        """Set up local variables.
        """
        super(PlayTests, self).setUp(
            "tests/data/shakespeare/", "structure.json", "brief_example.xml")

    def test_get_sentences(self):
        """Test get_sentences
        """
        #Test more cases?
        self.failUnless(self.extractor.get_sentences(self.json["units"][0],
            self.xml.getroot(), False)[0].text == etree.tostring(
            self.xml.getroot()[5], method="text").strip() + "\n")

def main():
    unittest.main()

if __name__ == "__main__":
    main()
