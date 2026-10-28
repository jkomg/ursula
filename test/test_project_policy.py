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


class PolicyV2Tests(unittest.TestCase):
    def policy(self):
        return dict(version=2, profile='mirantis', organization='mirantis',
                    allowed_agents=['claude-code', 'codex', 'mirantis-litellm'],
                    primary_order=['claude-code', 'codex'],
                    review_order=['codex', 'claude-code', 'mirantis-litellm'],
                    allow_mirantis_litellm=True)

    def test_primary_failover_in_order(self):
        self.assertEqual(m.route(self.policy())['requested_agent'], 'claude-code')
        self.assertEqual(m.route(self.policy(), unavailable=('claude-code',))['requested_agent'], 'codex')
        with self.assertRaises(ValueError):
            m.route(self.policy(), unavailable=('claude-code', 'codex'))

    def test_reviewer_is_other_family_then_gateway(self):
        self.assertEqual(m.reviewer(self.policy(), 'claude-code')['reviewer'], 'codex')
        self.assertEqual(m.reviewer(self.policy(), 'codex')['reviewer'], 'claude-code')
        r = m.reviewer(self.policy(), 'claude-code', ('codex',))
        self.assertEqual(r['reviewer'], 'mirantis-litellm')
        self.assertTrue(r['verify_model_family'])
        with self.assertRaises(ValueError):
            m.reviewer(self.policy(), 'claude-code', ('codex', 'mirantis-litellm'))

    def test_gateway_cannot_be_primary(self):
        p = self.policy()
        p['primary_order'] = ['mirantis-litellm', 'codex']
        with self.assertRaises(ValueError):
            m.validate(p)
        with self.assertRaises(ValueError):
            m.route(self.policy(), agent='mirantis-litellm')

    def test_every_primary_needs_other_family_reviewer(self):
        p = self.policy()
        p['review_order'] = ['codex']
        p['primary_order'] = ['claude-code', 'codex']
        with self.assertRaises(ValueError):
            m.validate(p)

    def test_generic_litellm_any_org_but_mirantis_one_stays_scoped(self):
        p = dict(self.policy(), profile='personal', organization='personal', allow_mirantis_litellm=False,
                 allowed_agents=['claude-code', 'chatgpt', 'litellm'], primary_order=['claude-code'],
                 review_order=['chatgpt', 'litellm'])
        m.validate(p)
        p['allowed_agents'].append('mirantis-litellm')
        with self.assertRaises(ValueError):
            m.validate(p)

    def test_v2_rejects_v1_fields_and_unlisted_agents(self):
        p = self.policy()
        p['default_agent'] = 'codex'
        with self.assertRaises(ValueError):
            m.validate(p)
        p = self.policy()
        p['review_order'] = ['gemini']
        with self.assertRaises(ValueError):
            m.validate(p)

    def test_cli_review_route(self):
        import json, subprocess, sys, tempfile
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'policy.json'
            path.write_text(json.dumps(self.policy()))
            out = subprocess.run([sys.executable, str(Path(m.__file__)), str(path), '--review-for', 'claude-code',
                                  '--unavailable', 'codex'], capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertEqual(json.loads(out.stdout)['review']['reviewer'], 'mirantis-litellm')
            bad = subprocess.run([sys.executable, str(Path(m.__file__)), str(path), '--unavailable', 'nobody'],
                                 capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1)

    def test_explicit_agent_respects_order_and_availability(self):
        p = self.policy()
        p['allowed_agents'].append('gemini')
        with self.assertRaises(ValueError):
            m.route(p, agent='gemini')
        with self.assertRaises(ValueError):
            m.route(self.policy(), agent='codex', unavailable=('codex',))
        with self.assertRaises(ValueError):
            m.reviewer(p, 'gemini')
