#!/bin/bash
# Publish binance-th to PyPI using a token from .env (token-based, à la tvkit).
#
# Usage:  ./scripts/publish.sh
# Requires:  PYPI_TOKEN=pypi-... in a gitignored .env, and uv.
#
# ⚠ Publishing is PUBLIC and IRREVERSIBLE — a version can never be re-uploaded.
set -e

# Load ONLY PYPI_TOKEN from .env (parse-only; do NOT `export $(... .env)` — other lines
# in this .env are malformed and would break a whole-file export).
if [ -f .env ]; then
    PYPI_TOKEN=$(sed -n 's/^[[:space:]]*PYPI_TOKEN[[:space:]]*=[[:space:]]*//p' .env | head -1 | tr -d "\"'" | tr -d ' ')
    export PYPI_TOKEN
fi

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 binance-th → PyPI${NC}"
echo "====================="

if ! command -v uv &>/dev/null; then
    echo -e "${RED}❌ uv is required — https://docs.astral.sh/uv/${NC}"
    exit 1
fi

# Name is static; version is DYNAMIC (hatch reads binance_th/__init__.py), so read it
# from the package, not from pyproject['project']['version'] (which does not exist here).
package_name=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['name'])")
package_version=$(uv run python -c "import binance_th; print(binance_th.__version__)")

echo -e "${BLUE}📦 Package: ${package_name} v${package_version}${NC}"
echo -e "${YELLOW}⚠️  Publishes to PRODUCTION PyPI — public and irreversible.${NC}"
echo ""

# Build + validate the artifact
echo -e "${BLUE}🔨 Building (uv build)...${NC}"
rm -rf dist
uv build
if [ ! -d dist ] || [ -z "$(ls -A dist)" ]; then
    echo -e "${RED}❌ Build failed — dist/ is empty.${NC}"
    exit 1
fi
echo -e "${BLUE}🔎 twine check...${NC}"
uv run twine check dist/*
echo -e "${GREEN}✅ Built + checked:${NC}"
ls -1 dist
echo ""

# Validate token
echo -e "${BLUE}🔐 Validating PyPI token...${NC}"
if [ -z "$PYPI_TOKEN" ]; then
    echo -e "${RED}❌ PYPI_TOKEN not found in .env${NC}"
    echo "Add:  PYPI_TOKEN=pypi-your-token-here"
    exit 1
fi
if [[ ! "$PYPI_TOKEN" =~ ^pypi- ]]; then
    echo -e "${RED}❌ PYPI_TOKEN should start with 'pypi-'${NC}"
    exit 1
fi
echo -e "${GREEN}✅ PYPI_TOKEN present (${#PYPI_TOKEN} chars)${NC}"
echo ""

# Confirm
read -r -p "Publish ${package_name} v${package_version} to PRODUCTION PyPI? (y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cancelled — nothing uploaded.${NC}"
    exit 0
fi

# Upload
echo -e "${GREEN}📤 Uploading to PyPI...${NC}"
if uv run twine upload dist/* --username __token__ --password "$PYPI_TOKEN" --verbose; then
    echo -e "${GREEN}✅ Published!${NC}"
    echo "  https://pypi.org/project/${package_name}/${package_version}/"
    echo "  Install:  pip install ${package_name}   (or)   uv add ${package_name}"
    echo -e "${BLUE}💡 Tag the release:${NC} git tag v${package_version} && git push origin v${package_version}"
else
    echo -e "${RED}❌ Upload failed.${NC}"
    echo "Common causes:"
    echo "  • 403 Forbidden — the token is not authorized for '${package_name}'. A"
    echo "    tvkit-project-scoped token cannot upload a new project; create an"
    echo "    ACCOUNT-scoped token at https://pypi.org/manage/account/token/ and retry."
    echo "  • File already exists — bump the version (a version can't be re-uploaded)."
    echo "  • Network / bad token — check PYPI_TOKEN in .env."
    exit 1
fi
