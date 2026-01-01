#!/bin/bash
# Setup multi-remote hot availability for AutoEQ
set -e

echo "=============================================="
echo "AutoEQ Multi-Remote Setup"
echo "=============================================="

# GitHub
echo "[1/4] Setting up GitHub remote..."
if git remote | grep -q "github"; then
    echo "  GitHub remote already exists"
else
    git remote add github git@github.com:VitaNova/autoeq.git 2>/dev/null || \
    git remote add github https://github.com/VitaNova/autoeq.git
    echo "  GitHub remote added"
fi

# Gitea
echo "[2/4] Setting up Gitea remote..."
if git remote | grep -q "gitea"; then
    echo "  Gitea remote already exists"
else
    git remote add gitea git@gitea.vitainfra.com:vitanova/autoeq.git 2>/dev/null || \
    git remote add gitea https://gitea.vitainfra.com/vitanova/autoeq.git
    echo "  Gitea remote added"
fi

# ex63
echo "[3/4] Setting up ex63 remote..."
if git remote | grep -q "ex63"; then
    echo "  ex63 remote already exists"
else
    git remote add ex63 ex63:/root/autoeq 2>/dev/null || true
    echo "  ex63 remote added"
fi

# Rename origin if needed
echo "[4/4] Verifying origin..."
if ! git remote | grep -q "origin"; then
    echo "  No origin set - setting to local path"
fi

echo ""
echo "Configured remotes:"
git remote -v

echo ""
echo "Push to all remotes with:"
echo "  git push origin main && git push github main && git push gitea main"
