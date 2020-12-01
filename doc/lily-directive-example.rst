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
           \tempo  "Allegretto" 4 = 110
           c4 d e e     f e d2
           e4 d c c     d c b2
           b4 g a2      c4 a g2
           c2 d         d4 c b8 c4.
     }
     >>
   }
