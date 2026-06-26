# Hero Demo — recording guide

The single highest-value asset for the repo. One 15–30s GIF at the top of the README does ~80% of conversion. Lead with the **hidden-city / "fares airlines hide"** moment.

## Option A — Claude Desktop screen recording (recommended, most impressive)

1. Install: `pip install wander-agent`, add to Claude Desktop MCP config.
2. Screen-record (macOS: `Cmd+Shift+5`, record a tight window — just the chat).
3. Type exactly this and let it run:
   > Find me a flight from New York to Tokyo in August the airlines don't want me to see — hidden-city or split-ticket if it's cheaper.
4. Stop when the cheaper fare + savings appears. Keep it under 30s — trim the thinking pause.
5. Convert to GIF: `ffmpeg -i demo.mov -vf "fps=12,scale=900:-1:flags=lanczos" -loop 0 demo/hero.gif`
6. Reference at top of README: `![demo](demo/hero.gif)`

**Make it pop:** clean desktop, large font, dark theme, no notifications. The "saved $240" number is the screenshot people share.

## Option B — Terminal GIF via vhs (fully scriptable, no manual typing)

Install [vhs](https://github.com/charmbracelet/vhs): `brew install vhs`, then:

```bash
vhs demo/hero.tape   # outputs demo/hero.gif
```

Edit `hero.tape` to match a real CLI entrypoint or a short Python snippet that prints a tool result.

## Where it goes

Top of `README.md`, right under the title block, before "What is this?". One GIF. Don't bury it.
