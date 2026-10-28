import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('project_policy', Path(__file__).resolve().parents[1]/'scripts/project_policy.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PolicyTests(unittest.TestCase):
    def policy(self):
        return dict(version=1, profile='iren', organization='iren', allowed_agents=['codex', 'claude-code', 'ollama'], default_agent='codex', review_agent='claude-code', allow_mirantis_litellm=False)

    def test_allowed_is_not_authenticated(self):
        result = m.route(self.policy(), 'iren', 'ollama')
        self.assertEqual(result['requested_agent'], 'ollama')
        self.assertIn('pending', result['dispatch'])

    def test_cross_org_and_agent_rejected(self):
        for org, agent in [('mirantis', 'codex'), ('personal', 'codex'), ('iren', 'gemini'), ('iren', 'mirantis-litellm')]:
            with self.assertRaises(ValueError):
                m.route(self.policy(), org, agent)

    def test_litellm_opt_in_only_mirantis(self):
        p = self.policy()
        p['allowed_agents'].append('mirantis-litellm')
        p['allow_mirantis_litellm'] = True
        with self.assertRaises(ValueError):
            m.validate(p)
        p['organization'] = 'mirantis'
        m.validate(p)
        p['allow_mirantis_litellm'] = False
        with self.assertRaises(ValueError):
            m.validate(p)

    def test_malformed_and_extra_fields(self):
        for value in [None, [], {}, {'version': True}]:
            with self.assertRaises(ValueError):
                m.validate(value)
        p = self.policy()
        p['api_key'] = 'not-a-real-key'
        with self.assertRaises(ValueError):
            m.validate(p)
        with self.assertRaises(ValueError):
            m.unique_object([('organization', 'iren'), ('organization', 'mirantis')])

    def test_same_primary_reviewer_rejected(self):
        p = self.policy()
        p['review_agent'] = 'codex'
        with self.assertRaises(ValueError):
            m.validate(p)

    def test_same_provider_family_and_empty_agent(self):
        p = self.policy()
        p['allowed_agents'].append('chatgpt')
        p['review_agent'] = 'chatgpt'
        with self.assertRaises(ValueError):
            m.validate(p)
        with self.assertRaises(ValueError):
            m.route(self.policy(), agent='')

    def test_distinct_profile_same_org(self):
        p = self.policy()
        p['profile'] = 'iren-project-a'
        m.route(p, 'iren-project-a')
        with self.assertRaises(ValueError):
            m.route(p, 'iren')

    def test_cli_rejects_invalid_input(self):
        import json, subprocess, sys, tempfile
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'policy.json'
            for content in ['{"organization":"iren","organization":"mirantis"}', 'x'*16385, json.dumps(self.policy())]:
                path.write_text(content)
                result = subprocess.run([sys.executable, str(Path(m.__file__)), str(path), '--profile', 'other'], capture_output=True, text=True)
                self.assertEqual(result.returncode, 1)
                self.assertIn('No dispatch performed', result.stderr)

    def test_defaults_and_schema_errors(self):
        self.assertEqual(m.route(self.policy())['requested_agent'], 'codex')
        for field, value in [('version', 2), ('organization', '../iren'), ('profile', ''), ('allowed_agents', ['codex','codex']), ('default_agent', 'gemini')]:
            p = self.policy()
            p[field] = value
            with self.assertRaises(ValueError):
                m.validate(p)
