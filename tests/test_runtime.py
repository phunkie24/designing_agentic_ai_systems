"""Offline regression checks for bugs that otherwise interrupt live lessons."""

import ast
import contextlib
from dataclasses import dataclass, field
import io
import json
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional
import unittest
import subprocess
import sys
import re
import uuid
from datetime import datetime
from unittest.mock import Mock

import nbformat
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def definitions(name, index, namespace):
    source = nbformat.read(ROOT / name, as_version=4).cells[index].source
    tree = ast.parse(source)
    tree.body = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.Import, ast.ImportFrom))]
    exec(compile(tree, name, 'exec'), namespace)


class RuntimeTests(unittest.TestCase):
    def test_simulated_approval_rejects_string_false(self):
        env = {'json': json, 're': re, 'List': List, 'Dict': Dict,
               'uuid': uuid, 'datetime': datetime,
               'call_llm': lambda *args, **kwargs: '{"approved": "false"}'}
        definitions('Chapter_13_Human_in_the_Loop.ipynb', 19, env)
        gate = env['ApprovalGate']()
        with contextlib.redirect_stdout(io.StringIO()):
            result = gate.request_approval('test action', 'high', 'test', 'simulation')
        self.assertEqual(result['status'], 'rejected')
        self.assertFalse(gate.approved)

    def test_human_review_handles_null_action_and_uncovered_policy(self):
        response = {'covered_by_policy': True, 'needs_human': False, 'action': None}
        env = {'json': json, 're': re, 'List': List, 'Dict': Dict,
               'call_llm': lambda *args, **kwargs: json.dumps(response)}
        definitions('Chapter_13_Human_in_the_Loop.ipynb', 15, env)
        agent = env['HumanOnTheLoop']([], 'test')
        with contextlib.redirect_stdout(io.StringIO()):
            agent.act('Market closed; no action')
            response['covered_by_policy'] = False
            agent.act('Outside policy')
        self.assertEqual(len(agent.actions), 1)
        self.assertEqual(len(agent.escalated), 1)

    def test_json_fences_and_invalid_json(self):
        from course_utils import parse_json_response
        self.assertEqual(parse_json_response('```json\n{"total": 0}\n```'), {'total': 0})
        self.assertEqual(parse_json_response(' {"total": 0} '), {'total': 0})
        with self.assertRaises(json.JSONDecodeError):
            parse_json_response('```json\n{"total":\n```')

    def test_mcp_step_references(self):
        env = {'json': json, 're': re, 'List': List, 'Dict': Dict, 'MCPClient': object}
        definitions('Chapter_10_Model_Context_Protocol.ipynb', 15, env)
        resolve = env['resolve_step_references']
        results = {1: "{'spend': 48500, 'name': 'Example'}", 2: '{"result": 4850}'}
        self.assertEqual(resolve('$step_1.spend', results), 48500)
        self.assertEqual(resolve('$step_1.spend * 0.1', results), '48500 * 0.1')
        self.assertEqual(resolve('Discount: $step_2.result', results), 'Discount: 4850')
        with self.assertRaises(ValueError):
            resolve('$step_1.missing', results)
        with self.assertRaises(ValueError):
            resolve('$step_3', results)

    def test_blank_base_url_uses_provider_default(self):
        env = {**os.environ, 'DEEPSEEK_API_KEY': 'test-only', 'DEEPSEEK_BASE_URL': '  '}
        result = subprocess.run([sys.executable, '-c',
            'import course_config; print(course_config.base_url)'],
            cwd=ROOT, env=env, capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), 'https://api.deepseek.com/anthropic')

    def test_learning_report_preserves_label_order(self):
        # Grouped generated labels exposed the original non-stratified split bug.
        data = [{'text': f'{label} support request number {i}', 'label': label}
                for label in ['URGENT', 'NORMAL', 'LOW'] for i in range(7)]
        env = {'call_llm': Mock(return_value=json.dumps(data)), 'json': json, 're': re}
        source = nbformat.read(ROOT / 'Chapter_9_Learning_and_Adaptation.ipynb', as_version=4).cells[23].source
        with contextlib.redirect_stdout(io.StringIO()) as output:
            exec(compile(source, 'learning-report', 'exec'), env)
        self.assertEqual(set(env['y_test']), {'URGENT', 'NORMAL', 'LOW'})
        for label in ['URGENT', 'NORMAL', 'LOW']:
            self.assertIn(label, output.getvalue())

    def test_mcp_exports_valid_json_schema(self):
        env = dict(dataclass=dataclass, field=field, Any=Any, Callable=Callable,
                   Dict=Dict, List=List, Optional=Optional)
        definitions('Chapter_10_Model_Context_Protocol.ipynb', 7, env)
        server = env['MCPServer']('test')
        @server.tool('Add one')
        def add_one(value: int) -> int:
            return value + 1
        schema = server.list_tools()[0]['inputSchema']
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate({'value': 4})
        self.assertFalse(server.call_tool('add_one', {'value': 4})['isError'])
        self.assertTrue(server.call_tool('missing', {})['isError'])

    def tool_environment(self, response):
        create = Mock(return_value=response)
        return {'client': SimpleNamespace(messages=SimpleNamespace(create=create)),
                'MODEL': 'test', 'json': json, 'TOOL_SCHEMAS': [], 'TOOL_REGISTRY': {},
                'FINANCIAL_TOOLS': [], 'FINANCIAL_REGISTRY': {},
                'CODE_TOOL_SCHEMA': [], 'CODE_REGISTRY': {}}, create

    def test_tool_loops_stop_on_repeated_tool_requests(self):
        for index, name in [(10, 'run_tool_agent'), (16, 'run_financial_agent'), (18, 'run_code_agent')]:
            with self.subTest(agent=name), contextlib.redirect_stdout(io.StringIO()):
                env, create = self.tool_environment(SimpleNamespace(stop_reason='tool_use', content=[]))
                definitions('Chapters_5_6_Tool_Use_and_Planning.ipynb', index, env)
                result = env[name]('test')
                self.assertEqual(create.call_count, 8)
                self.assertIn('8', result)

    def test_truncated_tool_response_stops_immediately(self):
        for index, name in [(16, 'run_financial_agent'), (18, 'run_code_agent')]:
            with self.subTest(agent=name), contextlib.redirect_stdout(io.StringIO()):
                env, create = self.tool_environment(SimpleNamespace(stop_reason='max_tokens', content=[]))
                definitions('Chapters_5_6_Tool_Use_and_Planning.ipynb', index, env)
                self.assertIn('max_tokens', env[name]('test'))
                self.assertEqual(create.call_count, 1)

    def test_all_notebooks_use_course_kernel_and_install_file(self):
        for path in ROOT.glob('*.ipynb'):
            nb = nbformat.read(path, as_version=4)
            self.assertEqual(nb.metadata.kernelspec.name, 'agentic-ai-course')
            self.assertIn('%pip install -r requirements-lock.txt', nb.cells[2].source)
            self.assertIn('installation', nb.cells[2].metadata.tags)


class FastMCPTests(unittest.IsolatedAsyncioTestCase):
    async def test_generated_server_discovers_and_executes_tools(self):
        from fastmcp import Client
        source = nbformat.read(ROOT / 'Chapter_10_Model_Context_Protocol.ipynb', as_version=4).cells[17].source
        assignment = ast.parse(source).body[0]
        server_source = ast.literal_eval(assignment.value)
        env = {'__name__': 'course_server_test'}
        exec(compile(server_source, 'fastmcp_server.py', 'exec'), env)
        async with Client(env['mcp']) as client:
            tools = await client.list_tools()
            self.assertEqual({tool.name for tool in tools}, {'calculate', 'get_stock_price'})
            result = await client.call_tool('calculate', {'expression': '2 + 3'})
            self.assertEqual(json.loads(result.content[0].text)['result'], 5)


if __name__ == '__main__':
    unittest.main()
