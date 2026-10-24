# claude-plugins

Claude plugins I've built for my own work and use every day, published as a plugin marketplace named `aleos`.

| Plugin | What it does |
| :-- | :-- |
| [`decision-docs`](plugins/decision-docs/skills/decision-docs/SKILL.md) | Keeps a project's decisions, research, open questions and current state in a `docs/` folder, with [MADR](https://adr.github.io/madr/) decision records, agent rules that make agents consult them, and a script that checks them |

## Install

### Claude Code

1. Add the marketplace:

   ```
   /plugin marketplace add aleos/claude-plugins
   ```

2. Install the plugin:

   ```
   /plugin install decision-docs@aleos
   ```

From a shell, the same two steps are `claude plugin marketplace add aleos/claude-plugins` and `claude plugin install decision-docs@aleos`.

### Claude chat and Cowork

Plugins work on the paid plans, in chat on the web, the Chat tab in Claude Desktop, and Cowork.

1. Open **Customize** and go to the **Plugins** tab.
2. Select **Add**, then **Add marketplace**.
3. Enter `aleos/claude-plugins`, then add `decision-docs` from the marketplace.

## Updates

Each plugin carries a version, and a new version reaches you when you update the marketplace: run `/plugin marketplace update aleos`. To get updates automatically instead, open `/plugin`, go to **Marketplaces**, select `aleos` and select **Enable auto-update**.

## Using decision-docs

Ask for it in plain words, for example "set up decision docs in this repo", "record this decision" or "document what we just decided". On setup, the skill creates the `docs/` folder, copies the MADR templates, adds its agent rules to the project's instruction file and shows you what it added, and offers to backfill decisions already made. After every change to `docs/`, it runs `scripts/check.py` over the folder, which needs Python 3.

## License

[MIT](LICENSE). The bundled MADR templates are MIT or CC0, under [their own license](plugins/decision-docs/skills/decision-docs/templates/MADR-LICENSE.MIT).
