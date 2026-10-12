"""Offline checks: real CLI/file/media behavior; provider responses are mocked."""
import base64
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
swap = load('swap_runner', 'core/skills/reference-swap/swap.py')
finish = load('finish_runner', 'core/skills/ugc-finish/finish.py')

class Helpers(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR'))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ref = self.root / 'reference.png'
        Image.new('RGB', (320, 480), '#ababab').save(self.ref)
        self.prompt = self.root / 'prompt.txt'
        self.prompt.write_text('Test fixture edit.')
        self.out = self.root / 'roll.png'
        self.state = self.root / 'ledger.json'
    def args(self, *extra):
        return swap.parser().parse_args(['--prompt', str(self.prompt), '--ref', str(self.ref), '--out', str(self.out), *extra])
    def actual(self, *extra):
        return self.args('--state', str(self.state), '--approval', 'offline-test-authorization', '--estimated-cost', '1', *extra)
    def cli(self, script, *extra):
        return subprocess.run([sys.executable, str(ROOT / script), *map(str,extra)], capture_output=True, text=True, check=False)
    def test_dry_run_no_network_credentials_or_writes(self):
        with patch.object(swap, 'credentials', side_effect=AssertionError('credentials accessed')), patch.object(swap, 'request_image', side_effect=AssertionError('network accessed')):
            result = swap.execute(self.args('--dry-run'))
        self.assertEqual(result['status'], 'dry-run')
        self.assertFalse(self.out.exists())
        self.assertFalse(self.state.exists())
    def test_real_cli_dry_run(self):
        result = self.cli('core/skills/reference-swap/swap.py', '--prompt', self.prompt, '--ref', self.ref, '--out', self.out, '--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'dry-run')
    def test_parallel_roll_option_rejected(self):
        result = self.cli('core/skills/reference-swap/swap.py', '--prompt', self.prompt, '--ref', self.ref, '--out', self.out, '--dry-run', '-n', '2')
        self.assertNotEqual(result.returncode, 0)
    def test_unapproved_call_rejected_before_credentials(self):
        with patch.object(swap, 'credentials', side_effect=AssertionError('credentials accessed')):
            with self.assertRaises(ValueError): swap.execute(self.args())
    def test_output_overwrite_rejected(self):
        self.out.write_bytes(b'original')
        with self.assertRaises(FileExistsError): swap.execute(self.args('--dry-run'))
        self.assertEqual(self.out.read_bytes(), b'original')
    def test_higher_resolution_requires_exception(self):
        with self.assertRaises(ValueError): swap.execute(self.args('--dry-run', '--size', '2K'))
        self.assertEqual(swap.execute(self.args('--dry-run', '--size', '2K', '--exception-approval', 'offline-test'))['size'], '2K')
    def test_bad_cost_rejected(self):
        for value in [0, -1, float('inf'), float('nan')]:
            a = self.actual(); a.estimated_cost = value
            with self.assertRaises(ValueError): swap.validate(a)
    def test_state_input_collision_rejected(self):
        a = self.actual(); a.state = self.ref
        with self.assertRaises(ValueError): swap.validate(a)
    def test_fourth_attempt_rejected_before_provider(self):
        self.state.write_text(json.dumps({'attempts':[{'status':'failed'}]*3}))
        with patch.object(swap, 'credentials', side_effect=AssertionError('credentials accessed')):
            with self.assertRaises(ValueError): swap.execute(self.actual())
    def test_dry_run_respects_existing_attempt_ledger(self):
        self.state.write_text(json.dumps({'attempts':[{'status':'failed'}]*3}))
        with self.assertRaises(ValueError): swap.execute(self.args('--state', str(self.state), '--dry-run'))
    def test_failed_mock_submission_counted_and_no_output(self):
        with patch.object(swap, 'credentials', return_value='test-fixture'), patch.object(swap, 'request_image', side_effect=ValueError('Provider returned no image')):
            with self.assertRaises(ValueError): swap.execute(self.actual())
        self.assertFalse(self.out.exists())
        self.assertEqual(json.loads(self.state.read_text())['attempts'][0]['status'], 'failed')
    def test_mock_submission_saves_valid_png_and_receipt(self):
        with patch.object(swap, 'credentials', return_value='test-fixture'), patch.object(swap, 'request_image', return_value=self.ref.read_bytes()):
            result = swap.execute(self.actual())
        with Image.open(self.out) as im: im.verify()
        self.assertEqual(result['attempt'], 1)
        self.assertEqual(json.loads(self.state.read_text())['attempts'][0]['status'], 'saved')
    def test_project_lock_prevents_parallel_paid_requests_across_ledgers(self):
        with patch.object(swap, 'ROOT', self.root), swap.project_roll_lock():
            with patch.object(swap, 'credentials', side_effect=AssertionError('credentials accessed')):
                with self.assertRaises(BlockingIOError): swap.execute(self.actual())
    def test_finish_preserves_exif_display_orientation(self):
        exif = Image.Exif(); exif[274] = 6
        Image.new('RGB', (320,480)).save(self.ref, exif=exif)
        output = self.root / 'oriented.jpg'
        finish.finish_image(self.ref, output, 2.5)
        with Image.open(output) as image:
            self.assertEqual(image.size, (480,320)); self.assertFalse(image.getexif())
    def test_provider_no_image_is_failure(self):
        with patch.object(swap.urllib.request, 'urlopen', return_value=io.BytesIO(b'{"candidates":[]}')):
            with self.assertRaises(ValueError): swap.request_image(self.args(), b'{}', 'test-fixture')
    def test_failure_exit_is_nonzero(self):
        with patch.object(swap, 'execute', side_effect=ValueError('No image')), contextlib.redirect_stderr(io.StringIO()):
            code = swap.main(['--prompt', str(self.prompt), '--ref', str(self.ref), '--out', str(self.out), '--dry-run'])
        self.assertEqual(code, 1)
    def test_finish_does_not_upscale_and_strips_exif(self):
        exif = Image.Exif(); exif[270] = 'private fixture metadata'
        Image.new('RGB', (320,480)).save(self.ref, exif=exif)
        destination = self.root / 'final'
        result = self.cli('core/skills/ugc-finish/finish.py', self.ref, '--out', destination)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = destination / 'reference.jpg'
        with Image.open(output) as image:
            self.assertEqual(image.size, (320,480)); self.assertFalse(image.getexif())
        receipt = json.loads(output.with_suffix('.jpg.finish.json').read_text())
        self.assertEqual(receipt['route'], 'local-approximation')
    def test_finish_downsizes_large_image(self):
        self.assertEqual(finish.to_1080(Image.new('RGB', (1440,2160))).size, (1080,1620))
    def test_finish_overwrite_and_repeat_rejected(self):
        destination = self.root / 'final'
        first = self.cli('core/skills/ugc-finish/finish.py', self.ref, '--out', destination)
        self.assertEqual(first.returncode, 0, first.stderr)
        again = self.cli('core/skills/ugc-finish/finish.py', self.ref, '--out', destination)
        self.assertNotEqual(again.returncode, 0)
        repeat = self.cli('core/skills/ugc-finish/finish.py', destination / 'reference.jpg', '--out', self.root / 'twice')
        self.assertNotEqual(repeat.returncode, 0)
    def test_finish_basename_collisions_rejected(self):
        other = self.ref.with_suffix('.jpg'); Image.new('RGB', (32,48)).save(other)
        result = self.cli('core/skills/ugc-finish/finish.py', self.ref, other, '--out', self.root / 'final')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / 'final').exists())
    def test_telegram_requires_explicit_destination_without_sending(self):
        result = self.cli('core/skills/ugc-finish/finish.py', self.ref, '--out', self.root / 'final', '--telegram')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / 'final').exists())
    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'ffmpeg/ffprobe required')
    def test_real_video_finish_preserves_smaller_resolution(self):
        source = self.root / 'clip.mp4'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=gray:s=320x480:r=30','-t','0.3','-c:v','libx264','-pix_fmt','yuv420p',str(source)],check=True)
        result = self.cli('core/skills/ugc-finish/finish.py', source, '--out', self.root / 'final')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',str(self.root / 'final/clip.mp4')],text=True)
        self.assertEqual(json.loads(data)['streams'][0], {'width':320,'height':480})

if __name__ == '__main__': unittest.main()
