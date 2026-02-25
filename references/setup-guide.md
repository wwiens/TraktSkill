# Getting Started with trakt-cli

trakt-cli is a command-line tool for browsing Trakt.tv — find trending shows, search for movies, check what's airing this week, and more. There are two tiers: **public browsing** (just an API key) and **personal features** like your watch history and watchlist (requires logging in). This guide covers both.

---

## What you'll need

- **Python 3.9 or newer** — run `python3 --version` to check
- **A Trakt.tv account** (free) — you need one to get an API key, even for public browsing
- An internet connection

> **Note:** Commands like `trakt trending` and `trakt movies search` work with just an API key. Commands that touch your personal data (history, watchlist, ratings) also need a login, which is covered in the optional [Step 6](#step-6--log-in-for-personal-features-optional).

---

## Step 1 — Create a Trakt account

Go to **https://trakt.tv/auth/join** and sign up for a free account.

If you already have a Trakt account, skip to Step 2.

---

## Step 2 — Register an API application

This is the step that surprises most new users: to use any Trakt API client (including this one), you register a small "application" on Trakt's website. This gives you a personal API key that identifies your requests.

1. Log in to Trakt, then go to **https://trakt.tv/oauth/applications/new**
   *(or navigate there manually: Settings → Your API Apps → New Application)*

2. Fill in the form:

   | Field | What to enter |
   |---|---|
   | **Name** | Anything you like — e.g. `My Trakt CLI` |
   | **Redirect URI** | `urn:ietf:wg:oauth:2.0:oob` (copy-paste exactly) |
   | **Description** | Optional — leave it blank if you like |
   | Everything else | Leave as-is |

   > The Redirect URI value `urn:ietf:wg:oauth:2.0:oob` is the standard placeholder for apps (like CLIs) that can't open a browser window to receive a callback. Copy it exactly.

3. Click **Save**. You'll land on the detail page for your new application.

4. On that page, find and copy two values — you'll need them in the next steps:
   - **Client ID** — a 64-character hex string; this is your API key for all public commands
   - **Client Secret** — another 64-character hex string; only needed if you want to log in (Step 6)

---

## Step 3 — Install trakt-cli

From the root of this repository, run:

```bash
pip install -e .
```

pip will automatically install the three dependencies (`click`, `httpx`, and `rich`).

**If pip warns about a PATH issue** — something like *"The script trakt is installed in '/Users/yourname/Library/Python/3.x/bin' which is not on PATH"* — run this to fix it for your current terminal session:

```bash
export PATH="$HOME/Library/Python/3.$(python3 -c 'import sys; print(sys.version_info.minor)')/bin:$PATH"
```

To make this permanent, add the same line to your `~/.zshrc` (or `~/.bash_profile`).

> **Windows users:** pip will print the exact folder to add to your PATH — it looks different but the same principle applies.

Verify the install worked:

```bash
trakt --help
```

---

## Step 4 — Add your API key

Paste your **Client ID** from Step 2 into this command:

```bash
trakt config set-key YOUR_CLIENT_ID
```

This saves the key to `~/.config/trakt-cli/config.ini` so you never have to type it again.

> **Power users:** you can also set the environment variable `export TRAKT_API_KEY=YOUR_CLIENT_ID` instead — the CLI checks that first.

---

## Step 5 — Try it out

With your API key saved, these commands work immediately — no login required:

```bash
trakt trending
```
Lists TV shows that are trending right now (most active watchers in the last 24 hours).

```bash
trakt movies search inception
```
Searches for movies matching "inception" and shows the top results.

```bash
trakt calendar shows
```
Shows all episodes airing in the next 7 days.

If you see results in your terminal, you're all set for public browsing.

---

## Step 6 — Log in for personal features *(optional)*

This step is only needed if you want to access your own Trakt data: watch history, watchlist, ratings, recommendations, checkin, and sync.

### 6a. Save your Client Secret

Paste your **Client Secret** from Step 2:

```bash
trakt config set-secret YOUR_CLIENT_SECRET
```

### 6b. Log in

```bash
trakt auth login
```

The CLI will print something like:

```
Open: https://trakt.tv/activate
Enter code: ABCD-1234
Waiting for authorization...
```

Here's what to do:

1. Open **https://trakt.tv/activate** in your browser
2. Type in the short code shown in your terminal (e.g. `ABCD-1234`) and approve it
3. Switch back to your terminal — it's printing dots while it waits for you
4. Once you approve, it prints: `Logged in successfully.`

### 6c. Verify the login

```bash
trakt auth status
```

You should see something like: `Logged in. Token expires 2026-05-01 12:34 UTC.`

### 6d. Try a personal command

```bash
trakt sync history
```

This shows your recent watch history pulled from Trakt.

---

## Staying logged in

- **Tokens refresh automatically** — when your token is close to expiring, the CLI refreshes it in the background. You don't need to do anything.
- **If you ever get logged out:** just run `trakt auth login` again.
- **To log out:** run `trakt auth logout` — this clears the stored token.

---

## What next?

See **[README.md](README.md)** for the full command reference: every command, all options, and examples.

Quick reminder: `trakt --help` lists all top-level commands, and `trakt <command> --help` shows the options for any specific command:

```bash
trakt --help
trakt movies --help
trakt sync --help
```
