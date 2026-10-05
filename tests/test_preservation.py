import ast
import hashlib
import json
from pathlib import Path
import re
import unittest

import nbformat
from IPython.core.inputtransformer2 import TransformerManager


ROOT = Path(__file__).resolve().parents[1]


class IgnoreDocumentation(ast.NodeTransformer):
    def generic_visit(self, node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if ast.get_docstring(node):
                node.body = node.body[1:]
        return super().generic_visit(node)

    def visit_Assign(self, node):
        if (len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == 'MODEL' and isinstance(node.value, ast.Name)
                and node.value.id == 'MODEL'):
            return None
        return self.generic_visit(node)


def expected_provider_change(source, index):
    source = source.replace('f"${{\'AAPL\': 189.25, \'MSFT\': 430.50}.get(ticker.upper(), 100.0)}"',
                            'f"${ {\'AAPL\': 189.25, \'MSFT\': 430.50}.get(ticker.upper(), 100.0)}"')
    source = source.replace('for t in SupportTier]])}})', 'for t in SupportTier]]))}')
    source = re.sub(r'([\"\'])claude-[\w.-]+\1', 'MODEL', source)
    if index == 3:
        source = 'from course_config import MODEL\n' + source
        source = source.replace('PROVIDER = "anthropic"', 'PROVIDER = "deepseek"')
        source = source.replace('if PROVIDER == "anthropic":', 'if PROVIDER == "deepseek":')
        source = source.replace('Anthropic client ready.', 'DeepSeek client ready.')
    source = source.replace('.messages.create(', '.messages.create(thinking={"type": "disabled"}, ')
    source = source.replace('ChatAnthropic(model=', 'ChatAnthropic(model_kwargs={"thinking": {"type": "disabled"}}, model=')
    if index == 2:
        source = source.replace('pip install ', 'pip install python-dotenv ', 1)
    return source


def normalized_ast(source):
    transformed = TransformerManager().transform_cell(source)
    tree = ast.parse(transformed)
    return ast.dump(IgnoreDocumentation().visit(tree), include_attributes=False)


class PreservationTests(unittest.TestCase):
    def test_all_original_cells_and_logic_are_preserved(self):
        fixes = json.loads((ROOT / 'tests/teaching_fixes.json').read_text(encoding='utf-8'))
        baseline = json.loads((ROOT / 'tests/original_baseline.json').read_text(encoding='utf-8'))
        self.assertEqual(len(baseline), 12)
        for name, original in baseline.items():
            notebook = nbformat.read(ROOT / name, as_version=4)
            nbformat.validate(notebook)
            self.assertEqual(len(original['cells']), len(notebook.cells), name)
            for index, (before, after) in enumerate(zip(original['cells'], notebook.cells)):
                with self.subTest(notebook=name, cell=index):
                    self.assertEqual(before['cell_type'], after.cell_type)
                    if after.cell_type == 'code':
                        # Hashes were derived from the original archive with the same
                        # provider normalization. No local backup is needed after cloning.
                        expected = fixes.get(f'{name}:{index}', before['ast_sha256'])
                        self.assertEqual(hashlib.sha256(normalized_ast(after.source).encode()).hexdigest(), expected)
                        # Running a lesson locally may add outputs without changing its logic.

    def test_every_original_exercise_is_present(self):
        baseline = json.loads((ROOT / 'tests/original_baseline.json').read_text(encoding='utf-8'))
        for name, original in baseline.items():
            notebook = nbformat.read(ROOT / name, as_version=4)
            after = '\n'.join(c.source for c in notebook.cells if c.cell_type == 'markdown')
            self.assertEqual(original['exercises'], re.findall(r'Exercise \d+', after), name)


if __name__ == '__main__':
    unittest.main()
