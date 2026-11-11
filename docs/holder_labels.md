# Holder labels — RWA Flow Tracker

> **STATUS: SKIPPED (2026-11-11)** — top-holder addresses are generated
> below but labels were not researched. The table is kept as the template
> for completing this step later. Until then, treat all labels as
> `unknown` and do NOT claim "labelled holders" in CV/write-up materials.

Phase 2 deliverable. For each top holder (from `sql/04_top_holders.sql` /
`sql/08_where_activity_goes.sql`), record who it is and **where the label
came from**. If a label is a guess, mark it as a guess — rule 4 in
AGENTS.md.

Label categories: `exchange`, `issuer`, `custodian`, `fund`, `defi`,
`bridge`, `unknown`.

Sources to try, in order of effort:
1. **Etherscan** — address page often shows a name tag; free, no key needed
   for the website (API needs a key).
2. **Arkham** — free tier, good exchange/institution labels.
3. **Nansen** — free tier; labels are part of what the JD asks about, so
   prefer it where it has coverage and note "Nansen" as the source.
4. **Manual** — project docs, official announcements, on-chain role
   (e.g. the contract IS the token's own minter → label `issuer`).

| Asset | Address | Balance | Label | Source | Confidence | Notes |
|---|---|---|---|---|---|---|
| BUIDL | `0xed71aa0da4fdba512ffa398fcff9db8c49a5cf72` | 55,065,941.14 (29.6446%) |  |  |  |  |
| BUIDL | `0x713742701e5aec2e31c272705d85aa8c3a51a258` | 31,680,293.97 (17.055%) |  |  |  |  |
| BUIDL | `0xe827abf9f462ac4f147753d86bc5f91e186e4e9c` | 15,891,429.18 (8.5551%) |  |  |  |  |
| BUIDL | `0x8780dd016171b91e4df47075da0a947959c34200` | 13,000,000.00 (6.9985%) |  |  |  |  |
| BUIDL | `0xa318d9af160110330d7e3b56cb7da0d9f7d6d67b` | 10,746,245.35 (5.7852%) |  |  |  |  |
| BUIDL | `0xb48cfe40ab635f6875b570d391dff805cf3acc32` | 8,682,891.18 (4.6744%) |  |  |  |  |
| BUIDL | `0xe6a8cc634da37d85b5f048bfd65d1e5eff6613b8` | 5,860,383.15 (3.1549%) |  |  |  |  |
| BUIDL | `0xc0d9ed97ccdfca762b1bbeb40c9c7679a7290e43` | 5,529,841.22 (2.977%) |  |  |  |  |
| BUIDL | `0xe3b11b7a5845727406935e0951ba77901dc4a48b` | 5,384,460.38 (2.8987%) |  |  |  |  |
| BUIDL | `0xf76d5dfba4544eb96e8d60d3cf817a34df019e8e` | 5,281,739.25 (2.8434%) |  |  |  |  |
| BUIDL | `0x225c19beb8f6ad683b1d3a091dca0fcfc603ecde` | 4,830,816.50 (2.6007%) |  |  |  |  |
| BUIDL | `0xf79afe03e24a80b767e48fe6fbdb3b8d9fe40a95` | 4,797,746.63 (2.5829%) |  |  |  |  |
| BUIDL | `0x71b39fdc5369db226d00abe703c56f405c1901c9` | 3,786,839.90 (2.0386%) |  |  |  |  |
| BUIDL | `0x9283c5125f4a0886b9e63e0b0fe7037382215800` | 3,491,418.42 (1.8796%) |  |  |  |  |
| BUIDL | `0x41d7d4d3352b2c7f2d65244320cb9bdbaa41deb4` | 3,084,811.54 (1.6607%) |  |  |  |  |
| BUIDL | `0x72be8c14b7564f7a61ba2f6b7e50d18dc1d4b63d` | 2,516,716.20 (1.3549%) |  |  |  |  |
| BUIDL | `0x7c97bac74c384b21f24de9e59d1bce4ffad8f2b6` | 1,500,100.00 (0.8076%) |  |  |  |  |
| BUIDL | `0x866c9a77d8ab71d2874703e80cb7ad809b301e8e` | 1,480,244.38 (0.7969%) |  |  |  |  |
| BUIDL | `0xc7125da07a7110049ecc68f43bf10de4d45ca84e` | 630,361.82 (0.3394%) |  |  |  |  |
| BUIDL | `0x4e67722883ad992182e83b79bf06a93972963cac` | 587,787.86 (0.3164%) |  |  |  |  |
| OUSG | `0x9da0ab5d7f95a8d0295e8e2967403c8dbbbeaf94` | 334,356.00 (30.5512%) |  |  |  |  |
| OUSG | `0x5d87fa995c54fff52cfe1c18d8ebf79f0eeb3aeb` | 261,208.83 (23.8675%) |  |  |  |  |
| OUSG | `0x56e60979d5934a05d22606b0455d52f59f20a6a0` | 187,133.34 (17.099%) |  |  |  |  |
| OUSG | `0x2fc2f705110a7f46ce85f701d7217ef1018f01a3` | 79,521.24 (7.2661%) |  |  |  |  |
| OUSG | `0xbd9676ea1d6cad553e87ec456869633c669ffb03` | 75,241.51 (6.8751%) |  |  |  |  |
| OUSG | `0x391897d4a5fddcb9e66a8cb837cfbfd6e918a437` | 68,964.72 (6.3015%) |  |  |  |  |
| OUSG | `0x74ddc8ff631a61e59ab9b08294d80efc314193ea` | 22,202.06 (2.0287%) |  |  |  |  |
| OUSG | `0x4307b4c9d5a48ac7cb112ef6af7fbeff5efa6af7` | 13,286.88 (1.2141%) |  |  |  |  |
| OUSG | `0x5ed4ebaf21f83959f81b7e7545e25d313c84081f` | 11,408.24 (1.0424%) |  |  |  |  |
| OUSG | `0x64bef4478942d8fd62be281707076442aa2d055e` | 8,648.38 (0.7902%) |  |  |  |  |
| OUSG | `0xe05ec030ac8e066503c6c5ea0403c74f8a8ab2de` | 8,560.83 (0.7822%) |  |  |  |  |
| OUSG | `0x9ff88e2c4844a47a70233ba676c3928b05d255cf` | 4,922.02 (0.4497%) |  |  |  |  |
| OUSG | `0xe257e2f1f544dfda152ba508bdd87832cec1406c` | 3,602.10 (0.3291%) |  |  |  |  |
| OUSG | `0x0e9ed4777f4c5b8de2df491d289fd49165156cb2` | 2,518.52 (0.2301%) |  |  |  |  |
| OUSG | `0xadf5e32eb413e62dc072aa5fd12f19a115ac3c12` | 1,927.81 (0.1762%) |  |  |  |  |
| OUSG | `0x54752f87a3f8b6c594c9afb110b2c491614de204` | 1,539.95 (0.1407%) |  |  |  |  |
| OUSG | `0x87237a1cb9e05eb498225f9a32286217116da227` | 1,497.54 (0.1368%) |  |  |  |  |
| OUSG | `0x1ceb9259e44a05cc069937b6af02d60f9b149e82` | 1,292.38 (0.1181%) |  |  |  |  |
| OUSG | `0x92f907d7f3dba5fa290b5bbd786f07d56028e4de` | 1,276.03 (0.1166%) |  |  |  |  |
| OUSG | `0x9f57efb63209e7b4849cd3414392f0850effbb66` | 1,204.11 (0.11%) |  |  |  |  |
| USDY | `0xa5b614026dcb1ef6e0e39aa53351b4f4bd225302` | 359,037,168.47 (32.0941%) |  |  |  |  |
| USDY | `0x661b5e00424b56ba6e369e0c2f21e31b6fb8ee1a` | 298,780,676.98 (26.7078%) |  |  |  |  |
| USDY | `0x9c6fa3b81ce92b7d82980d68ccce9d6e48fe4ac2` | 106,360,871.12 (9.5075%) |  |  |  |  |
| USDY | `0xc882b111a75c0c657fc507c04fbfcd2cc984f071` | 95,152,030.64 (8.5056%) |  |  |  |  |
| USDY | `0xc392749b6ff2cd95e5a4e3ed396c93f813395041` | 83,405,034.64 (7.4555%) |  |  |  |  |
| USDY | `0x13134b8d770907ecb263cb88a67f9af833007afc` | 32,661,115.46 (2.9196%) |  |  |  |  |
| USDY | `0xeeb066ada2d5c5ed9e4d9ee042bdeed430ae8512` | 28,843,984.01 (2.5783%) |  |  |  |  |
| USDY | `0xc9e397454f5478f4418e45181849c6ea66303d5a` | 18,195,193.45 (1.6265%) |  |  |  |  |
| USDY | `0xc0db94fdde74f3902ea7995194d290f6bee78f8c` | 15,992,070.24 (1.4295%) |  |  |  |  |
| USDY | `0x6870289efc708e41a97ad5068a9f84b0dd2bfaed` | 13,342,617.96 (1.1927%) |  |  |  |  |
| USDY | `0xce93c2ab2af688d036aa33b115e6852bf893d9f5` | 8,258,965.50 (0.7383%) |  |  |  |  |
| USDY | `0xa0533554f048891e5aa07ce1278a70d7ba389888` | 5,899,756.87 (0.5274%) |  |  |  |  |
| USDY | `0xaf37c1167910ebc994e266949387d2c7c326b879` | 5,085,515.95 (0.4546%) |  |  |  |  |
| USDY | `0x6d542b698541ffd216c45acdc1c6c1cd233dff94` | 4,403,415.43 (0.3936%) |  |  |  |  |
| USDY | `0x656158cdedcdaef5e9001a32d6848acc2217a99d` | 3,474,943.69 (0.3106%) |  |  |  |  |
| USDY | `0xd97ece4a24c4538d96e14296c5544c871cae2eeb` | 3,067,064.04 (0.2742%) |  |  |  |  |
| USDY | `0xc4630d28e388563351fd2c152ba1507fbb1d13cf` | 2,607,999.50 (0.2331%) |  |  |  |  |
| USDY | `0x189b2c1ce2f4cd8e535e98b005a2d7e798124b18` | 1,897,112.44 (0.1696%) |  |  |  |  |
| USDY | `0x57a99eaca6c4d922b061c73cc0b87dac0b244e54` | 1,830,824.99 (0.1637%) |  |  |  |  |
| USDY | `0x0c2c7e7aaffb6700857532c943d1443bbdd7ab16` | 1,811,783.21 (0.162%) |  |  |  |  |

## Known addresses worth checking first

- BUIDL issuer/custody: Securitize-related wallets; check Arkham for
  "Securitize" labelled addresses.
- OUSG: Ondo's `OUSG_InstantManager` contract
  `0x93358db73B6cd4b98D89c8F5f230E81a95c2643a` and Coinbase Prime address
  `0xF67416a2C49f6A46FEe1c47681C5a3832cf8856c` (from docs.ondo.finance/addresses)
  are documented non-holder infrastructure — if they appear as "holders"
  in results, label them `issuer`/`custodian` with source "Ondo docs".
- USDC: known exchange wallets are well labelled on Etherscan/Arkham.

## Phase 2 upgrade

Once labels are filled, add a `labels` CTE to `sql/08_where_activity_goes.sql`
joining address → label and re-run to get inflow volume by category —
that table feeds the executive summary.
