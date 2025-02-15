# Doom Remake

## Formulas

#### how to calculate the projection height of the walls
```
 PROJECTED_HEIGHT       WALL_HEIGHT                                 SCREEN_DIST
 ----------------  =  ----------------  =>  PROJECTED_HEIGHT  =  -----------------
   SCREEN_DIST             DEPTH                                       DEPTH
```
### Path Finding moving to neighboring tiles
```
graph (self.ways):

|----------|----------|----------|
|  -1, -1  |   0, -1  |   1, -1  |
|----------|----------|----------|
|  -1, 0   |   0, 0   |   1, 0   |
|----------|----------|----------|
|  -1, 1   |   0, 1   |   1, 1   |
|----------|----------|----------|
```

## Notes
- needed to use `pngcrush` to fix *.png files
  - install via homebrew: `brew install pngcrush` 
  - use command: `pngcrush -ow -rem allb -reduce file.png`

## Reference
#### Doom SpriteDatabase: https://spritedatabase.net/game/760
#### Doom Text Generator: https://fontmeme.com/doom-font/
#### youtube link: https://www.youtube.com/watch?v=ECqUrT7IdqQ&list=PLi77irUVkDatlbulEY4Kz8O107HO8RGH8
#### github link: https://github.com/StanislavPetrovV/DOOM-style-Game