from pathlib import Path
import tempfile
import unittest
import zipfile

from package_skill import package_skill


class PackageSkillTests(unittest.TestCase):
    def test_standalone_reproducible_archive_excludes_user_data_and_keeps_license(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "sample-skill"
            for name, value in {
                "SKILL.md": "---\nname: sample-skill\ndescription: Example\n---\n",
                "vendor/lib/LICENSE.md": "MIT license",
                "scripts/run.py": "print('ok')",
                "scripts/test_run.py": "test only",
                "scripts/__pycache__/run.pyc": "cache",
                "references/.env": "PRIVATE_KEY=secret",
                ".resume-site-work/input/resume.txt": "private resume",
            }.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(value)
            first, second = Path(tmp) / "one.zip", Path(tmp) / "two.zip"
            self.assertEqual(package_skill(root, first)["sha256"], package_skill(root, second)["sha256"])
            with zipfile.ZipFile(first) as archive:
                self.assertEqual(set(archive.namelist()), {
                    "sample-skill/SKILL.md", "sample-skill/vendor/lib/LICENSE.md", "sample-skill/scripts/run.py",
                })
            with self.assertRaises(FileExistsError):
                package_skill(root, first)

    def test_runtime_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skill"
            (root / "references").mkdir(parents=True)
            (root / "SKILL.md").write_text("skill")
            (root / "references" / "outside.txt").symlink_to(Path(tmp) / "outside")
            with self.assertRaisesRegex(ValueError, "Symlinks"):
                package_skill(root, Path(tmp) / "release.zip")


if __name__ == "__main__":
    unittest.main()
