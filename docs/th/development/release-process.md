# ขั้นตอนการออกรุ่น

[หน้าแรก](../index.md) > การพัฒนา > ขั้นตอนการออกรุ่น

[English](../../development/release-process.md) · **ไทย**

binance-th อยู่บน PyPI: <https://pypi.org/project/binance-th/> เวอร์ชันเป็นแบบ **dynamic** — hatchling อ่าน
`binance_th.__version__` จาก `binance_th/__init__.py` จึงไม่มี `version` ใน `pyproject.toml` ให้แก้เวอร์ชันที่นั่น

ตอนออกรุ่นมีสองสิ่งที่เกิดขึ้นแยกกัน: **อัปโหลดขึ้น PyPI** (สคริปต์ในเครื่องแบบใช้ token) และ **GitHub Release**
(เวิร์กโฟลว์ที่ทริกเกอร์ด้วย tag) ทั้งสองแยกจากกันโดยตั้งใจ

## 1. เผยแพร่ขึ้น PyPI — `scripts/publish.sh`

```bash
./scripts/publish.sh
```

สคริปต์นี้จะ:

1. โหลด **เฉพาะ** `PYPI_TOKEN` จาก `.env` ที่ถูก gitignore (parse แบบเจาะจง ไม่ `export` ทั้งไฟล์)
2. อ่านชื่อแพ็กเกจจาก `pyproject.toml` และเวอร์ชันจาก `import binance_th`
3. `uv build` แล้ว `uv run twine check dist/*`
4. ตรวจ token (ต้องขึ้นต้นด้วย `pypi-`) และขอการยืนยัน
5. `uv run twine upload dist/* --username __token__ --password "$PYPI_TOKEN"`

> ⚠ การเผยแพร่เป็น **สาธารณะและย้อนกลับไม่ได้** — เวอร์ชันหนึ่งอัปโหลดซ้ำไม่ได้เด็ดขาด ให้ขยับเวอร์ชันทุกครั้งที่มีการเปลี่ยนแปลง
> token ต้องเป็นแบบ **account-scoped** (token ที่ผูกกับโปรเจกต์อื่นอัปโหลดโปรเจกต์ใหม่ไม่ได้ — จะได้ `403`)

## 2. Tag → GitHub Release — `.github/workflows/release.yml`

```bash
git tag v1.0.0 && git push origin v1.0.0
```

การ push tag `v*` จะทริกเกอร์เวิร์กโฟลว์ **Release** ซึ่งรัน `uv build`, `twine check` และสร้าง GitHub Release
พร้อมแนบ sdist + wheel และ note ที่สร้างอัตโนมัติ มัน **ไม่** เผยแพร่ขึ้น PyPI (จึงไม่ต้องใช้ secret ของ PyPI
หรือ trusted-publisher) — นั่นเป็นหน้าที่ของ `publish.sh`

## ลำดับปกติ

1. ขยับ `__version__`, อัปเดต [`CHANGELOG.md`](../../../CHANGELOG.md), merge เข้า `main`
2. `./scripts/publish.sh` → PyPI
3. `git tag vX.Y.Z && git push origin vX.Y.Z` → GitHub Release

## ดูเพิ่มเติม

- [การร่วมพัฒนา](contributing.md) · [การทดสอบ](testing.md)
- [ADR การแพ็กเกจ](../../plans/adr/ADR-0010-packaging-and-distribution.md)
