# open-bestiary
An open-source bestiary simple bestiary designed for RPG games, allowing users to create and manage entries and organize games seperately.

CLI version is a standalone binary written in Nim, compiled for Linux.<br>
It follows a simple input system, all commands viewable from the `help` command.<br>
The groups (games) are saved to ~/.config/bestiary.nim/bestiary.group_name.ini. (Linux, i dont know where the config directory is on windows, the code should know where it is, i dont)

bestiary2json is a node script (uses npm ini library) to take the ini files and convert them to json's.

# To-do
[ ] Web version<br>
[ ] GUI<br>
[ ] Some kind of bestiary submission system.
[ ] Finish rest of commands.. (Only a few missing)
