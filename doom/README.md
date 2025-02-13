# Doom Remake

## Formulas

#### how to calculate the projection height of the walls
```
 PROJECTED_HEIGHT       WALL_HEIGHT                                 SCREEN_DIST
 ----------------  =  ----------------  =>  PROJECTED_HEIGHT  =  -----------------
   SCREEN_DIST             DEPTH                                       DEPTH
```
## Notes
- needed to use `pngcrush` to fix *.png files
  - install via homebrew: `brew install pngcrush` 
  - use command: `pngcrush -ow -rem allb -reduce file.png`

## Reference
#### youtube link: https://www.youtube.com/watch?v=ECqUrT7IdqQ&list=PLi77irUVkDatlbulEY4Kz8O107HO8RGH8
#### github link: https://github.com/StanislavPetrovV/DOOM-style-Game