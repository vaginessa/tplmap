import unittest
import requests
import os
import sys
import random

sys.path.insert(10, os.path.join(sys.path[0], '..'))
from plugins.engines.jinja2 import Jinja2
from core.channel import Channel
from utils import rand
from utils import strings
from basetest import BaseTest

class Jinja2Test(unittest.TestCase, BaseTest):

    expected_data = {
        'language': 'python',
        'engine': 'jinja2',
        'eval' : 'python' ,
        'exec' : True,
        'read' : True,
        'write' : True,
        'trailer_tag': '{{%(trailer)s}}',
        'header_tag': '{{%(header)s}}',
        'render_tag': '{{%(payload)s}}',
    }

    url = 'http://127.0.0.1:15001/reflect/jinja2?tpl=%s&inj=*'
    plugin = Jinja2

    reflection_tests = [
        (1, 1, '%s', {}),
        (1, 1, 'AAA%sAAA', {}),

        # Reflecting tag ${} context
        (1, 1, '{{%s}}', { 'prefix': '1}}', 'suffix' : '' }),
        (1, 1, '{{ \'%s\' }}', { 'prefix': '1\'}}', 'suffix' : '' }),
        (1, 1, '{{ "%s" }}', { 'prefix': '1"}}', 'suffix' : '' }),
        (1, 3, '{{ """%s""" }}', { 'prefix': '1"}}', 'suffix' : '' }), # {{"""%s"""}} -> {{"""1"}}
        (1, 2, '{{ "1"|join(%s) }}', { 'prefix': '1)}}', 'suffix' : '' }),
        (1, 2, '{{ "1"|join(\'%s\') }}', { 'prefix': '1\')}}', 'suffix' : '' }),
        (1, 2, '{{ "1"|join("%s") }}', { 'prefix': '1")}}', 'suffix' : '' }),
        (1, 2, '{{ "1"|join("""%s""") }}', { 'prefix': '1")}}', 'suffix' : '' }), # {{("""%s""")}} -> {{("""1")]}}

        (1, 4, '{{[%s]}}', { 'prefix': '1]}}', 'suffix' : '' }),
        (1, 3, '{{ [\'%s\'] }}', { 'prefix': '1\']}}', 'suffix' : '' }),
        (1, 3, '{{ ["%s"] }}', { 'prefix': '1"]}}', 'suffix' : '' }),
        (1, 3, '{{ ["""%s"""] }}', { 'prefix': '1"]}}', 'suffix' : '' }), # {{["""%s"""]}} -> {{["""1"]}}
        (1, 5, '{{ "1"|join([%s]) }}', { 'prefix': '1])}}', 'suffix' : '' }),
        (1, 5, '{{ "1"|join([\'%s\'])) }}', { 'prefix': '1\'])}}', 'suffix' : '' }),
        (1, 5, '{{ "1"|join(["%s"]) }}', { 'prefix': '1"])}}', 'suffix' : '' }), # {{["""%s"""]}} -> {{["""1"]}}

        (1, 3, '{{{%s}}}', { 'prefix': '1:1}}}', 'suffix' : '' }),
        (1, 3, '{{{1:%s}}}', { 'prefix': '1}}}', 'suffix' : '' }),
        (1, 3, '{{ {1:\'%s\'} }}', { 'prefix': '1\'}}}', 'suffix' : '' }),
        (1, 3, '{{ {1:"%s"} }}', { 'prefix': '1"}}}', 'suffix' : '' }),
        (1, 3, '{{ {1:"""%s"""} }}', { 'prefix': '1"}}}', 'suffix' : '' }),
        (1, 3, '{{{%s:1}}}', { 'prefix': '1:1}}}', 'suffix' : '' }),
        (1, 3, '{{ {\'%s\':1} }}', { 'prefix': '1\':1}}}', 'suffix' : '' }),
        (1, 3, '{{ {"%s":1} }}', { 'prefix': '1":1}}}', 'suffix' : '' }),
        (1, 3, '{{ {"""%s""":1}} }', { 'prefix': '1":1}}}', 'suffix' : '' }),

        # if and for blocks context with {% %}
        (1, 1, '{%% if %s: %%}\n{%% endif %%}', { 'prefix' : '1%}', 'suffix' : '' }),
        (1, 2, '{%% for a in %s: %%}\n{%% endfor %%}', { 'prefix' : '"1"%}', 'suffix' : '' }),
        (1, 1, '{%% if %s==1: %%}\n{%% endif %%}', { 'prefix' : '1%}', 'suffix' : '' }),
        (1, 1, '{%% if \'%s\'==1: %%}\n{%% endif %%}', { 'prefix' : '1\'%}', 'suffix' : '' }),
        (1, 1, '{%% if "%s"==1: %%}\n{%% endif %%}', { 'prefix' : '1"%}', 'suffix' : '' }),
        (1, 1, '{%% if """%s"""==1: %%}\n{%% endif %%}', { 'prefix' : '1"%}', 'suffix' : '' }), # if """%s""": -> if """1":
        (1, 2, '{%% if (1, %s)==1: %%}\n{%% endif %%}', { 'prefix' : '1)%}', 'suffix' : '' }),
        (1, 2, '{%% if (1, \'%s\')==1: %%}\n{%% endif %%}', { 'prefix' : '1\')%}', 'suffix' : '' }),
        (1, 2, '{%% if (1, "%s")==1: %%}\n{%% endif %%}', { 'prefix' : '1")%}', 'suffix' : '' }),
        (1, 2, '{%% if (1, """%s""")==1: %%}\n{%% endif %%}', { 'prefix' : '1")%}', 'suffix' : '' }), # if (1, """%s"""): -> if (1, """1"):

        (1, 3, '{%% if [%s]==1: %%}\n{%% endif %%}', { 'prefix' : '1]%}', 'suffix' : '' }),
        (1, 3, '{%% if [\'%s\']==1: %%}\n{%% endif %%}', { 'prefix' : '1\']%}', 'suffix' : '' }),
        (1, 3, '{%% if ["%s"]==1: %%}\n{%% endif %%}', { 'prefix' : '1"]%}', 'suffix' : '' }),
        (1, 3, '{%% if ["""%s"""]==1: %%}\n{%% endif %%}', { 'prefix' : '1"]%}', 'suffix' : '' }), # if ["""%s"""]: -> if ["""1"]:
        (1, 5, '{%% if (1, [%s])==1: %%}\n{%% endif %%}', { 'prefix' : '1])%}', 'suffix' : '' }),
        (1, 5, '{%% if (1, [\'%s\'])==1: %%}\n{%% endif %%}', { 'prefix' : '1\'])%}', 'suffix' : '' }),
        (1, 5, '{%% if (1, ["%s"])==1: %%}\n{%% endif %%}', { 'prefix' : '1"])%}', 'suffix' : '' }),
        (1, 5, '{%% if (1, ["""%s"""])==1: %%}\n{%% endif %%}', { 'prefix' : '1"])%}', 'suffix' : '' }), # if (1, ["""%s"""]): -> if (1, ["""1"]):

        (1, 3, '{%% for a in {%s}: %%}\n{%% endfor %%}', { 'prefix' : '1:1}%}', 'suffix' : '' }),
        (1, 3, '{%% if {%s:1}==1: %%}\n{%% endif %%}', { 'prefix' : '1:1}%}', 'suffix' : '' }),
        (1, 3, '{%% if {\'%s\':1}==1: %%}\n{%% endif %%}', { 'prefix' : '1\':1}%}', 'suffix' : '' }),
        (1, 3, '{%% if {"%s":1}==1: %%}\n{%% endif %%}', { 'prefix' : '1":1}%}', 'suffix' : '' }),
        (1, 3, '{%% if {"""%s""":1}==1: %%}\n{%% endif %%}', { 'prefix' : '1":1}%}', 'suffix' : '' }), # if {"""%s""":1}: -> if {"""1":1}:
        (1, 3, '{%% if {1:%s}==1: %%}\n{%% endif %%}', { 'prefix' : '1}%}', 'suffix' : '' }),
        (1, 3, '{%% if {1:\'%s\'}==1: %%}\n{%% endif %%}', { 'prefix' : '1\'}%}', 'suffix' : '' }),
        (1, 3, '{%% if {1:"%s"}==1: %%}\n{%% endif %%}', { 'prefix' : '1"}%}', 'suffix' : '' }),
        (1, 3, '{%% if {1:"""%s"""}==1: %%}\n{%% endif %%}', { 'prefix' : '1"}%}', 'suffix' : '' }), # if {1:"""%s""":1}: -> if {1:"""1"}:

        # if and for blocks context with line_statement_prefix
        (5, 5, '# if %s:\n# endif\n', { 'prefix' : '1\n', 'suffix' : '\n' }),
        (5, 5, '# for a in %s:\n# endfor', { 'prefix' : '"1"\n', 'suffix' : '\n' }),
        (5, 5, '# if %s==1:\n# endif', { 'prefix' : '1\n', 'suffix' : '\n' }),
        (5, 5, '# if \'%s\'==1:\n# endif', { 'prefix' : '1\'\n', 'suffix' : '\n' }),
        (5, 5, '# if "%s"==1:\n# endif', { 'prefix' : '1"\n', 'suffix' : '\n' }),
        (5, 5, '# if """%s"""==1:\n# endif', { 'prefix' : '1"\n', 'suffix' : '\n' }), # if """%s""": -> if """1":
        (5, 5, '# if (1, %s)==1:\n# endif', { 'prefix' : '1)\n', 'suffix' : '\n' }),
        (5, 5, '# if (1, \'%s\')==1:\n# endif', { 'prefix' : '1\')\n', 'suffix' : '\n' }),
        (5, 5, '# if (1, "%s")==1:\n# endif', { 'prefix' : '1")\n', 'suffix' : '\n' }),
        (5, 5, '# if (1, """%s""")==1:\n# endif', { 'prefix' : '1")\n', 'suffix' : '\n' }), # if (1, """%s"""): -> if (1, """1"):

        (5, 5, '# if [%s]==1:\n# endif', { 'prefix' : '1]\n', 'suffix' : '\n' }),
        (5, 5, '# if [\'%s\']==1:\n# endif', { 'prefix' : '1\']\n', 'suffix' : '\n' }),
        (5, 5, '# if ["%s"]==1:\n# endif', { 'prefix' : '1"]\n', 'suffix' : '\n' }),
        (5, 5, '# if ["""%s"""]==1:\n# endif', { 'prefix' : '1"]\n', 'suffix' : '\n' }), # if ["""%s"""]: -> if ["""1"]:
        (5, 5, '# if (1, [%s])==1:\n# endif', { 'prefix' : '1])\n', 'suffix' : '\n' }),
        (5, 5, '# if (1, [\'%s\'])==1:\n# endif', { 'prefix' : '1\'])\n', 'suffix' : '\n' }),
        (5, 5, '# if (1, ["%s"])==1:\n# endif', { 'prefix' : '1"])\n', 'suffix' : '\n' }),
        (5, 5, '# if (1, ["""%s"""])==1:\n# endif', { 'prefix' : '1"])\n', 'suffix' : '\n' }), # if (1, ["""%s"""]): -> if (1, ["""1"]):

        (5, 5, '# for a in {%s}:\n# endfor', { 'prefix' : '1:1}\n', 'suffix' : '\n' }),
        (5, 5, '# if {%s:1}==1:\n# endif', { 'prefix' : '1:1}\n', 'suffix' : '\n' }),
        (5, 5, '# if {\'%s\':1}==1:\n# endif', { 'prefix' : '1\':1}\n', 'suffix' : '\n' }),
        (5, 5, '# if {"%s":1}==1:\n# endif', { 'prefix' : '1":1}\n', 'suffix' : '\n' }),
        (5, 5, '# if {"""%s""":1}==1:\n# endif', { 'prefix' : '1":1}\n', 'suffix' : '\n' }), # if {"""%s""":1}: -> if {"""1":1}:
        (5, 5, '# if {1:%s}==1:\n# endif', { 'prefix' : '1}\n', 'suffix' : '\n' }),
        (5, 5, '# if {1:\'%s\'}==1:\n# endif', { 'prefix' : '1\'}\n', 'suffix' : '\n' }),
        (5, 5, '# if {1:"%s"}==1:\n# endif', { 'prefix' : '1"}\n', 'suffix' : '\n' }),
        (5, 5, '# if {1:"""%s"""}==1:\n# endif', { 'prefix' : '1"}\n', 'suffix' : '\n' }), # if {1:"""%s""":1}: -> if {1:"""1"}:

        # Comment blocks
        (5, 1, '{# %s #}', { 'prefix' : '1#}', 'suffix' : '{#' }),

    ]

    def test_reflection_limit(self):

        obj, data = self._get_detection_obj_data('http://127.0.0.1:15001/limit/jinja2?tpl=%s&inj=*&limit=8' % '')

        expected_data = { 'render_tag' : self.expected_data['render_tag'], 'unreliable' : 'Jinja2' }

        self.assertEqual(data, expected_data)

    def test_reflection_quotes(self):

        obj, data = self._get_detection_obj_data(self.url % '')

        result = obj.execute('echo 1"2"')
        self.assertEqual(result, '12')

        result = obj.execute('echo 1\\"2')
        self.assertEqual(result, '1"2')
