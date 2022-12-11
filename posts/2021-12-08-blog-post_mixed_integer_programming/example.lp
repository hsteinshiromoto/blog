\ Model example
\ LP format - for model browsing. Use MPS format to capture full model detail.
Maximize
  x1 + x2 + 2 x3 - 2 x4
Subject To
 c1: x1 + 2 x3 <= 700
 c2: 2 x2 - 8 x3 <= 0
 c3: x2 - 2 x3 + x4 >= 1
 c4: x1 + x2 + x3 + x4 = 10
 c5: x1 >= 0
 c6: x2 >= 0
 c7: x3 >= 0
 c8: x4 >= 0
 c9: x1 <= 10
 c10: x2 <= 10
 c11: x3 <= 10
 c12: x4 <= 10
Bounds
Generals
 x3 x4
End
