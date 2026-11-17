# Vision

> Source (Turkish): [`docs/vision.md`](../docs/vision.md), [`docs/design/framework.md`](../docs/design/framework.md)

**One sentence.** A merchant RPG and strategy game set in the 16th-century Mediterranean. You start as a merchant without even a ship, and try to survive, profit and grow in a harsh, living trade ecosystem.

## What it is not
- **Not a tycoon or city builder.** The player does not lay out factories; they deal with people, risk and information.
- **Not a war game.** Conflict matters a great deal, but the player affects it only indirectly: avoidance, security, insurance, flags, bribes.

## The experience
- **Start:** limited capital, some reputation, no ship. The intended starting point is Venice, around 1560.
- **Early options:** buy cargo space or a freight share on someone else's voyage (the ship can sink), low-risk bonds, a share in a caravan, deals with local merchants and producers.
- **Growth:** a shop, a ship (first a share, then all of it), caravans, agents (*fattori*); later, port facilities and legal entities.
- **Scaling:** the player manages people, not buildings. Agents pursue their own interests, are partly rational and carry risk.

## The world
- It starts at a historical moment, built as it was then. Historical events happen regardless; the player's influence is limited (prices, the development of some routes).
- The ecosystem is full of merchants large and small, guilds, caravans, corsairs, insurers and bankers. **All of them follow the same rules as the player**, with different starting conditions and goals.
- Prices come entirely from dynamic markets, which the player also moves.
- Time flows continuously, EU4-style: the player sets the speed, pauses, reads and thinks. The game spans one lifetime; it may continue through an heir or a company.

## Principles (from the framework)
| | Principle |
|---|---|
| P1 | Merchant RPG + strategy; not a tycoon. |
| P2 | The player is an ordinary agent in the economy; NPCs follow the same rules. |
| P3 | **Living ecosystem simulation first, game second.** |
| P4 | The simulation is deterministic (seeded). |
| P5 | **Information travels physically and goes stale; this is the heart of the design.** |
| P6 | Readability is a design goal; an over-volatile economy is tiring. |
| P7 | "How does the player experience this?": a mechanic nobody can feel is removed. |
| P10 | **Opportunities come from frictions, not NPC stupidity** ([experiment 01](experiments/01-instant-information.md)). |
| P11 | **Real economic phenomena should show up in the game.** Pork cycles, cobwebs, herding, bubbles and survivorship bias are wanted features, not bugs. Only artifacts are fixed. |
| P12 | **Behaviour must emerge, not be tuned from above.** Each parameter is tied to a historical or empirical value, comes from the model's own data, or is replaced by a physical or institutional mechanism. Temporary proxies are flagged. |

Return frame: a bond yields about 4%, a near-riskless floor. Ordinary trade earns bond + risk premium. Good trading earns more, bad trading less, and nobody makes 50% a year. This is not enforced; it emerges from free entry tied to the bond rate ([experiment 03](experiments/03-entry-speed.md)).

## Roadmap
1. Living ecosystem simulation, headless. **This comes first.** (Current stage.)
2. Text-based play.
3. Visual, map-based playable version.
4. Possibly multiplayer.
