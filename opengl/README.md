# OPENGL

## OpenGl Formulas

- source: https://www.youtube.com/watch?v=Ab8TOSFfNp4

#### base_mesh.py:
- VBO

```aiignore
in_postion
|<------->|
 ------ ------ ------ ------ ------ ------ ------ ------ ------
|  x1  |  y1  |  z1  |  x2  |  y2  |  z2  |  x3  |  y3  |  z3  |
 ------ ------ ------ ------ ------ ------ ------ ------ ------
```
```aiignore
 -----              ----------------
| VBO |            | Shader Program |
 -----              ----------------
        \         /
         \       /
           -----
          | VAO |
           -----
```