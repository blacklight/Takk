import os
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
        self.__patterns_map = dict(map(lambda _: (_['id'], _), self.__patterns))

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
        try:
            xml_actions = self.__config.getElementsByTagName('actions')[0]
        except IndexError as e:
            self.__logger.warning({
                'msg_type' : 'Configuration warning',
                'content'  : '"%s" has no actions node' % self.__config_file
            })

            return

        self.__xml_actions = xml_actions.getElementsByTagName('action')
        if len(self.__xml_actions) == 0:
            self.__logger.warning({
                'msg_type' : 'Configuration warning',
                'content'  : '"%s" has no actions' % self.__config_file
            })

            return

        self.__parse_xml_actions_node()

    def __parse_xml_actions_node(self):
        self.__actions = []
        for xml_action in self.__xml_actions:
            if not 'id' in xml_action.attributes:
                raise AttributeError('Action #%d has no ID attribute' % len(__self.actions)+1)

            if not 'type' in xml_action.attributes:
                raise AttributeError('Action #%d has no type attribute - either "python" or "shell" is required' % len(__self.actions)+1)

            action = {
                'id': xml_action.attributes['id'].value,
                'type': xml_action.attributes['type'].value,
                'code': xml_action.firstChild.wholeText,
            }

            self.__actions.append(action)
        self.__actions_map = dict(map(lambda _: (_['id'], _), self.__actions))

    def __parse_rules(self):
        try:
            xml_rules = self.__config.getElementsByTagName('rules')[0]
        except IndexError as e:
            self.__logger.warning({
                'msg_type' : 'Configuration warning',
                'content'  : '"%s" has no rules node' % self.__config_file
            })

            return

        self.__xml_rules = xml_rules.getElementsByTagName('rule')
        if len(self.__xml_rules) == 0:
            self.__logger.warning({
                'msg_type' : 'Configuration warning',
                'content'  : '"%s" has no rules' % self.__config_file
            })

            return

        self.__parse_xml_rules_node()

    def __parse_xml_rules_node(self):
        self.__rules = []

        for xml_rule in self.__xml_rules:
            if not 'id' in xml_rule.attributes:
                raise AttributeError('Rule #%d has no ID attribute' % len(__self.rules)+1)

            on_nodes = xml_rule.getElementsByTagName('on')
            if len(on_nodes) != 1:
                raise AttributeError('Rule #%d must have exactly one ON node' % len(__self.rules)+1)

            then_nodes = xml_rule.getElementsByTagName('then')
            if len(then_nodes) != 1:
                raise AttributeError('Rule #%d must have exactly one THEN node' % len(__self.rules)+1)

            rule = {
                'id': xml_rule.attributes['id'].value,
                'on': self.__parse_on_node(xml_rule.getElementsByTagName('on')[0], []),
                'then': self.__parse_then_node(xml_rule.getElementsByTagName('then')[0], []),
            }

            self.__rules.append(rule)
        self.__rules_map = dict(map(lambda _: (_['id'], _), self.__rules))

    @classmethod
    def __parse_on_node(cls, node, out_node, in_and = False, in_or = False):
        child = node.firstChild

        while child != None:
            if not hasattr(child, 'tagName'):
                child = child.nextSibling
                continue

            if child.tagName == 'pattern':
                if not 'id' in child.attributes:
                    raise AttributeError('A rule pattern has no ID attribute')

                if len(out_node) == 0:
                    out_node.append([child.attributes['id'].value])
                else:
                    if in_and:
                        out_node[len(out_node)-1].append(child.attributes['id'].value)
                    elif in_or:
                        out_node.append([child.attributes['id'].value])
                    else:
                        raise AttributeError('A rule has multiple patterns specified outside of AND/OR tags')
            elif child.tagName == 'and':
                if len(out_node) == 0:
                    out_node.append([])
                return cls.__parse_on_node(child, out_node, in_and = True, in_or = False)
            elif child.tagName == 'or':
                return cls.__parse_on_node(child, out_node, in_and = False, in_or = True)

            child = child.nextSibling

        return out_node

    @classmethod
    def __parse_then_node(cls, node, out_node):
        pass

    def get_patterns(self):
        return self.__patterns

    def get_actions(self):
        return self.__actions

    def get_rules(self):
        return self.__rules

    def pattern_match(self, string):
        """
        Check whether [string] matches any of the configured patterns.
        The output is an array of matched patterns, in the order they
        were matched. Each of those has the structure:
        {
            'id': pattern_id,
            'arguments': { dictionary of arguments parsed, can be empty },
        }

        e.g., in this case:
            pattern -- <pattern id="play-music">
                <match><![CDATA[
                    play(.*)music(.*)artist {artist}
                ]]></match>
            </pattern>

            string -- play some music from the artist Led Zeppelin

        After executing:
            patterns = your_rules_object.pattern_match(string)

        You would have:
            patterns = [
                {
                    'id': 'play-music',
                    'arguments': {
                        'artist': 'Led Zeppelin'
                    }
                }

        An empty array is returned in case nothing is matched
        """

        matches = []

        for pattern in self.get_patterns():
            match_value = pattern['match']['value']
            match_attributes = pattern['match']['attributes']
            m = re.search(match_value, string, re.IGNORECASE)

            if m:
                match = {
                    'id': pattern['id'],
                    'attributes': {},
                }

                for attribute in match_attributes:
                    attribute_match = m.group(attribute['regex_index'])
                    if attribute_match:
                        match['attributes'][attribute['name']] = attribute_match.strip()

                matches.append(match)

        return matches

    def run_action(self, action_id, arguments={}):
        """
        Run an action by id.
        action_id -- The action_id
        arguments -- A dictionary containing the arguments to be passed to the action.
            The arguments are defined inside of the action code delimited by $$..$$.
            e.g. if you want to pass {'filename': 'your_file'} to your action, you need
            then to use it through $$filename$$ in your action code.
        """

        action = self.__actions_map[action_id]
        code = action['code']

        for key, value in arguments.items():
            code = action['code'].replace('$$%s$$' % key, value)

        if action['type'] == 'shell':
            os.system(code)
        else:
            eval(code.strip())

    def get_rules_by_patterns(self, pattern_ids):
        """
        Given an array of matched pattern IDs, return an array of matched rules
        """

        rules = []

        for rule in self.__rules:
            rule_satisfied = False  # OR logic for pattern sets

            for pattern_set in rule['on']:
                pattern_map = dict(map(lambda _: (_, True), pattern_set))
                input_pattern_map = dict(map(lambda _: (_, True), pattern_ids))
                pattern_set_satisfied = True  # AND logic for patterns

                for pattern_id in pattern_ids:
                    if not pattern_id in pattern_map:
                        pattern_set_satisfied = False
                        break

                for pattern_id in pattern_set:
                    if not pattern_id in input_pattern_map:
                        pattern_set_satisfied = False
                        break

                if pattern_set_satisfied:
                    rule_satisfied = True
                    break

            if rule_satisfied:
                rules.append(rule['id'])

        return rules

