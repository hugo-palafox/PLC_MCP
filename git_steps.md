# Git Quick Reference for PLC_MCP

This file summarizes common git workflows and copy-paste commands for:
- creating a new repo from an existing local project,
- cloning/pulling on another computer,
- pushing changes back to the remote, and
- switching between multiple computers.

---

## 1) Create a new GitHub repo from your local project

Run in VS Code terminal (PowerShell or Bash):

```powershell
git init
git config user.name "Your Name"
git config user.email "you@example.com"
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/hugo-palafox/PLC_MCP.git
git push -u origin main
```

If `origin` already exists and points to the wrong URL:

```powershell
git remote set-url origin https://github.com/hugo-palafox/PLC_MCP.git
git push -u origin main
```

---

## 2) Clone and set up on another computer

On the other computer (once only):

```bash
git clone https://github.com/hugo-palafox/PLC_MCP.git
cd PLC_MCP
```

Later, to update the local copy before you start working:

```bash
git fetch origin
git pull --rebase origin main
```

---

## 3) Make changes and push back to remote

Normal workflow:

```bash
# make edits
git add <files>
git commit -m "Short message describing change"
git push origin main
```

If remote has new commits, rebase first (recommended):

```bash
git fetch origin
git rebase origin/main
# resolve conflicts if any: edit files, git add <file>, git rebase --continue
git push origin main
```

If you truly intend to overwrite remote history (dangerous):

```bash
git push --force origin main
```

---

## 4) Switching between computers (recommended workflow)

1. On Computer A: commit and push frequently:

```bash
git add .
git commit -m "Work on feature X"
git push origin main
```

2. On Computer B before editing: pull/rebase latest:

```bash
git pull --rebase origin main
```

3. Repeat: edit on B, commit, push; back on A pull again.

---

## 5) Authentication options

- HTTPS: Git will prompt for username/password or Personal Access Token (PAT). On Windows, Git Credential Manager stores credentials.
- SSH (recommended for passwordless):

```bash
ssh-keygen -t ed25519 -C "you@example.com"
# copy ~/.ssh/id_ed25519.pub to GitHub -> Settings -> SSH keys
git clone git@github.com:hugo-palafox/PLC_MCP.git
```

To sign in via VS Code: Command Palette → "Git: Sign in to GitHub".

---

## 6) Useful commands

- `git status --porcelain --branch` — quick status + current branch
- `git remote -v` — show remotes
- `git branch --show-current` — current branch
- `git log --oneline --graph --decorate -n20` — recent commits graph
- `git remote set-url origin <url>` — change remote URL

---

If you want, I can: (A) add SSH setup steps tailored to your OS, (B) create a short PowerShell script to automate initial setup, or (C) open this file in the editor for further edits.

---

## 7) Understanding `git fetch` and `git rebase`

What `git fetch` does:
- Downloads commits, branches and tags from the remote into your local repository's remote-tracking branches (for example `origin/main`) without changing your working tree or current branch.
- Use it to inspect remote changes safely before integrating them.

Example:
```bash
git fetch origin
# now the remote's state is available as origin/main, origin/other-branch, etc.
```

What `git rebase` does:
- Replays your local commits on top of another branch's tip, producing a linear history where your commits appear "after" the target.
- It rewrites commit parents and therefore creates new commit SHAs for rebased commits.

Example (rebase current branch onto remote main):
```bash
git fetch origin
git rebase origin/main
```

Step-by-step workflow (recommended before pushing):
```bash
git fetch origin
git rebase origin/main   # or: git pull --rebase origin main
# resolve conflicts if any (see below)
git push origin main
```

Resolving conflicts during a rebase:
1. Git pauses and lists conflicted files.
2. Check status: `git status`
3. Edit conflicted files to resolve differences.
4. Stage resolved files: `git add <file>`
5. Continue the rebase: `git rebase --continue`
6. To abort and return to the pre-rebase state: `git rebase --abort`

Rebase vs Merge (brief):
- Rebase: produces a linear history (clean), rewrites commits. Good for local/private branches before pushing.
- Merge: preserves history and commit SHAs, creates a merge commit. Good when you want to keep merge history.

When not to rebase:
- Avoid rebasing commits that have already been pushed and shared with others unless all collaborators coordinate; rewriting shared history forces others to reconcile.

Pushing after a rebase:
- Because rebasing rewrites commits, pushing may require a force. Prefer safe force:
```bash
git push --force-with-lease origin main
```
`--force-with-lease` ensures you don't overwrite remote commits that you didn't base your work on.

Interactive rebase (edit/squash/reorder commits):
```bash
git fetch origin
git rebase -i origin/main
```
Follow the editor instructions to pick/squash/reword commits, then `git rebase --continue`.

Safety tips:
- Always fetch first and inspect `git log --oneline --graph origin/main..HEAD` to see what will be rebased.
- Use `--force-with-lease` over `--force` when pushing rewritten history.
- If unsure, make a local backup branch before rebasing: `git branch backup-before-rebase`

---

End of file.
