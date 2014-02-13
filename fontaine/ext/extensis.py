from __future__ import print_function

from lxml import etree

import re
import requests

from fontaine.ext.base import BaseExt


EXTENSIS_LANG_XML = 'https://raw.github.com/davelab6/extensis-languages/master/languages.xml'


class Extension(BaseExt):

    extension_name = 'extensis'

    @staticmethod
    def __getcharmaps__():
        glyphs = {}
        for ext in Extension.get_codepoints():
            parent_name = ext.getparent().attrib.get('parent')

            common_name = u'Extensis %s' % ext.getparent().attrib['name']
            unicodes = []
            if parent_name:
                common_name += u' + ' + parent_name
                unicodes = glyphs.get(parent_name, [])
            unicodes += Extension.get_unicodes(ext)
            glyphs[ext.getparent().attrib['name']] = unicodes

            yield type('Charmap', (object,),
                       dict(glyphs=unicodes, common_name=common_name,
                            native_name=''))

    @staticmethod
    def get_codepoints():
        """ Return all XML <scanning-codepoints> in received XML """
        response = requests.get(EXTENSIS_LANG_XML)
        if response.status_code != 200:
            return []

        content = re.sub('<!--.[^>]*-->', '', response.content)

        doc = etree.fromstring(content.lstrip('`'))
        return doc.findall('.//scanning-codepoints')

    @staticmethod
    def get_unicodes(codepoint):
        """ Return list of unicodes for <scanning-codepoints> """
        result = re.sub('\s', '', codepoint.text)
        return Extension.convert_to_list_of_unicodes(result)

    def __init__(self, unichar):
        self.unicodechar = int(unichar, 16)

    def findlanguages(self):
        """ Return string with languages containing passed unicodechar """
        languages = []
        for codepoint in Extension.get_codepoints():

            if self.unicodechar in Extension.get_unicodes(codepoint):
                try:
                    languages.append(codepoint.getparent().attrib['name'])
                except (KeyError, ValueError):
                    pass

        return ', '.join(languages)


if __name__ == '__main__':
    assert Extension('0x0531').findlanguages() == 'Armenian'
