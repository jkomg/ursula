# Getting started with Ursula in ChatGPT or Codex

Ursula helps you plan your week, spot blockers and prepare an update for your manager.
It brings together meeting notes, your calendar and Jira work, then proposes what
needs attention. You decide which changes to make.

You do not need to write code or edit configuration files. Setup is a conversation.
This guide is for managers and other staff using **Windows or Mac**. The exact
installation steps depend on the app your organisation provides; your technical
contact can help with that part.

## Before you start

Ask the person supporting Ursula for the **ChatGPT/OpenAI version** of the installation
package. The Claude version has a different setup. Both versions follow the same
weekly process and look for the same kinds of problems.

You will also need access to the work sources Ursula reads:

| Work source | Why Ursula needs it |
|---|---|
| Jira | Check existing work, avoid duplicate tickets and identify blockers |
| Google Drive | Read meeting notes and other work documents |
| Gmail | Find commitments made over email |
| Calendar | Understand your week and identify meetings without notes |
| Slack | Find requests and commitments outside meetings; read only |

Connecting these services is separate from installing Ursula. Your organisation may
need to approve access. Ursula will check what it can actually read during setup and
tell you if anything is missing.

## Get Ursula ready

Your technical contact can install Ursula for you or walk you through the process.
You should not need to open a terminal or run commands.

- **Mac:** if you are asked to unpack the installation package, double-click the zip file.
- **Windows:** if you are asked to unpack it, right-click the zip file and choose **Extract All**.

Only unpack the package if your installation instructions ask you to. Some installers
accept the zip directly. Unpacking a file does not, by itself, install Ursula.

Ursula can be used through a supported ChatGPT desktop installation or Codex. For
ChatGPT in a web browser or on a phone, your organisation will need to provide a
plugin that includes Ursula; the zip produced by this repository is not that plugin.
If installation is unavailable, your technical contact can help you provide the
instructions and supporting files in a chat for a manual review.

Once Ursula is available, open a new chat and say:

> Set up Ursula in dry-run. Explain each step in plain language.

If the app does not recognise Ursula, select it from the app's skill picker first.
In ChatGPT, look for it using `@`; in Codex, use `$ursula`.

## What setup will ask you

Have these answers ready; it is fine to ask for help finding them:

- Where your own work is tracked in Jira, and which other teams or people you follow.
- Who receives your weekly update, when they need it and which sections or numbers they want.
- When you plan your week and review what happened.
- The names of people you work with and any policies Ursula should consider.

Ursula will check access to your work sources, confirm the answers with you and show
you an initial board or written review. It should explain any checks it could not
complete rather than saying everything is ready.

If Jira is unavailable, Ursula cannot reliably check for existing tickets. If other
sources are missing, you can ask for a limited review, but it should clearly say what
it could not check. Full setup remains unfinished until the required checks pass.

## Start with a preview of proposed changes

**Dry-run means Ursula reads your work and shows its proposals without applying them.**
It does not change Jira or your calendar. It does keep a record of what it found,
so your board or written review shows the problems it spotted, and setup saves your
preferences so you do not have to repeat the interview.

Stay in dry-run for two full planning-and-review cycles. Read the proposals, correct
anything it misunderstood and reject suggestions that do not fit your priorities.
Only move to live use when the proposals consistently look right.

In live use, Ursula asks you to approve proposed changes. Calendar invitations and
changes that affect other people need separate approval. Ursula never sends email
or posts, drafts or reacts in Slack.

## Keep your setup between conversations

Ursula needs a reliable record of your preferences and previous reviews. Ask it to
explain where that record will be kept:

- **A private folder:** where the app has file access, your technical contact can help
  choose a suitable location on your Windows or Mac computer.
- **A saved handover file:** otherwise, Ursula can provide a file for you to keep and
  supply at the start of the next conversation. Save it somewhere approved for work data.

Do not assume a new chat remembers everything. If Ursula asks for your handover file,
provide the latest copy before starting. If you cannot provide it, ask for a limited
read-only review; Ursula should not create tickets or claim the full weekly process
is complete.

Moving from Claude does not automatically transfer your setup or review history.
Your technical contact can help you make that transition.

## Your board

The ChatGPT/Codex version provides a **dated snapshot** of your work, findings and
meeting-note gaps, including suggested agendas for one-to-ones where relevant.
It may be a browser-readable file or a written review in the chat.

The snapshot shows what Ursula observed at the time shown on it. It does not refresh
itself when Jira changes, and it has no buttons that update Jira. Ask Ursula for a
fresh review when you need current information. The Claude version has a separate
live board.

Keep the board and any handover files private or share them only through approved
work channels. They contain information about your work and colleagues.

## For the person supporting installation

Build packages and technical instructions are in `docs/release.md`. Storage and
connector details are in `reference/runtime.md`; the shared setup checks are in
`docs/setup.md`. For OpenAI installation, use the OpenAI bundle and verify that the
chosen app supports the installation method on the user's operating system.

The portable board helper is `scripts/render_snapshot.py`. It requires Python 3;
ordinary users do not need to run it themselves. Provide a board file or written
review they can open without development tools.

Official skill installation and discovery guidance:
[Build skills](https://learn.chatgpt.com/docs/build-skills).
