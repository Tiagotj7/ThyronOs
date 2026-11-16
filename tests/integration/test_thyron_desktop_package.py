"""Testes do pacote thyron-desktop: constroi o .deb e confere o conteudo.

Rodar da raiz do repositorio:
    python3 tests/integration/test_thyron_desktop_package.py -v

Requer dpkg-deb. Se o binario 'dconf' existir, o keyfile tambem e compilado de verdade.
"""
import configparser
import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PKG_DIR = REPO / "packages" / "thyron-desktop"
UUIDS = ("thyron-app-launcher@thyron-os.local", "thyron-lockscreen@thyron-os.local")
EXT_DEST = "usr/share/gnome-shell/extensions"
DCONF_FILE = "etc/dconf/db/local.d/10-thyron-desktop"
WALLPAPERS = {
    "thyron-desktop.png": "thyron-wallpaper-concept-wolf-lakeside.png",
    "thyron-wolf-moon-circle.png": "thyron-wallpaper-concept-wolf-moon-circle.png",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@unittest.skipUnless(shutil.which("dpkg-deb"), "dpkg-deb nao encontrado")
class ThyronDesktopPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="thyron-desktop-test-"))
        out = cls.tmp / "out"
        env = dict(os.environ, OUT_DIR=str(out))
        subprocess.run(["bash", str(PKG_DIR / "build.sh")], check=True,
                       env=env, capture_output=True, text=True)
        debs = list(out.glob("thyron-desktop_*_all.deb"))
        assert len(debs) == 1, debs
        cls.deb = debs[0]
        cls.root = cls.tmp / "root"
        cls.ctrl = cls.tmp / "ctrl"
        subprocess.run(["dpkg-deb", "-x", str(cls.deb), str(cls.root)], check=True)
        subprocess.run(["dpkg-deb", "-e", str(cls.deb), str(cls.ctrl)], check=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def files(self):
        return sorted(p.relative_to(self.root).as_posix()
                      for p in self.root.rglob("*") if p.is_file())

    def test_extensoes_instaladas_em_usr_share(self):
        for uuid in UUIDS:
            base = self.root / EXT_DEST / uuid
            self.assertTrue((base / "extension.js").is_file(), uuid)
            meta = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["uuid"], uuid)
            self.assertIn("50", meta["shell-version"])

    def test_extensao_identica_a_fonte(self):
        for uuid in UUIDS:
            src = REPO / "desktop" / "gnome" / "extensions" / uuid
            for f in src.rglob("*"):
                if f.is_file():
                    dst = self.root / EXT_DEST / uuid / f.relative_to(src)
                    self.assertTrue(dst.is_file(), f"faltando no pacote: {dst}")
                    self.assertEqual(sha256(f), sha256(dst), f.name)

    def test_lockscreen_tem_os_ativos_que_o_codigo_referencia(self):
        assets = self.root / EXT_DEST / UUIDS[1] / "assets"
        code = (self.root / EXT_DEST / UUIDS[1] / "extension.js").read_text(encoding="utf-8")
        for name in ("lock-wallpaper.png", "thyron-logo.png"):
            self.assertIn(name, code)
            self.assertTrue((assets / name).is_file(), name)

    def test_wallpapers_em_backgrounds_thyron(self):
        for dest, src in WALLPAPERS.items():
            got = self.root / "usr/share/backgrounds/thyron" / dest
            self.assertTrue(got.is_file(), dest)
            self.assertEqual(sha256(got), sha256(REPO / "branding" / "wallpapers" / src))

    def test_dconf_ativa_as_duas_extensoes(self):
        cp = configparser.RawConfigParser(interpolation=None)
        cp.read(self.root / DCONF_FILE, encoding="utf-8")
        value = cp.get("org/gnome/shell", "enabled-extensions")
        for uuid in UUIDS:
            self.assertIn(f"'{uuid}'", value)
        # nao pode desligar o dock/tema que ja estavam ativos na VM (Prompt Mestre 25.1)
        for keep in ("dash-to-dock@micxgx.gmail.com",
                     "user-theme@gnome-shell-extensions.gcampax.github.com"):
            self.assertIn(f"'{keep}'", value)

    @unittest.skipUnless(shutil.which("dconf"), "dconf nao encontrado")
    def test_dconf_compila(self):
        out = self.tmp / "local.db"
        r = subprocess.run(["dconf", "compile", str(out), str(self.root / "etc/dconf/db/local.d")],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_dconf_e_conffile(self):
        conffiles = (self.ctrl / "conffiles").read_text().split()
        self.assertEqual(conffiles, ["/" + DCONF_FILE])

    def test_nao_toca_no_gdm_nem_fora_dos_caminhos_previstos(self):
        allowed = ("etc/dconf/db/local.d/", "usr/share/backgrounds/thyron/",
                   "usr/share/gnome-shell/extensions/", "usr/share/doc/thyron-desktop/")
        for f in self.files():
            self.assertTrue(f.startswith(allowed), f"caminho inesperado: {f}")
            self.assertNotIn("gdm", f.lower())

    def test_sem_lixo_de_desenvolvimento(self):
        bad = (".venv", "__pycache__", ".egg-info", ".bak", ".git", ".zip", ".iso")
        for f in self.files():
            self.assertFalse(any(b in f for b in bad), f)

    def test_propriedade_e_permissoes(self):
        for p in self.root.rglob("*"):
            st = p.lstat()
            self.assertFalse(stat.S_IMODE(st.st_mode) & 0o022, f"gravavel por outros: {p}")
        listing = subprocess.run(["dpkg-deb", "-c", str(self.deb)],
                                 capture_output=True, text=True, check=True).stdout
        for line in listing.splitlines():
            self.assertEqual(line.split()[1], "root/root", line)

    def test_campos_de_controle(self):
        info = subprocess.run(["dpkg-deb", "-f", str(self.deb)],
                              capture_output=True, text=True, check=True).stdout
        fields = dict(line.split(": ", 1) for line in info.splitlines()
                      if line and not line.startswith(" "))
        self.assertEqual(fields["Package"], "thyron-desktop")
        self.assertEqual(fields["Architecture"], "all")
        self.assertIn("~dev", fields["Version"])
        self.assertIn("gnome-shell", fields["Depends"])
        self.assertIn("dconf-cli", fields["Depends"])

    def test_scripts_de_mantenedor(self):
        for name in ("postinst", "postrm"):
            script = self.ctrl / name
            self.assertTrue(os.access(script, os.X_OK), name)
            subprocess.run(["sh", "-n", str(script)], check=True)


if __name__ == "__main__":
    unittest.main()
