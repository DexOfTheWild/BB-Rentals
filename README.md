# BB-Rentals

Optional low-resolution game packaging artwork and recognition catalog for the
ACGC PC mod. Releases contain artwork and metadata only. Supply your own ROMs,
BIOS and base-game disc. This repository never downloads or redistributes them.

## Player setup

Use a main-game build supporting the launcher **Games** page, then choose
**Install / update BB-Rentals**. Place supported ROM files in the executable's
`roms/n64`, `roms/genesis`, `roms/snes`, `roms/psx` or `roms/famicom` folder.
Choose **Scan my ROMs**, or simply start the game. Python is not needed by players.

Exact SHA-256 matches pick up the authored art, names, prices, catalog and rental
policy. Filenames do not determine recognition. Unknown revisions retain generic
system packaging. N64 fingerprints include the three byte orders. PSX currently
recognizes the supplied CHD encoding; other CHD encodings can be added as hashes.

Catalog availability requires a readable player ROM and an implemented media
adapter. NES, N64, Genesis, SNES and PSX boxes use physical consoles. NES media
requires the main-game build with the standalone NES console adapter. Game Boy
still needs a media selector; its entries cannot auto-sell or rent. The migrated
Mega Man 2 box retains its legacy identity. Pokémon
is intentionally outside automatic discovery/catalog/rentals.

Rental eligibility feeds the game's rental pool. Bob's shelf checkout is a
separate unfinished feature; installing art does not enable that preview's checkout.
Game cores/BIOS and compatibility remain the main game's responsibility.

Manual library imports take precedence. Disabling this pack returns automatically
discovered games to generic boxes without removing owned items, ROMs or saves.

## Artwork pending

Super Smash Bros. (`bb.super-smash-bros`) and Tiny Toons (`bb.tiny-toons`)
are recognized using the supplied ROM fingerprints and temporarily use neutral
system boxes. Replace their assets in place when the custom artwork is ready;
keep the IDs unchanged. Both are catalog/rental eligible on the updated game
build; Tiny Toons uses the standalone NES console. Mega Man 2 and Battletoads
are also enabled for that console and the rental pool.

## Maintainers

`catalog.json` is the prepared manifest. Keep IDs stable. Its hashes are ROM
fingerprints, never ROM content. `assets/` contains the runtime OBJ, MTL and PNG
files. Add recognition hashes for verified revisions without bundling ROMs.

Run `python build_pack.py` to make `dist/BB-Rentals.zip` and its SHA-256 descriptor.
The builder rejects unexpected extensions and validates listed assets. Set the
catalog version, then push its matching `v...` tag to publish through the release
workflow. Releases have their own cadence, independent of the game executable.
Use **Install local ZIP** for unpublished builds.

Current art was generated/edited for this project. Extracted vanilla NES box
textures and original reference photographs are intentionally absent.
