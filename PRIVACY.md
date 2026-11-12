# Privacy: Unofficial Exanima Multiplayer Mod

Unofficial Exanima Multiplayer Mod by Veliathon. Not affiliated with or endorsed by Bare Mettle Entertainment.
Requires your own legitimate copy of Exanima.

**Read the warning first.** This mod is experimental software, written by AI. Use it entirely at your own risk: see the warning at the top of the README.

This note explains what information the mod uses, where it goes, and who can see it. The mod has no account, no
analytics and no server of its own.

## On your PC

- **Settings.** The launcher keeps your settings (your player name and your choices) in
  `%APPDATA%\ExanimaCoop\launcher.json`.
- **Co-op saves.** Co-op games are saved in `%APPDATA%\ExanimaCoop`. When you host, your save also holds your
  friends' co-op characters and the names they play under.
- **Logs.** The mod writes logs of your co-op sessions in `%APPDATA%\ExanimaCoop`. With **Detailed logs** ticked,
  they hold more detail. After a crash, the mod may also write crash files there (`crash-*.txt`, and a `.dmp` memory
  snapshot of the game that can contain anything the game had in memory).
- These files stay on your PC. Delete `%APPDATA%\ExanimaCoop` to remove them (this also removes your co-op saves).

## Version check

- The launcher asks GitHub once at start whether a newer version exists (you can turn this off). Nothing else is
  sent. The tick is in the launcher's **What's new** panel: **Check GitHub for new versions**. GitHub sees your IP
  address for that one request, under its own privacy policy.

## Bug reports

- The launcher's bug report gathers the technical details for you. Nothing is uploaded: you choose whether and where
  to paste it. **Report on GitHub** copies it and opens the mod's issue form; **Post on Discord** copies it and
  opens the Discord, for the **#bug-reports** forum. Only the mod and game versions go in the form's web address.
- The report excludes names, Steam IDs, IP addresses, passwords and file paths. What you write in the form or the
  post is your own and may contain personal information. Read the report before sharing it.
- Raw logs and crash files hold more than the report. Send them only if we ask, and only privately (a direct message
  on the Discord), never in a public channel.

## Playing together

- **Your player name** is shown to everyone in the session.
- **Hosting or joining through Steam** (the only way to connect in this release). The game's own Steam connection
  is used, under Steam's terms. Your Steam
  identity (your Steam name and profile) is visible to the players in the session. Hosting opens a Steam lobby
  that your Steam friends can see (nobody, under **Invite only**); it holds your player name, your Steam ID, the mod
  version, the number of players and whether a password is set (never the password). Steam connects the players
  directly or through its relays: which one depends on each player's Steam setting for sharing IP addresses
  (by default Steam shares it only with Steam friends). Relayed players don't see each other's IP addresses.
- **Connection and performance figures.** Players in a session see each other's connection and performance figures
  (ping, step cost, bytes per second, memory use) in the F1 panel. They are not sent anywhere else and are kept only
  in your own log.

## Discord, GitHub and Steam

- **Discord** (help, news, bug reports) is run by Discord under its own terms and privacy policy. Everyone in a
  channel can read what you post there, together with your Discord name, and anyone can copy a public post.
- **GitHub** (the mod's page, bug reports) is run by GitHub under its own terms and privacy policy. Issues on the
  mod's page are public, together with your GitHub name.
- **Steam** is run by Valve under its own terms and privacy policy.

## Who sees reports, and for how long

- A GitHub issue can be read by everyone; what you post in the **#bug-reports** forum by everyone in that channel.
- Logs or files you send privately are read only by the developer (Veliathon) and used only to find and fix the
  problem.
- We keep reports and files only as long as they're needed to fix the bug. You can delete your own Discord posts at
  any time, or ask us to remove a report or a file you sent. We can't recall copies other people have already made of
  a public post.

## Contact

Questions, or a request to remove something: ask on the Discord (https://discord.gg/wDxgGsUmxJ), or send the
developer a direct message there.
