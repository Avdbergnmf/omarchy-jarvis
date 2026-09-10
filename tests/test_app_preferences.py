"""A-029: durable app-open preference records (provenance, precedence, revoke). No
network/desktop calls — pure file-backed state under a temp APP_PREFS_PATH."""
import concurrent.futures
import datetime
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'actions'))
import core


class AppPreferencesTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.path = Path(self._dir.name) / 'app-preferences.json'

    def tearDown(self):
        self._dir.cleanup()

    # --- migration ---

    def test_migration_preserves_exact_ranking(self):
        entries = [{'name': 'Bitwarden', 'exec': 'bitwarden', 'stem': 'bitwarden', 'wmclass': 'bitwarden'},
                   {'name': 'Bitwarden', 'exec': 'flatpak run com.bitwarden.desktop', 'stem': 'com.bitwarden.desktop', 'wmclass': 'com.bitwarden.desktop'}]
        v1 = {'version': 1, 'queries': {'bitwarden': {'weights': {'com.bitwarden.desktop': 3}}}, 'last_open': None}
        self.path.write_text(json.dumps(v1))
        # Ranking must be identical to what v1 itself would have produced.
        self.assertEqual(core.resolve_app('bitwarden', entries, core.load_app_prefs(self.path))['stem'], 'com.bitwarden.desktop')
        prefs = core.load_app_prefs(self.path)
        self.assertEqual(prefs['version'], 2)
        migrated = [r for r in prefs['records'].values() if r['authority'] == 'migrated_v1']
        self.assertEqual(len(migrated), 1)
        self.assertEqual(migrated[0]['amount'], 3)
        self.assertEqual(migrated[0]['stem'], 'com.bitwarden.desktop')

    def test_migration_is_idempotent_on_repeated_load(self):
        v1 = {'version': 1, 'queries': {'x': {'weights': {'stem-a': 1}}}, 'last_open': None}
        self.path.write_text(json.dumps(v1))
        first = core.load_app_prefs(self.path)
        second = core.load_app_prefs(self.path)
        self.assertEqual(len(first['records']), 1)
        self.assertEqual(len(second['records']), 1)  # a fresh migration each load, not a duplicate on top of the old file

    def test_v1_backup_created_once_on_first_write_and_never_overwritten_again(self):
        v1 = {'version': 1, 'queries': {'x': {'weights': {'stem-a': 1}}}, 'last_open': None}
        original_bytes = json.dumps(v1)
        self.path.write_text(original_bytes)
        core.add_preference_record('y', 'stem-b', path=self.path)
        backup = self.path.with_name(self.path.name + '.v1.bak')
        self.assertTrue(backup.is_file())
        self.assertEqual(backup.read_text(), original_bytes)
        backup.write_text('do-not-touch')
        core.add_preference_record('z', 'stem-c', path=self.path)
        self.assertEqual(backup.read_text(), 'do-not-touch', 'a second write must not re-create or clobber the backup')

    def test_unknown_version_is_quarantined_not_silently_overwritten(self):
        garbage = json.dumps({'version': 99, 'nonsense': True})
        self.path.write_text(garbage)
        self.assertEqual(core.load_app_prefs(self.path)['records'], {}, 'an unreadable version reads as empty, not guessed at')
        core.add_preference_record('q', 's', path=self.path)
        quarantined = list(self.path.parent.glob(self.path.name + '.quarantined-*'))
        self.assertEqual(len(quarantined), 1)
        self.assertEqual(quarantined[0].read_text(), garbage)
        self.assertEqual(json.loads(self.path.read_text())['version'], core.PREFS_VERSION)

    def test_corrupt_json_is_quarantined_not_silently_overwritten(self):
        self.path.write_text('{not valid json at all')
        core.add_preference_record('q', 's', path=self.path)
        quarantined = list(self.path.parent.glob(self.path.name + '.quarantined-*'))
        self.assertEqual(len(quarantined), 1)
        self.assertEqual(quarantined[0].read_text(), '{not valid json at all')

    def test_malformed_individual_records_are_dropped_not_fatal(self):
        good = dict(id='pref_good', type='app_open_weight', query='q', stem='s', amount=1,
                    source={'run_id': None, 'event': 'correction'}, created_at=core._now_iso(),
                    authority='explicit_correction', confidence=1.0, supersedes=None, revokes=None,
                    expiry=None, status='active')
        data = {'version': 2, 'records': {'pref_good': good, 'pref_bad': {'id': 'pref_bad', 'type': 'app_open_weight'}}, 'last_open': None}
        self.path.write_text(json.dumps(data))
        prefs = core.load_app_prefs(self.path)
        self.assertEqual(list(prefs['records']), ['pref_good'])

    # --- precedence ---

    def test_explicit_authority_outranks_any_amount_of_inferred_repetition(self):
        for _ in range(50):
            core.add_preference_record('spotify', 'spotify-inferred', authority='inferred', confidence=0.2, path=self.path)
        core.add_preference_record('spotify', 'spotify-explicit', authority='explicit_correction', path=self.path)
        prefs = core.load_app_prefs(self.path)
        weights = core.query_weights('spotify', prefs)
        self.assertGreater(weights['spotify-explicit'], weights['spotify-inferred'],
                            'one explicit correction must outrank 50 inferred bumps by repetition')

    def test_migrated_v1_and_new_explicit_corrections_combine_in_the_same_tier(self):
        v1 = {'version': 1, 'queries': {'q': {'weights': {'stem-a': 2}}}, 'last_open': None}
        self.path.write_text(json.dumps(v1))
        core.add_preference_record('q', 'stem-a', authority='explicit_correction', path=self.path)
        weights = core.query_weights('q', core.load_app_prefs(self.path))
        self.assertEqual(weights['stem-a'], (2 + 1) * core.EXPLICIT_TIER_MULTIPLIER)

    def test_expired_record_does_not_contribute(self):
        past = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).isoformat()
        core.add_preference_record('q', 'stem-a', expiry=past, path=self.path)
        weights = core.query_weights('q', core.load_app_prefs(self.path))
        self.assertNotIn('stem-a', weights)

    def test_future_expiry_still_contributes(self):
        future = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)).isoformat()
        core.add_preference_record('q', 'stem-a', expiry=future, path=self.path)
        weights = core.query_weights('q', core.load_app_prefs(self.path))
        self.assertIn('stem-a', weights)

    # --- inspect / revoke / restore ---

    def test_revoke_and_restore_round_trip(self):
        record = core.add_preference_record('q', 'stem-a', path=self.path)
        self.assertIn('stem-a', core.query_weights('q', core.load_app_prefs(self.path)))
        revoked = core.revoke_preference(record['id'], path=self.path)
        self.assertEqual(revoked['status'], 'revoked')
        self.assertNotIn('stem-a', core.query_weights('q', core.load_app_prefs(self.path)))
        restored = core.restore_preference(record['id'], path=self.path)
        self.assertEqual(restored['status'], 'active')
        self.assertIn('stem-a', core.query_weights('q', core.load_app_prefs(self.path)))

    def test_revoke_and_restore_are_idempotent(self):
        record = core.add_preference_record('q', 'stem-a', path=self.path)
        core.revoke_preference(record['id'], path=self.path)
        again = core.revoke_preference(record['id'], path=self.path)  # already revoked — no-op, no error
        self.assertEqual(again['status'], 'revoked')

    def test_revoke_unknown_record_raises(self):
        with self.assertRaisesRegex(ValueError, 'Unknown preference record'):
            core.revoke_preference('pref_nonexistent', path=self.path)

    def test_inspect_filters_by_query_and_orders_newest_first(self):
        core.add_preference_record('alpha', 'stem-1', path=self.path)
        core.add_preference_record('beta', 'stem-2', path=self.path)
        second = core.add_preference_record('alpha', 'stem-3', path=self.path)
        alpha_only = core.inspect_preferences('alpha', path=self.path)
        self.assertEqual({r['stem'] for r in alpha_only}, {'stem-1', 'stem-3'})
        self.assertEqual(alpha_only[0]['id'], second['id'], 'newest first')

    def test_inspect_includes_revoked_records_for_transparency(self):
        record = core.add_preference_record('q', 'stem-a', path=self.path)
        core.revoke_preference(record['id'], path=self.path)
        statuses = {r['status'] for r in core.inspect_preferences('q', path=self.path)}
        self.assertEqual(statuses, {'revoked'})

    # --- provenance fields ---

    def test_record_carries_provenance_fields(self):
        record = core.add_preference_record('q', 'stem-a', run_id='run-123', path=self.path)
        self.assertTrue(record['id'].startswith('pref_'))
        self.assertEqual(record['type'], 'app_open_weight')
        self.assertEqual(record['source'], {'run_id': 'run-123', 'event': 'correction'})
        self.assertEqual(record['authority'], 'explicit_correction')
        self.assertEqual(record['confidence'], 1.0)
        self.assertIn('created_at', record)
        self.assertIsNone(record['supersedes'])
        self.assertIsNone(record['revokes'])
        self.assertEqual(record['status'], 'active')

    def test_unknown_authority_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unknown preference authority'):
            core.add_preference_record('q', 'stem-a', authority='made-up', path=self.path)

    # --- bounded growth ---

    def test_bounded_growth_prunes_oldest_revoked_before_active(self):
        with patch.object(core, 'PREF_RECORD_KEEP', 5):
            ids = [core.add_preference_record('q', f'stem-{i}', path=self.path)['id'] for i in range(5)]
            core.revoke_preference(ids[0], path=self.path)
            core.revoke_preference(ids[1], path=self.path)
            core.add_preference_record('q', 'stem-new', path=self.path)  # pushes total to 6, over the cap of 5
            prefs = core.load_app_prefs(self.path)
            self.assertEqual(len(prefs['records']), 5)
            self.assertNotIn(ids[0], prefs['records'], 'the oldest revoked record is pruned first')
            self.assertIn('stem-new', {r['stem'] for r in prefs['records'].values()})

    # --- concurrency / locking ---

    def test_concurrent_writers_do_not_lose_updates(self):
        def add(i):
            return core.add_preference_record('concurrent', f'stem-{i}', path=self.path)['id']
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
            ids = list(pool.map(add, range(40)))
        self.assertEqual(len(set(ids)), 40, 'every concurrent writer must get a unique id, none lost')
        prefs = core.load_app_prefs(self.path)
        self.assertEqual(len(prefs['records']), 40, 'no lost updates across concurrent read-modify-write cycles')


if __name__ == '__main__':
    unittest.main()
