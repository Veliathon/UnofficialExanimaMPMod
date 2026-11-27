# UEMM 0.6.8
Released 2026-11-27

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

## New in 0.6.8
- Hits on a friend, or on an enemy that is fighting someone else, now land with their full weight: the body moves as it should, a stumble plays out, and a killing blow throws the enemy the way it was hit. Before, those hits felt weak.
- Running into another player, or into an enemy that another player is fighting, now pushes them, with a weapon in hand or with empty hands. Before, it was like running into a wall.
- With three or more players, all of this also works between two players who both joined the host, and on an enemy that one of them is fighting. Before, those hits and shoves were not passed on.
- A plank or other object someone has just put down is now solid for everyone almost at once, also when a player is standing right next to it. Before, it could stay like a ghost for up to five seconds, and a friend stepping onto it could fall through.
- During a world transfer the players panel now says the world is being sent or received. Before, it showed a misleading, very high ping figure that looked like a broken connection.
- Everyone in a session needs this version: it cannot play together with the previous one, so update together.

## Known issues
Not fixed yet:
- Choosing a character on a very slow connection can leave the joining player without control.
- Going to the main menu in the middle of a level change is not handled yet.

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
