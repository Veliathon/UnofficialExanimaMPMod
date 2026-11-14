# UEMM 0.6.5
Released 2026-11-14

> [!CAUTION]
> **WARNING: EXPERIMENTAL SOFTWARE, WRITTEN BY AI**
>
> This mod's code was written by AI. Nobody can easily audit the whole code base, so its full behaviour, and what it might do to your PC, cannot be reviewed in total. The developer did ask AI to review it for safety, but that is AI checking its own work: not a real safety net. The mod runs inside the game and changes it while it plays. Use it entirely at your own risk. If you are not comfortable with that, do not download it and do not run it.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
>
> See LICENSE.txt sections 9 and 10.

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

## New in 0.6.5
- Fights no longer make the ping climb, and the joining player sees the action on time.
- Joining a game is much quicker.
- Everyone should update. The host must: the fix is on the side that sends.

## Known issues
Connection:
- On a slow host upload, far-away characters and objects move less smoothly, and joining takes longer. The player with
  the best upload should host.
- On a slow host upload, a friend joining can briefly make the game stutter for the players already in.

Combat:
- Under lag, a parry can look different on each screen. The block still counts.
- Hits on shields can do a few percent more or less damage than in single player.
- In busy fights, a hit can now and then look less natural than in single player. An enemy hit in a friend's fight
  can sink lower than it should.
- Now and then, an enemy that turns from one player to another pauses for a moment.
- Tested less: large fights (several players against several enemies), and companions with several players.

Objects and items:
- After a rejoin, some loose objects can sit at a slightly different angle. They're in the right place.
- Now and then an object a friend moved earlier shows in a slightly different spot on their screen.
- Rarely, a loose object, a dropped item or a carried bag shows differently on another player's screen: it jumps, is
  flung, or shows twice. The items inside agree. Tell us if one goes missing or doubles.
- Using objects as tools, like wedging a lever or a door with a pot, is tested less.

Other:
- A late joiner may see someone's clothing colours or weapon quality differently.
- A disconnected friend's character stays in the world.
- Enemies in an empty room can now and then fight each other.
- The F1 players list sometimes doesn't open on a friend's PC.
- A few rare crashes seen in testing could not be repeated. Keep a checkpoint.

Limits of this release:
- Steam only. Hosting and joining by address (Manual in the launcher, shown as DISABLED) come later.
- No Arena in co-op.
- POSSESS takes a free character of the party. Never one another player is using, and never the game's own
  characters.
- Everyone needs the same mod version and the supported game version. A game update stops the mod until it's updated.
- If the host's game closes or crashes, the session ends for everyone.
- The host trusts the players it lets in. No cheat protection: play with people you know.
- Ping matters: Exanima's combat is physics-driven. The F1 ping colours are provisional, measured on a local network,
  not a guarantee.
- Windows only.
