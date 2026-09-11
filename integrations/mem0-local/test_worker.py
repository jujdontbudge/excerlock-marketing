"""Local regression checks; the separate live add probe exercises Luna once."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest
from worker import configure_environment, create_memory, no_python_network, state_path, validate

SCRIPT = Path(__file__).with_name('worker.py')
PROJECT = Path('/tmp/excerlock-mem0-test-project')
PROJECT_ID = 'github.com/example/mem0-test-project'
MARKETING_PROJECT_ID = 'github.com/JohanSardar/excerlock-marketing'


def invoke(request, project=PROJECT):
    request = {'project_id': PROJECT_ID, **request}
    env = dict(os.environ, PATH='/usr/bin:/bin')  # No Node: read/search/delete must not need an LLM.
    result = subprocess.run([sys.executable, str(SCRIPT), '--project-dir', str(project)],
                            input=json.dumps(request), capture_output=True, text=True,
                            env=env, timeout=40, check=False)
    assert result.returncode == 0, result.stdout
    return json.loads(result.stdout)


@pytest.mark.parametrize('payload', [
    {}, {'action': 'reset'}, {'action': 'add', 'text': 'not approved'},
    {'action': 'delete', 'approved': False, 'id': 'x'},
    {'action': 'add', 'approved': True, 'text': ''},
    {'action': 'search', 'query': 'x', 'limit': 21},
    {'action': 'get', 'id': '../bad'},
])
def test_reject_bad_or_unapproved_input(payload):
    with pytest.raises((ValueError, TypeError)):
        validate(payload)


def test_scope_isolation_and_normalization(tmp_path):
    assert state_path(tmp_path / 'a') != state_path(tmp_path / 'b')
    assert state_path(tmp_path / 'a' / '..') == state_path(tmp_path)


def test_stable_project_identity_across_clones_and_worktrees(tmp_path):
    first_checkout = tmp_path / 'firstmate' / 'projects' / 'marketing'
    second_checkout = tmp_path / 'treehouse' / 'task-123'
    assert state_path(first_checkout, project_id=PROJECT_ID) == state_path(second_checkout, project_id=PROJECT_ID)
    assert state_path(first_checkout, project_id=PROJECT_ID) != state_path(
        second_checkout,
        project_id='github.com/JohanSardar/excerlock-app',
    )
    assert state_path(first_checkout, project_id=MARKETING_PROJECT_ID).name == 'a28edc9fdaabbd8ba7eab23a'


def test_config_status_offline():
    status = invoke({'action': 'status'})
    assert status['reasoning'] == 'max'
    assert status['autoCapture'] is False
    assert status['automaticRecall'] is True
    assert status['searchThreshold'] == 0.3
    assert status['scopes'] == ['project', 'session']
    assert status['telemetry'] is False
    assert status['rawHistory'] == 'in-memory only'
    assert status['projectId'] == PROJECT_ID


def test_scope_paths_are_distinct():
    assert state_path(PROJECT, 'project') != state_path(PROJECT, 'session', 'one')
    assert state_path(PROJECT, 'session', 'one') != state_path(PROJECT, 'session', 'two')


def test_new_actions_and_scope_validation():
    validate({'action': 'get_all'})
    validate({'action': 'update', 'id': '00000000-0000-0000-0000-000000000000', 'text': 'new', 'approved': True})
    validate({'action': 'delete_all', 'approved': True})
    with pytest.raises(ValueError):
        validate({'action': 'search', 'query': 'x', 'scope': 'session'})
    with pytest.raises(ValueError):
        validate({'action': 'add', 'text': 'x', 'approved': True, 'category': 'invalid'})


def test_live_probe_persisted_search_scope_and_delete():
    # Luna extraction was separately live-tested. Seed a direct local test record so
    # this regression suite remains repeatable without another provider request.
    configure_environment()
    no_python_network()
    state = state_path(PROJECT, project_id=PROJECT_ID)
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    memory = create_memory(state)
    try:
        result = memory.add('The fictional Juniper Observatory project uses a violet dashboard and holds its review day on Thursday.', user_id='johansardar', metadata={'source': 'repeatable-test'}, infer=False)
        ids = [m['id'] for m in result['results'] if m['event'] == 'ADD']
    finally:
        memory.db.close()
        memory.vector_store.client.close()
    assert ids
    try:
        results = invoke({'action': 'search', 'query': 'What color is Juniper Observatory dashboard?'})
        assert any(x['id'] in ids for x in results['results'])
        listing = invoke({'action': 'list'})
        assert any(x['id'] in ids for x in listing['results'])
        for ident in ids:
            assert invoke({'action': 'get', 'id': ident})['found'] is True
            assert invoke(
                {'action': 'get', 'id': ident, 'project_id': 'github.com/example/other-project'},
                PROJECT.with_name('mem0-other-test-project'),
            )['found'] is False
    finally:
        for ident in ids:
            invoke({'action': 'delete', 'approved': True, 'id': ident})
    for ident in ids:
        assert invoke({'action': 'get', 'id': ident})['found'] is False
    assert not invoke({'action': 'search', 'query': 'Juniper Observatory violet Thursday'})['results']
    assert not list(state_path(PROJECT, project_id=PROJECT_ID).rglob('history.db'))
