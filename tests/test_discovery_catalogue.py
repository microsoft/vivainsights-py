import pathlib
import re
import sys
import unittest

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import yaml

import vivainsights as vi

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOGUE_PATH = ROOT / "vivainsights" / "discovery" / "workflows.yml"

sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import generate_discovery  # noqa: E402
from test_public_api import EXPECTED_PUBLIC_FUNCTIONS  # noqa: E402

REQUIRED_FIELDS = (
    "id",
    "task",
    "intents",
    "python_function",
    "input_grain",
    "required_columns",
    "selected_columns",
    "privacy",
    "returns",
    "return_types",
    "example",
    "runnable",
    "documentation",
    "related",
    "r_function",
    "parity",
)

DOCUMENTATION_TEMPLATE = (
    "https://microsoft.github.io/vivainsights-py/_api/vivainsights.{module}.html"
)


def load_catalogue():
    with CATALOGUE_PATH.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


class TestDiscoveryCatalogue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue = load_catalogue()
        cls.workflows = cls.catalogue["workflows"]

    def test_catalogue_metadata(self):
        self.assertEqual(self.catalogue["schema_version"], 1)
        self.assertEqual(self.catalogue["package"], "vivainsights")
        self.assertEqual(self.catalogue["language"], "python")
        self.assertGreaterEqual(len(self.workflows), 10)

    def test_required_fields_present(self):
        for workflow in self.workflows:
            for field in REQUIRED_FIELDS:
                self.assertIn(field, workflow, f"{workflow.get('id')} missing {field}")

    def test_ids_are_unique_and_kebab_case(self):
        ids = [workflow["id"] for workflow in self.workflows]
        self.assertEqual(len(ids), len(set(ids)))
        for identifier in ids:
            self.assertRegex(identifier, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

    def test_functions_are_public_exports(self):
        for workflow in self.workflows:
            name = workflow["python_function"]
            self.assertIn(name, EXPECTED_PUBLIC_FUNCTIONS)
            self.assertTrue(callable(getattr(vi, name, None)))
            for related in workflow["related"]:
                self.assertIn(related, EXPECTED_PUBLIC_FUNCTIONS)

    def test_every_public_function_is_discoverable(self):
        covered = set()
        for workflow in self.workflows:
            covered.add(workflow["python_function"])
            covered.update(workflow["related"])
        missing = set(EXPECTED_PUBLIC_FUNCTIONS) - covered
        self.assertEqual(missing, set())

    def test_intents_and_privacy_are_populated(self):
        for workflow in self.workflows:
            self.assertGreaterEqual(len(workflow["intents"]), 2)
            self.assertTrue(workflow["privacy"].strip())
            self.assertTrue(workflow["returns"].strip())

    def test_documentation_urls_match_module(self):
        for workflow in self.workflows:
            function = getattr(vi, workflow["python_function"])
            module = function.__module__.split(".")[-1]
            self.assertEqual(
                workflow["documentation"],
                DOCUMENTATION_TEMPLATE.format(module=module),
            )

    def test_return_types_match_signatures(self):
        import inspect

        for workflow in self.workflows:
            function = getattr(vi, workflow["python_function"])
            parameter = inspect.signature(function).parameters.get("return_type")
            if parameter is None:
                self.assertEqual(workflow["return_types"], [])
            else:
                self.assertTrue(workflow["return_types"])
                self.assertIn(parameter.default, workflow["return_types"])

    def test_parity_values_use_vocabulary(self):
        vocabulary = set(self.catalogue["parity_vocabulary"])
        for workflow in self.workflows:
            self.assertIn(workflow["parity"], vocabulary)

    def test_examples_reference_their_function(self):
        for workflow in self.workflows:
            self.assertIn(f"{workflow['python_function']}(", workflow["example"])
            compile(workflow["example"], workflow["id"], "eval")

    def test_runnable_examples_execute(self):
        executed = 0
        for workflow in self.workflows:
            if not workflow["runnable"]:
                continue
            try:
                eval(workflow["example"], {"vi": vi})  # noqa: S307
            except Exception as error:  # pragma: no cover - surfaced as failure
                self.fail(f"{workflow['id']} example failed: {error}")
            finally:
                plt.close("all")
            executed += 1
        self.assertGreaterEqual(executed, 20)


class TestGeneratedDiscoveryArtifacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue = load_catalogue()

    def test_generated_files_are_up_to_date(self):
        guide = generate_discovery.GUIDE_PATH.read_text(encoding="utf-8")
        llms = generate_discovery.LLMS_PATH.read_text(encoding="utf-8")
        self.assertEqual(
            guide.replace("\r\n", "\n"),
            generate_discovery.build_guide(self.catalogue),
        )
        self.assertEqual(
            llms.replace("\r\n", "\n"),
            generate_discovery.build_llms(self.catalogue),
        )

    def test_llms_index_covers_every_workflow(self):
        llms = generate_discovery.LLMS_PATH.read_text(encoding="utf-8")
        for workflow in self.catalogue["workflows"]:
            self.assertIn(f"`{workflow['python_function']}()`", llms)
        self.assertIn("mingroup", llms)
        self.assertIn("return_type", llms)

    def test_guide_documents_every_workflow(self):
        guide = generate_discovery.GUIDE_PATH.read_text(encoding="utf-8")
        for workflow in self.catalogue["workflows"]:
            self.assertIn(f"### {workflow['task']}", guide)

    def test_generated_files_declare_provenance(self):
        for path in (generate_discovery.GUIDE_PATH, generate_discovery.LLMS_PATH):
            text = path.read_text(encoding="utf-8")
            self.assertIn("Do not edit manually", text)
            self.assertRegex(text, re.escape("tools/generate_discovery.py"))


if __name__ == "__main__":
    unittest.main()
