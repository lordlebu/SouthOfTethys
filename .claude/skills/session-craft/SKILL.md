---
name: session-craft
description: Environment gotchas and working practices for SouthOfTethys canon and its 4000BCESaraswathy game sibling. Read this early in any session here, and consult it whenever you are about to push or delete a branch, bump the index, re-export the bundle to the game, or touch both repositories in one sitting. Several items are hard refusals and cross-repo blind spots that look like a broken setup or a passing check when they are neither, so reading it first saves a round of wrong diagnosis.
---

# Working in canon

`CLAUDE.md` is the authority on what canon is and what the rules are. This is the complement: what
the *environment* does, and the failure modes that live between this repository and the game.

The game repo carries a fuller version of this skill covering rendering, art intake and verifying
that something actually draws. If both repos are attached, read that one too.

---

## The environment

### Branch deletion is blocked, and there is no route

`git push origin --delete` returns **HTTP 403**, one branch or thirty. So does the REST endpoint
`DELETE /repos/{owner}/{repo}/git/refs/heads/{branch}`:

```
Write access to this GitHub API path is not permitted through this proxy.
```

There is no `delete_branch` in the GitHub MCP set either. It is a platform limit on Claude Code
sessions, not a repository permission — **do not try all three routes**. Scan, hand over a
ready-to-paste command with the names inlined, and note that GitHub's branches page can do it and
offers restore afterwards.

Before blaming GitHub for a network refusal, read `curl -sS "$HTTPS_PROXY/__agentproxy/status"`. An
empty `recentRelayFailures` means the refusal came from the far end.

### `gh` installs and is half useless

`apt-get install -y gh` works and picks up the environment's `GH_TOKEN` with no login. Then most of
it fails: **GraphQL is blocked for Claude Code sessions**, and `gh pr list`, `gh pr checks`,
`gh pr status`, `gh issue list` and `gh repo view` are all GraphQL. Only `gh api` REST routes,
`gh pr view --json` and `gh run list` work. The `mcp__github__*` tools already cover everything, so
reach for those.

---

## The cross-repo seam

### The version split has a blind spot, and it has caught us

The game's `npm run check:data` compares its bundle against **its own lock**, not against canon. So
the two repositories can disagree about what an entity is called while every check on both sides
stays green.

That happened: a pull request merged only the first of two commits on its branch, leaving `main`
here with `poi_stacked_temple` while the game had already shipped a bundle built from
`poi_alms_step`. Nothing failed.

**`check_export_boundary.py` is the check that sees it**, because it reports `game bundle: matches`
by comparing against the sibling checkout. Run all three gates, not two, whenever both repos have
been touched in one session:

```bash
python utils/lint_story.py && python utils/check_playability.py && python utils/check_export_boundary.py
```

### Bumping the index has a tail

`update_index.py --bump minor` changes the version and counts, and then the lint **refuses the
commit** until `README.md` and `CLAUDE.md` carry the same numbers. That is deliberate and it caught
the same mistake twice in one session. Expect the sequence:

1. `python utils/update_index.py --bump minor`
2. fix the version line in `README.md` *and* `CLAUDE.md` — they are worded differently, so a single
   `sed` will usually miss one
3. `python utils/check_export_boundary.py --update` — a version bump changes all five bundle files
4. `python utils/export_canon_bundle.py --apply` to carry it to the game
5. all three gates

### A pull request can merge while you are working

It happened three times in one session across the two repos. Fetch before committing:

```bash
git fetch origin main && git log --oneline -1 origin/main
```

After a merge, restart the branch from the new base rather than stacking on the old tip, and
**before any force-push run `git cherry origin/<branch> HEAD`** — a `-` means that commit's patch is
already present under a different sha and nothing is lost, a `+` means it is not. That is also how
to tell a genuinely unmerged branch from one whose content already landed when triaging what is
safe to delete.

### The push gate needs `/hooks` opened once

`.claude/hooks/push-gate.sh` refuses a push onto a branch whose pull request has already merged. It
is committed here and it works, but Claude Code's settings watcher only watches directories that
had a settings file when the session *started* — so in the session that created it, it never fires.
By hand it still answers correctly:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git push"}}' | .claude/hooks/push-gate.sh
```

---

## Authoring

### Read the art before writing the prose about it

Canon describes places the game draws. A point of interest was authored as a temple built in four
stacked courses of four materials; the painted sheet was a single-period domed temple on one high
plinth, and the recommendation that followed — regenerate the art — was **written without opening
the file**. Looking took ten seconds and reversed it.

The `Read` tool renders images. If canon is about to describe something that already has art, open
the art first. Where they disagree and the art is good, the prose moves.

### Check the spelling against canon before inventing a people

A backstory arrived naming the *Jhawara*. Canon already carried those people as **Jharwa**, in
`mythology_chess_of_fate`, `character_jharwa_elder_repa` and the massacre itself. Using the new
spelling would have created a second people who are the same people. Grep before authoring a proper
noun that sounds like it might already exist.

### An edge must be stated from both ends

`AUTHORING.md` says it and it is easy to miss: only `successors` is read when the timeline is
drawn, so an edge declared on one side exists in canon and never appears in the picture.
