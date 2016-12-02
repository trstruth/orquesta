# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from orchestra import exceptions as exc
from orchestra.expressions import base as expressions


class YAQLFacadeEvaluationTest(unittest.TestCase):

    def test_basic_eval(self):
        expr = '<% $.foo %>'

        data = {'foo': 'bar'}

        self.assertEqual('bar', expressions.evaluate(expr, data))

    def test_basic_eval_undefined(self):
        expr = '<% $.foo %>'

        data = {}

        self.assertRaises(
            exc.ExpressionEvaluationException,
            expressions.evaluate,
            expr,
            data
        )

    def test_nested_eval(self):
        expr = '<% $.nested.foo %>'

        data = {
            'nested': {
                'foo': 'bar'
            }
        }

        self.assertEqual('bar', expressions.evaluate(expr, data))

    def test_multi_eval(self):
        expr = '<% $.foo %> and <% $.marco %>'

        data = {
            'foo': 'bar',
            'marco': 'polo'
        }

        self.assertEqual('bar and polo', expressions.evaluate(expr, data))

    def test_eval_recursive(self):
        expr = '<% $.fee %>'

        data = {
            'fee': '<% $.fi %>',
            'fi': '<% $.fo %>',
            'fo': '<% $.fum %>',
            'fum': 'fee-fi-fo-fum'
        }

        self.assertEqual('fee-fi-fo-fum', expressions.evaluate(expr, data))

    def test_multi_eval_recursive(self):
        expr = '<% $.fee %> <% $.im %>'

        data = {
            'fee': '<% $.fi %>',
            'fi': '<% $.fo %>',
            'fo': '<% $.fum %>',
            'fum': 'fee-fi-fo-fum!',
            'im': '<% $.hungry %>',
            'hungry': 'i\'m hungry!'
        }

        self.assertEqual(
            'fee-fi-fo-fum! i\'m hungry!',
            expressions.evaluate(expr, data)
        )

    def test_type_preservation(self):
        data = {
            'k1': 101,
            'k2': 1.999,
            'k3': True,
            'k4': [1, 2],
            'k5': {'k': 'v'},
            'k6': None
        }

        self.assertEqual(
            data['k1'],
            expressions.evaluate('<% $.k1 %>', data)
        )

        self.assertEqual(
            data['k2'],
            expressions.evaluate('<% $.k2 %>', data)
        )

        self.assertTrue(expressions.evaluate('<% $.k3 %>', data))

        self.assertListEqual(
            data['k4'],
            expressions.evaluate('<% $.k4 %>', data)
        )

        self.assertDictEqual(
            data['k5'],
            expressions.evaluate('<% $.k5 %>', data)
        )

        self.assertIsNone(expressions.evaluate('<% $.k6 %>', data))

    def test_type_string_detection(self):
        expr = '<% $.foo %> -> <% $.bar %>'

        data = {
            'foo': 101,
            'bar': 201
        }

        self.assertEqual('101 -> 201', expressions.evaluate(expr, data))

    def test_custom_function(self):
        expr = '<% json(\'{"a": 123}\') %>'

        self.assertDictEqual({'a': 123}, expressions.evaluate(expr))

    def test_custom_function_failure(self):
        expr = '<% json(int(123)) %>'

        self.assertRaises(
            exc.ExpressionEvaluationException,
            expressions.evaluate,
            expr
        )