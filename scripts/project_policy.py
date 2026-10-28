"""Validate nonsecret project routing intent. Does not authenticate or dispatch."""
import argparse
import json
from pathlib import Path
import re

AGENTS = {'claude-code', 'codex', 'chatgpt', 'gemini', 'ollama', 'mirantis-litellm'}
FIELDS = {'version', 'profile', 'organization', 'allowed_agents', 'default_agent', 'review_agent', 'allow_mirantis_litellm'}


def validate(policy):
    if not isinstance(policy, dict) or set(policy) != FIELDS:
        raise ValueError('Policy must contain exactly the documented nonsecret fields')
    if type(policy['version']) is not int or policy['version'] != 1:
        raise ValueError('Unsupported policy version')
    org = policy['organization']
    if not isinstance(org, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,47}', org):
        raise ValueError('Invalid organization slug')
    profile = policy['profile']
    if not isinstance(profile, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,47}', profile):
        raise ValueError('Invalid profile slug')
    agents = policy['allowed_agents']
    if not isinstance(agents, list) or not agents or any(not isinstance(a, str) or a not in AGENTS for a in agents):
        raise ValueError('Invalid allowed agents')
    if len(set(agents)) != len(agents):
        raise ValueError('Duplicate agents')
    if policy['default_agent'] not in agents or policy['review_agent'] not in agents:
        raise ValueError('Primary and reviewer must be allowed agents')
    family = lambda a: 'openai' if a in ('codex', 'chatgpt') else a
    if family(policy['default_agent']) == family(policy['review_agent']):
        raise ValueError('Choose different provider families; also follow project-specific review rules')
    flag = policy['allow_mirantis_litellm']
    if type(flag) is not bool or (flag and org != 'mirantis'):
        raise ValueError('Mirantis LiteLLM requires Mirantis organization and explicit opt-in')
    if ('mirantis-litellm' in agents) != flag:
        raise ValueError('LiteLLM allowlist and opt-in must agree')
    return policy


def route(policy, profile=None, agent=None):
    validate(policy)
    if profile is not None and profile != policy['profile']:
        raise ValueError('Different organization: open a clean project/chat; do not forward context')
    chosen = policy['default_agent'] if agent is None else agent
    if chosen not in policy['allowed_agents']:
        raise ValueError('Agent is not approved for this project')
    return {'organization': policy['organization'], 'requested_agent': chosen,
            'policy_check': 'listed', 'dispatch': 'pending account and capability verification'}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('policy', type=Path)
    p.add_argument('--profile')
    p.add_argument('--agent', choices=sorted(AGENTS))
    a = p.parse_args()
    try:
        with a.policy.open('rb') as f:
            raw = f.read(16385)
        if len(raw) > 16384:
            raise ValueError('Policy exceeds 16 KiB')
        policy = json.loads(raw, object_pairs_hook=unique_object)
        print(json.dumps(route(policy, a.profile, a.agent)))
    except (ValueError, OSError, TypeError):
        p.exit(1, 'Routing blocked: invalid policy, unapproved agent or organization mismatch. No dispatch performed.\n')


if __name__ == '__main__':
    main()
