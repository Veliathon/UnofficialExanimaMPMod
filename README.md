> [!CAUTION]
> **WARNING: EXPERIMENTAL SOFTWARE, WRITTEN BY AI**
>
> This mod's code was written by AI. Nobody can easily audit the whole code base, so its full behaviour, and what it might do to your PC, cannot be reviewed in total. The developer did ask AI to review it for safety, but that is AI checking its own work: not a real safety net. The mod runs inside the game and changes it while it plays. Use it entirely at your own risk. If you are not comfortable with that, do not download it and do not run it.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
>
> See LICENSE.txt sections 9 and 10.

# Unofficial Exanima Multiplayer Mod 0.6.5

Play Exanima together online. One player hosts; up to three friends join from their own PCs, each with their own
character.

Unofficial Exanima Multiplayer Mod by Veliathon. Not affiliated with or endorsed by Bare Mettle Entertainment.
Requires your own legitimate copy of Exanima. Exanima is a trademark of its owner.

## Please read: a note for players
This is an unofficial, fan-made multiplayer mod. What you are about to play is an altered version of Exanima, not
the game as its developer made it, so it does not represent the original game. Issues you run into may come from
the mod rather than the game.

Exanima is a carefully crafted single-player game. Ideally, play this mod only once you have properly enjoyed the
original on its own: it is the best way to see the care and detail its developer put in, and then to enjoy it
together with friends.

While the mod is installed or was in use:
- please do not contact Bare Mettle Entertainment about any problem;
- please do not post bugs or issues on the official Exanima forums, Steam discussions or Bare Mettle's channels;
- report everything to us instead: click the bug icon in the launcher (GitHub Issues or our Discord).

The "UEMM" mark in the corner of the screen and the line under the menu logo show that the mod is running. Please
leave them visible in screenshots and videos, so nobody mistakes the mod for the original game.

## Contents
- [Read this first](#read-this-first)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Hosting a game](#hosting-a-game)
- [Joining a game](#joining-a-game)
- [Networking](#networking)
- [Saves](#saves)
- [Privacy](#privacy)
- [Troubleshooting](#troubleshooting)
- [Known issues and limitations](#known-issues-and-limitations)
- [Uninstalling](#uninstalling)
- [Support and bug reports](#support-and-bug-reports)
- [Licence](#licence)

## Read this first
- 0.6.5 is an early release. It's in decent shape, but not finished.
- Expect bugs, known and unknown. Some can end a session.
- Keep a checkpoint, and back up your saves (see [Saves](#saves)).
- Play it and tell us what breaks. Every report helps the next version. The known issues are in the release notes
  on the Releases page.

## Features
- **Four-player co-op.** Bring up to three friends over Steam. No port forwarding.
- **Your own character.** Join from the main menu. Make someone new, or pick up where you left off.
- **Combat that holds up.** Hits, blocks and shoves land the way they should, on enemies and on each other.
- **Friendly fire.** Clip a friend mid-fight and they'll feel it.
- **Travel as a party.** Exits wait for everyone. You arrive together.
- **Shared chests.** One looter at a time, and nothing goes missing.
- **One world.** Doors, levers and pressure plates work for everyone.
- **Magic for all.** Everyone casts, and a Bolt flies true on every screen.
- **Drop in, drop out.** Leave, come back, take your character back.
- **Progress that sticks.** Skills and gear stay in the host's save. Co-op saves live apart from your own.
- **The F1 panel.** Who's here, their ping, the join code.
- **A launcher that just works.** Finds your game, installs in one click, checks versions, and writes your bug reports.

## Requirements
Every player needs:
- Windows 10 or 11 (64-bit).
- Exanima on Steam, game version **V 0.9.5.2g** (Steam build 25803178).
- Steam running and online.
- This mod, the same version for everyone (0.6.5).

**The host needs a good upload.** The host sends the game to every friend. For smooth fights, plan on about 2 Mbit/s of upload per friend (about 6 Mbit/s for three friends). The player with the best upload should host; you can test yours at any speed-test site.

Nothing else to install: everything the mod uses is in the download.

## Installation
1. Back up your saves (see [Saves](#saves)). Download `UEMM-0.6.5.zip` from the Releases page.
2. Unzip it into its own folder, for example in your Documents. Keep the files together.
3. Start **Exanima Co-op.exe**.
4. The first time, read the licence and choose **I agree**.
5. The launcher finds your Steam copy of Exanima and checks its version. Click **Install** to add the mod to it (your
   game itself stays as it is).
6. In the launcher, keep the **Steam** tab (at the top of the launcher) and choose **Host** or **Join**: see
   [Hosting a game](#hosting-a-game) and [Joining a game](#joining-a-game).

The launcher only adds the mod's files to the game folder; the game itself stays as it is. To play without the mod,
start Exanima from Steam as usual.

### "Windows protected your PC"
The mod isn't code-signed yet, so SmartScreen may show this the first time. If you have the exact official release,
choose **More info**, then **Run anyway**.

### Smart App Control
Smart App Control can block programs that aren't code-signed, and can briefly block the game when the launcher
starts it. Wait a minute and try again. If it keeps blocking the launcher, tell us on the Discord. Please don't turn
off Smart App Control or other Windows security for the mod.

### Antivirus warnings
The mod's loader and in-memory game changes can trigger antivirus warnings. A warning may be a false positive, but
don't assume every flagged download is safe. Check you have the exact official release, and report the file,
version and detection name so we can look into it. Do not disable your antivirus.

## Hosting a game
This release connects through **Steam** only: no port forwarding. At the top of the launcher, its **Steam** tab is
chosen; the **Manual** tab (by address) shows **DISABLED** and comes in a later release.

0. Pick the player with the best upload as host.
1. Start the launcher, type your name, and on its **Steam** tab choose **Host**.
2. Pick the maximum number of players (you plus up to three friends).
3. Under **Who can join**:
   - **Invite only** (the default): only friends you invite. A join code alone isn't enough.
   - **Friends**: any Steam friend, with Join Game in Steam or your join code.
4. Press **Start hosting**. The game opens at its main menu.
5. The **players panel** on the right shows who has joined, their ping and your **join code** (click to copy).
   **F1** hides or shows it. Invite friends from the panel (each friend installs the mod first: see
   [Joining a game](#joining-a-game)).
6. When everyone's in, choose **BEGIN** for a new game or **CONTINUE** for a co-op game.

You can switch between Friends and Invite only while you play, from the F1 panel. New characters join new games
only, on the first level. On a continued save, friends take a free character of the party with POSSESS.

## Joining a game
Before you can join, install the mod on your own PC: download the zip, start **Exanima Co-op.exe** and click
**Install** (see [Installation](#installation)). Every player needs the same mod version. Without the mod installed, an
invite just opens normal Exanima.

The host must have you on their Steam friends list (or, under Invite only, have invited you). Any of these works:
- Accept the host's Steam invite.
- In your Steam friends list, right-click the host and choose **Join Game**.
- In the launcher, on the **Steam** tab, choose **Join**, paste the host's join code and press **Connect**.

If your game is closed, Steam opens the launcher with the host filled in: press **Connect**. If a co-op game is
already running, the game shows the invite: press **Insert**, exit that game, then press **Connect** in the launcher.

Your game opens at its main menu and joins the host there. It says **WAITING FOR THE HOST** until the host begins or
continues. Then **CREATE** makes a new character (new games only; the line above shows the free slots), and
**POSSESS** takes a free character of the party: one you made before, or one a friend left behind. Nobody can take a
character another player is using.

## Networking
Steam connects the players, through its relay when needed. No ports to open, no router changes. Everyone needs Steam
running and online.

If Windows asks whether to allow Exanima through the firewall, choose **Allow** (at least Private networks).

## Saves
The mod is designed to keep co-op saves separate from single-player saves. Back up your saves before installing or
updating, and keep a backup while you test this release.

- Co-op games: `%APPDATA%\ExanimaCoop`. Single-player games: `%APPDATA%\Exanima`. (Win+R, paste the path.)
- To back up: close the game and copy both folders somewhere safe.

## Privacy
- **On your PC.** Launcher settings, co-op saves, logs and crash files stay in `%APPDATA%\ExanimaCoop`. As host,
  your save also holds your friends' co-op characters.
- **Version check.** The launcher asks GitHub once at start whether a newer version exists (you can turn this off).
  Nothing else is sent. GitHub sees your IP address for that one request.
- **Bug reports.** The report is a text; it isn't uploaded, and you choose whether and where to paste it. It holds
  technical details of your latest session only (versions, host or client, connection type, ping, performance,
  counts of problems) and no names, Steam IDs, IP addresses, passwords or file paths. Only the mod and game versions
  go into the GitHub form's web address. What you write in the form or post is public. Read the report before you
  share it. Send logs or crash files only if asked, and only privately.
- **Through Steam.** Hosting opens a Steam lobby only your Steam friends can see (or nobody, under Invite only). It
  holds your player name, your Steam ID, the mod version and the player count. Players in a session see each other's
  Steam identity. Steam connects players directly or through its relays, depending on each player's Steam setting
  for sharing IP addresses (by default only with friends); relayed players don't see each other's IP addresses.
- **In a session.** Players see each other's connection and performance figures (ping, step cost, bytes per second,
  memory) in the F1 panel. They go nowhere else and are kept only in your own log.
- **Discord, GitHub and Steam** have their own terms and privacy policies. Discord posts are seen by everyone
  in the channel; GitHub issues by everyone. Bug reports are kept only as long as needed to fix the bug; ask on the
  Discord to have one removed.
- The full privacy note is `PRIVACY.md` in this folder (also on the mod's GitHub page).

## Troubleshooting
- **"Game version not supported."** Steam updated Exanima. The launcher explains how to get the supported version
  without touching your normal install. Watch the Discord for a mod update.
- **Smart App Control blocked it.** See [Smart App Control](#smart-app-control).
- **Friends can't join.** Check you're Steam friends (or, under Invite only, that you invited them), Steam is online
  on both PCs, and everyone has the same mod version. Blocked Exanima at the firewall prompt? Windows Security >
  Firewall & network protection > Allow an app through firewall, then tick Exanima.
- **"Version mismatch".** Everyone needs the same mod version and game version.
- **Slow for one player.** Close other demanding programs, and report it with the launcher's bug icon.
- **Something else.** Bug icon in the launcher, then **Report on GitHub**, or **Post on Discord** without a GitHub
  account (see [Support and bug reports](#support-and-bug-reports)).

## Known issues and limitations
The full list is in the release notes for 0.6.5, on the Releases page.

The main limits:
- Steam only. Hosting and joining by address come later.
- Under lag, a parry can look different on each screen. The block still counts.
- Hits on shields can do a few percent more or less damage than in single player.
- In busy fights, a hit can now and then look less natural than in single player.
- Now and then, an enemy that turns from one player to another pauses for a moment.
- No Arena in co-op.
- POSSESS takes a free character of the party. Never one another player is using, and never the game's own
  characters.
- If the host's game closes or crashes, the session ends for everyone.
- The host trusts the players it lets in. No cheat protection: play with people you know.
- Everyone needs the same mod version and the supported game version.
- Not code-signed yet (see [Installation](#installation)).
- Ping matters: Exanima's combat is physics-driven. The F1 ping colours are provisional, measured on a local network,
  not a guarantee. Ping is only the connection's delay, so co-op combat can differ from single player even at a low
  ping.

## Uninstalling
1. In the launcher, click **Uninstall**. It removes the mod's files from the game folder.
2. Delete the mod's folder.
3. To remove co-op saves, settings and logs too, delete `%APPDATA%\ExanimaCoop`.

## Support and bug reports
- Discord: https://discord.gg/wDxgGsUmxJ (news, questions in **#help**, ideas in **#i-would-like**, bugs in the
  **#bug-reports** forum). New there? Accept the rules in **#rules** first.
- Found a bug? Tick **Detailed logs (for bug reports)** if you can, then click the **bug icon** at the top right of
  the launcher: **Report on GitHub**, or **Post on Discord** without a GitHub account. The launcher gathers the
  details and copies them; say what happened and paste them. GitHub:
  https://github.com/Veliathon/UnofficialExanimaMPMod/issues (a free account). On Discord, search #bug-reports first:
  already there? React with a thumbs-up and reply.
- Tried it? Tell us if you liked it, and why, in **#rate-the-mod** on the Discord.

## Licence
Free to download and play, and curiosity is welcome: look inside to learn how it works, check its security, or make
your own mods work alongside it. The licence asks two things: don't use it as the base of a rival multiplayer mod
(including by having an AI rewrite or rename its code), and link to the official download instead of re-uploading
it. Want to build on it? Ask on the Discord. Full terms: `LICENSE.txt`. Third-party components and their licences:
`THIRD-PARTY-NOTICES.txt`.

Copyright (c) 2026 Veliathon. Unofficial Exanima Multiplayer Mod by Veliathon. Not affiliated with or endorsed by
Bare Mettle Entertainment. Requires your own legitimate copy of Exanima.
