# OPENGL

- source: https://www.youtube.com/watch?v=Ab8TOSFfNp4

## OpenGl Rendering Pipeline:
```aiignore

 verticles     ----------------                ----------------                ----------------        
 -----------> |     Vertex     | -----------> |    Primitive   | -----------> |  Rasterization | 
              |     Shader     |              |    assembly    |              |                | 
               ----------------                ----------------                ----------------
                       &#9650;                                                               |
                       |                                                               |
                       |                                                               &#9660;
               ----------------                                                 ----------------
              |    Uniforms    | --------------------------------------------> |     Fragment   |
              |                |                                               |      Shader    |
               ----------------                                                 ----------------
                                                                                       |
                                                                                       |
                                                                                       &#9660;
                                               ----------------                 ----------------
                                              |   FrameBuffer  | <------------ |      TEST      |
                                              |                |               |                |
                                               ----------------                 ----------------
```

## Formulas

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
         &#8664;      &#8665;
           -----
          | VAO |
           -----
```


#### quad.vert:
```aiignore

 model                  world                  camera                  clip
 space     ----------   space    -----------   space    ------------   space
 -------> |  Model   | -------> |   View    | -------> | Projection | ------->
          | trasform |          | transform |          | transform  | 
           ----------            -----------            ------------
```


## HTML Entity / Symbols:
- &#9660; 
- &#9650;
- &#8664;
- &#8665;
- `<`
- `>`