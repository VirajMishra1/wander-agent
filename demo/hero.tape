# vhs tape — terminal hero demo. Run: vhs demo/hero.tape  ->  demo/hero.gif
# Docs: https://github.com/charmbracelet/vhs
# Edit the prompt/output below to match a real entrypoint before recording.

Output demo/hero.gif

Set FontSize 22
Set Width 1000
Set Height 600
Set Theme "Catppuccin Mocha"
Set Padding 24
Set TypingSpeed 60ms

Type "pip install wander-agent"
Enter
Sleep 1s
Type "# Now ask your AI: 'Find me a NYC->Tokyo flight the airlines hide'"
Enter
Sleep 1500ms
Type "wander-agent --version"
Enter
Sleep 2s
# Replace the lines above with a command that prints a real hidden-city
# fare result so the GIF shows the magic moment (the savings number).
Sleep 2s
