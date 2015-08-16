import re

from xml.dom import minidom
from __armando__ import Armando

###
Armando.initialize()
###

from config import Config
from logger import Logger

class Rules(object):
    __config = Config.get_config()
    __logger = Logger.get_logger(__name__)

    """
    Contains the logic to parse and map the rules in rules.xml
    @author: Fabio "BlackLight" Manganiello <blacklight86@gmail.com>
    """

    def __init__(self, config_file):
        self.__config_file = config_file
        xml_doc = minidom.parse(self.__config_file)

        try:
            self.__config = xml_doc.getElementsByTagName('app')[0]
        except IndexError as e:
            raise AttributeError(u'[%s] has no "app" root node' % self.__config_file)

        self.__parse_patterns()
        self.__parse_actions()
        self.__parse_rules()

    def __parse_patterns(self):
        try:
            xml_patterns = self.__config.getElementsByTagName('patterns')[0]
        except IndexError as e:
            self.__logger.warning({
                'msg_type' : 'Configuration warning',
                'content'  : '"%s" has no patterns node' % self.__config_file
            })

            return

        self.__xml_patterns = xml_patterns.getElementsByTagName('pattern')
        if len(self.__xml_patterns) == 0:
            self.__logger.warning({
                'msg_type' : 'Configuration warning',
                'content'  : '"%s" has no patterns' % self.__config_file
            })

            return

        self.__parse_xml_patterns_node()

    def __parse_xml_patterns_node(self):
        self.__patterns = []

        for xml_pattern in self.__xml_patterns:
            if not 'id' in xml_pattern.attributes:
                raise AttributeError('Pattern #%d has no ID attribute' % len(__self.patterns)+1)

            pattern = {
                'id': xml_pattern.attributes['id'].value,
            }

            try:
                match = xml_pattern.getElementsByTagName('match')[0]
            except IndexError as e:
                raise AttributeError('The pattern [%s] has no match attributes' % pattern.id)

            match_content = match.firstChild.wholeText
            pattern['match'] = self.__build_match(match_content)

            self.__patterns.append(pattern)
        self.__patterns_map = dict(map(lambda _: (_['id'], _['match']), self.__patterns))

    @classmethod
    def __build_match(cls, match_content):
        " Extract keywords and replace them with (.+?) in the regex "

        tmp_content = match_content
        regex = '(.*){([A-Za-z0-9-_\s]+)\[regex-index=(\d+)\]}(.*)'
        attributes = []
        m = re.search(regex, tmp_content)

        while m:
            match_content = match_content.replace(tmp_content, m.group(1) + '(.*)' + m.group(4))
            tmp_content = m.group(1)
            attributes.insert(0, {
                'name': m.group(2).strip(),
                'regex_index': int(m.group(3)),
            })

            m = re.search(regex, tmp_content)

        return {
            'value': match_content.strip(),
            'attributes': attributes,
        }

    def __parse_actions(self):
        actions = []
        self.__actions = actions

    def __parse_rules(self):
        rules = []
        self.__rules = rules

    def get_patterns(self):
        return self.__patterns

    def get_actions(self):
        return self.__actions

    def get_rules(self):
        return self.__rules

    def pattern_match(self, string):
        """
        Check whether [string] matches any of the configured patterns.
        In case it does, it returns *the first* pattern it matches.
        The output is a tuple (pattern_id, attributes).
        e.g., in this case:
            pattern -- <pattern id="play-music">
                <match><![CDATA[
                    play(.*)music(.*)artist {artist}
                ]]></match>
            </pattern>

            string -- Play some music from the artist Led Zeppelin

        After executing:
            pattern_id, attributes = your_rules_object.pattern_match(string)

        You would have:
            pattern_id -- play-music
            attributes -- {
                'artist': 'Led Zeppelin'
            }

        (None, {}) is returned in case nothing is matched
        """

        matched_pattern_id = None
        attributes = {}

        for pattern in self.get_patterns():
            match_value = pattern['match']['value']
            match_attributes = pattern['match']['attributes']
            m = re.search(match_value, string, re.IGNORECASE)

            if m:
                matched_pattern_id = pattern['id']

                for attribute in match_attributes:
                    attribute_match = m.group(attribute['regex_index'])
                    if attribute_match:
                        attributes[attribute['name']] = attribute_match.strip()   # Every second grouping

                break

        return (matched_pattern_id, attributes)

