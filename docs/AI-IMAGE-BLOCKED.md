# AI image tool status

Checked on 2026-10-02. The requested Imagen route in the installed Codex CLI was unavailable. `codex --version` returned `codex-cli 0.160.0`; `codex help imagegen` exited with code 2 and returned this exact error:

```text
error: unrecognized subcommand 'imagegen'

Usage: codex [OPTIONS] [PROMPT]
       codex [OPTIONS] <COMMAND> [ARGS]

For more information, try '--help'.
```

No Imagen call succeeded. After the user explicitly asked to use the available built-in image tool, `image_gen.imagegen` generated 102 accepted catalogue variants and seven accepted building/facility variants. The tool reported neither a model name nor a version. The catalogue manifest records 161 attempts: 102 accepted photo records and 59 rejected retries; every catalogue photo has an accepted variant. The seven building/facility prompts, source hashes, output paths, dimensions, times and checksums are recorded in `tools/ai_images/company-manifest.json`; the catalogue equivalents are in `tools/ai_images/manifest.json`.

Originals and delivered original WebPs remain the factual source and are preserved. AI variants are stored separately. The checked-in default is `ai-illustration`; `original` and `both` remain available in `data/editorial.json`. The site uses the concise `AI illustration` badge and descriptive alt text, and explains that illustrations are visual aids rather than photos of actual stock or company premises. Building illustrations are generic and do not depict Sanyo Aquarium's premises. Logos and association marks remain original files.
