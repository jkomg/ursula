"""Validate nonsecret project routing intent. Does not authenticate or dispatch."""
import argparse
import json
from pathlib import Path
import re

AGENTS = {'claude-code', 'codex', 'chatgpt', 'gemini', 'ollama', 'litellm', 'mirantis-litellm'}
GATEWAYS = {'litellm', 'mirantis-litellm'}
COMMON = {'version', 'profile', 'organization', 'allowed_agents', 'allow_mirantis_litellm'}
FIELDS = {1: COMMON | {'default_agent', 'review_agent'}, 2: COMMON | {'primary_order', 'review_order'}}


def family(agent):
    # A gateway's family depends on the model it serves; dispatch must check the actual model.
    if agent in ('codex', 'chatgpt'):
        return 'openai'
    if agent == 'claude-code':
        return 'anthropic'
    return 'gateway' if agent in GATEWAYS else agent


def agent_list(value, allowed, name):
    if not isinstance(value, list) or not value or any(not isinstance(a, str) or a not in allowed for a in value):
        raise ValueError(f'Invalid {name}')
    if len(set(value)) != len(value):
        raise ValueError(f'Duplicate agents in {name}')
    return value


def validate(policy):
    if not isinstance(policy, dict) or type(policy.get('version')) is not int or policy['version'] not in FIELDS:
        raise ValueError('Unsupported policy version')
    if set(policy) != FIELDS[policy['version']]:
        raise ValueError('Policy must contain exactly the documented nonsecret fields')
    org = policy['organization']
    if not isinstance(org, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,47}', org):
        raise ValueError('Invalid organization slug')
    profile = policy['profile']
    if not isinstance(profile, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,47}', profile):
        raise ValueError('Invalid profile slug')
    agents = agent_list(policy['allowed_agents'], AGENTS, 'allowed agents')
    flag = policy['allow_mirantis_litellm']
    if type(flag) is not bool or (flag and org != 'mirantis'):
        raise ValueError('Mirantis LiteLLM requires Mirantis organization and explicit opt-in')
    if ('mirantis-litellm' in agents) != flag:
        raise ValueError('LiteLLM allowlist and opt-in must agree')
    if policy['version'] == 1:
        if policy['default_agent'] not in agents or policy['review_agent'] not in agents:
            raise ValueError('Primary and reviewer must be allowed agents')
        if family(policy['default_agent']) == family(policy['review_agent']):
            raise ValueError('Choose different provider families; also follow project-specific review rules')
        return policy
    primaries = agent_list(policy['primary_order'], set(agents), 'primary order')
    reviewers = agent_list(policy['review_order'], set(agents), 'review order')
    if any(a in GATEWAYS for a in primaries):
        raise ValueError('A model gateway reviews; it cannot be primary because it holds no connectors')
    for p in primaries:
        if not any(family(r) != family(p) for r in reviewers):
            raise ValueError('Every primary needs a reviewer from another provider family')
    return policy


def orders(policy):
    validate(policy)
    if policy['version'] == 1:
        return [policy['default_agent']], [policy['review_agent']]
    return policy['primary_order'], policy['review_order']


def route(policy, profile=None, agent=None, unavailable=()):
    primaries, _ = orders(policy)
    if profile is not None and profile != policy['profile']:
        raise ValueError('Different organization: open a clean project/chat; do not forward context')
    if agent is None:
        chosen = next((a for a in primaries if a not in unavailable), None)
        if chosen is None:
            raise ValueError('No approved primary is available; stop rather than substitute')
    else:
        chosen = agent
    if chosen not in policy['allowed_agents'] or chosen in GATEWAYS:
        raise ValueError('Agent is not approved as primary for this project')
    if policy['version'] >= 2 and (chosen not in primaries or chosen in unavailable):
        raise ValueError('Agent is not an available primary in primary_order')
    return {'organization': policy['organization'], 'requested_agent': chosen,
            'policy_check': 'listed', 'dispatch': 'pending account and capability verification'}


def reviewer(policy, acting, unavailable=()):
    primaries, reviewers = orders(policy)
    if acting not in primaries:
        raise ValueError('Acting agent is not an approved primary')
    for r in reviewers:
        if r != acting and r not in unavailable and family(r) != family(acting):
            return {'organization': policy['organization'], 'reviewer': r,
                    'skipped': [s for s in reviewers[:reviewers.index(r)]],
                    'verify_model_family': r in GATEWAYS,
                    'dispatch': 'pending account and capability verification'}
    raise ValueError('No independent reviewer available; review stays pending')


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
    p.add_argument('--review-for', choices=sorted(AGENTS), help='acting primary; prints the reviewer to use')
    p.add_argument('--unavailable', default='', help='comma-separated agents whose last executed attempt failed')
    a = p.parse_args()
    try:
        with a.policy.open('rb') as f:
            raw = f.read(16385)
        if len(raw) > 16384:
            raise ValueError('Policy exceeds 16 KiB')
        policy = json.loads(raw, object_pairs_hook=unique_object)
        down = tuple(x for x in a.unavailable.split(',') if x)
        if any(x not in AGENTS for x in down):
            raise ValueError('Unknown agent in --unavailable')
        result = route(policy, a.profile, a.agent, down)
        if a.review_for:
            result['review'] = reviewer(policy, a.review_for, down)
        print(json.dumps(result))
    except (ValueError, OSError, TypeError):
        p.exit(1, 'Routing blocked: invalid policy, unapproved agent, no available route or organization mismatch. No dispatch performed.\n')


if __name__ == '__main__':
    main()
