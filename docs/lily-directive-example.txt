.. lily::
   :noedge:
   :nofooter:
   :audio:

   \version "2.20.0"
   \header {
     title = "翼をください, Excerpts"
   }

   \score {
     <<
       \new Staff \relative c' {
           \time 4/4
           \tempo 4 = 70
           r4 r r c8 d                  e8 e f16 e8 d16 (d4) e8 d
           c8 c d16 c8 b16 (b4) b8 g    a4 c8 a g4 c4
           d4 r r r
     }
     >>
   }
