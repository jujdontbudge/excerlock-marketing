"""Local regression checks; the separate live add probe exercises Luna once."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import pytest
from worker import configure_environment, create_memory, no_python_network, state_path, validate

SCRIPT = Path(__file__).with_name('worker.py')
PROJECT = Path('/tmp/excerlock-mem0-test-project')
OTHER_CHECKOUT = PROJECT.with_name('excerlock-mem0-test-worktree')
PROJECT_ID = 'github.com/example/mem0-test-project'
OTHER_PROJECT_ID = 'github.com/example/other-project'
MARKETING_PROJECT_ID = 'github.com/JohanSardar/excerlock-marketing'


def start_worker(request, project=PROJECT):
    env = dict(os.environ, PATH='/usr/bin:/bin')  # No Node: read/search/delete must not need an LLM.
    read_end, write_end = os.pipe()
    with os.fdopen(write_end, 'w') as writer:
        writer.write(json.dumps(request))
    process = subprocess.Popen([sys.executable, str(SCRIPT), '--project-dir', str(project)],
                               stdin=read_end, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                               text=True, env=env)
    os.close(read_end)
    return process


def invoke(request, project=PROJECT):
    process = start_worker({'project_id': PROJECT_ID, **request}, project)
    stdout, _ = process.communicate(timeout=40)
    assert process.returncode == 0, stdout
    return json.loads(stdout)


@pytest.mark.parametrize('payload', [
    {}, {'action': 'reset'}, {'action': 'add', 'text': 'not approved'},
    {'action': 'delete', 'approved': False, 'id': 'x'},
    {'action': 'add', 'approved': True, 'text': ''},
    {'action': 'search', 'query': 'x', 'limit': 21},
    {'action': 'get', 'id': '../bad'},
])
def test_reject_bad_or_unapproved_input(payload):
    with pytest.raises((ValueError, TypeError)):
        validate({'project_id': PROJECT_ID, **payload})


@pytest.mark.parametrize('payload', [
    {'action': 'status'},
    {'action': 'status', 'project_id': ''},
    {'action': 'status', 'project_id': 'x' * 256},
    {'action': 'status', 'project_id': 'github.com/example/bad\nid'},
])
def test_reject_missing_or_invalid_project_id(payload):
    with pytest.raises(ValueError):
        validate(payload)


def test_worker_requires_project_id():
    process = start_worker({'action': 'status'})
    stdout, _ = process.communicate(timeout=40)
    assert process.returncode == 2
    assert json.loads(stdout)['error'] == 'ValueError'


def test_project_identity_governs_state_path():
    assert state_path(PROJECT_ID) != state_path(OTHER_PROJECT_ID)
    assert state_path(PROJECT_ID, 'session', 'one') != state_path(OTHER_PROJECT_ID, 'session', 'one')
    assert state_path(MARKETING_PROJECT_ID).name == 'a28edc9fdaabbd8ba7eab23a'


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
    assert status['storage'] == invoke({'action': 'status'}, OTHER_CHECKOUT)['storage']


def test_scope_paths_are_distinct():
    assert state_path(PROJECT_ID, 'project') != state_path(PROJECT_ID, 'session', 'one')
    assert state_path(PROJECT_ID, 'session', 'one') != state_path(PROJECT_ID, 'session', 'two')


def test_new_actions_and_scope_validation():
    validate({'action': 'get_all', 'project_id': PROJECT_ID})
    validate({'action': 'update', 'id': '00000000-0000-0000-0000-000000000000', 'text': 'new', 'approved': True, 'project_id': PROJECT_ID})
    validate({'action': 'delete_all', 'approved': True, 'project_id': PROJECT_ID})
    with pytest.raises(ValueError):
        validate({'action': 'search', 'query': 'x', 'scope': 'session', 'project_id': PROJECT_ID})
    with pytest.raises(ValueError):
        validate({'action': 'add', 'text': 'x', 'approved': True, 'category': 'invalid', 'project_id': PROJECT_ID})


def test_reader_waits_for_in_flight_operation():
    from filelock import FileLock
    state = state_path(PROJECT_ID)
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    with FileLock(str(state / 'operation.lock')):
        reader = start_worker({'action': 'list', 'project_id': PROJECT_ID})
        time.sleep(8)
    stdout, _ = reader.communicate(timeout=40)
    assert reader.returncode == 0, stdout
    assert 'results' in json.loads(stdout)


def test_live_probe_persisted_search_scope_and_delete():
    # Luna extraction was separately live-tested. Seed a direct local test record so
    # this regression suite remains repeatable without another provider request.
    configure_environment()
    no_python_network()
    state = state_path(PROJECT_ID)
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
            assert invoke({'action': 'get', 'id': ident}, OTHER_CHECKOUT)['found'] is True
            assert invoke({'action': 'get', 'id': ident, 'project_id': OTHER_PROJECT_ID})['found'] is False
    finally:
        for ident in ids:
            invoke({'action': 'delete', 'approved': True, 'id': ident})
    for ident in ids:
        assert invoke({'action': 'get', 'id': ident})['found'] is False
    assert not invoke({'action': 'search', 'query': 'Juniper Observatory violet Thursday'})['results']
    assert not list(state_path(PROJECT_ID).rglob('history.db'))
