# Attribution and license notices

`terse-agent-output` adapts ideas from three upstream sources. This file is the consolidated attribution. The MIT license in `LICENSE` applies to the original contributions in this repo (the framing, the three fixes, the packaging, the eval work). It does not extend to the upstream sources, whose terms are their own.

## License chain

| Source | Author | License | What we use | Status |
|---|---|---|---|---|
| [attention-control](https://github.com/aaddrick/attention-control) | aaddrick | MIT | The concept, the evaluation harness, and the base structure of the rule | Clean. MIT permits reuse with attribution. |
| [i-have-adhd](https://github.com/ayghri/i-have-adhd) | Ayoub G. | MIT | The shape layer (result-first, no preamble, shape rules) | Clean. MIT permits reuse with attribution. |
| [asd-ste100 output style](https://gist.github.com/L1nefeed/4164ecaaf77879e76dca3c06f142f1c2) | L1nefeed | **No explicit license** | The language-layer principles (one word one meaning, active voice, simple tenses, sentence limits) | **Uncertain.** The Gist states no license, so default copyright applies. |
| [ASD-STE100](https://www.asd-ste100.org/) Issue 9 | ASD (Aerospace, Security and Defence Industries Association of Europe) | **Copyright + EU trademark** (No. 017966390) | Nothing directly. The L1nefeed Gist is itself an adaptation of the standard's principles. | **Restricted.** The standard is free as a PDF but redistribution is prohibited without written STEMG permission. |

## The asd-ste100 caveat

The language layer of `terse.md` derives from principles expressed in the L1nefeed Gist, which is itself an adaptation of ASD-STE100. Two things follow:

1. **We do not reproduce ASD-STE100.** This repo contains none of the standard's text, dictionary, or full rule set. It applies general technical-writing principles (active voice, simple tenses, short sentences) that the standard also teaches. Those principles are ideas, not the standard's copyrighted expression.

2. **The L1nefeed Gist has no license.** Adapting from an unlicensed gist is legally uncertain. Our language rules are written in our own words and apply the same principles; we do not copy the Gist verbatim. But we cannot warrant that the language layer is cleanly redistributable under MIT. Verify with the upstream authors before relying on that chain for commercial use.

3. **ASD-STE100 is a trademark of ASD.** We do not claim compliance with, certification by, or endorsement from ASD or STEMG. The name is referenced for attribution only. Do not present this project as an STE100 implementation.

## Modifications

This fork changes the upstream attention-control content as follows:

- Drops the air-traffic-control framing in favor of a direct output discipline.
- Adds three fixes: a verbatim-override for reproduced text, a no-tools deadlock guard, and a calibration of general knowledge versus user-specific facts.
- Adds an OMP/Pi packaging layer and a TTSR enforcement companion (OMP only).

No upstream source endorses this fork. Attribution is for credit, not endorsement.

## If you are a rightsholder

If you hold rights in any upstream source and object to this adaptation, open an issue and we will address it promptly.
