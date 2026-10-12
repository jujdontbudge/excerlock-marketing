import test from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {resolve} from 'node:path';
import {projectMemoryAPI} from './project-policy.mjs';

const requirePi = createRequire('/Users/johansardar/.local/lib/node_modules/@earendil-works/pi-coding-agent/package.json');
const {createJiti} = requirePi('jiti');
const jiti = createJiti(import.meta.url, {alias: {
  '@earendil-works/pi-ai': '/Users/johansardar/.local/lib/node_modules/@earendil-works/pi-coding-agent/node_modules/@earendil-works/pi-ai/dist/index.js',
  typebox: requirePi.resolve('typebox'),
}});
const {default: register} = await jiti.import(resolve('.pi/extensions/mem0-local-memory.ts'));
const hooks = [], tools = [], commands = new Map();
const pi = {
  on(name) {hooks.push(name);},
  registerTool(definition) {tools.push(definition);},
  registerCommand(name, definition) {commands.set(name, definition);},
};
register(pi);
const tool = tools.find(t => t.name === 'local_memory');
const ctx = {cwd: process.cwd(), sessionManager: {getSessionId: () => 'cleanup-regression'}};

test('actual shared engine keeps manual tools/commands but registers no automatic hooks', () => {
  assert.deepEqual(hooks, []);
  assert.ok(tool);
  for (const name of ['mem0-status', 'mem0-search', 'mem0-remember', 'memory-review']) assert.ok(commands.has(name));
});
test('new automatic hook names cannot bypass the project adapter', () => {
  projectMemoryAPI(pi).on('future_capture_event', () => {});
  assert.deepEqual(hooks, []);
});
test('unapproved mutation is rejected by the actual shared engine', async () => {
  await assert.rejects(tool.execute('test', {action:'add', text:'unused', approved:false}, undefined, undefined, ctx), /approval/);
});
test('real shared worker status reports effective and engine policy separately', async () => {
  const result = await tool.execute('test', {action:'status'}, undefined, undefined, ctx);
  const status = JSON.parse(result.content[0].text);
  assert.equal(status.autoCapture, false);
  assert.equal(status.automaticRecall, false);
  assert.equal(typeof status.engineAutoCapture, 'boolean');
  assert.equal(typeof status.engineAutomaticRecall, 'boolean');
  assert.equal(status.project, process.cwd());
});
