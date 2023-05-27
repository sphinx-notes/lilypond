========
Examples
========

The LilyPond documentation used in example can be downloaded here:
:download:`/_scores/minuet-in-g.ly`.

Original paper size
===================

.. code-block:: rst

   .. lilyinclude:: /_scores/minuet-in-g.ly

.. lilyinclude:: /_scores/minuet-in-g.ly

Paper without Footer and Edge
=============================

.. code-block:: rst

   .. lilyinclude:: /_scores/minuet-in-g.ly
      :nofooter:
      :noedge:

.. lilyinclude:: /_scores/minuet-in-g.ly
   :nofooter:
   :noedge:
 
Smallest Paper Size
===================

.. code-block:: rst

   .. lilyinclude:: /_scores/minuet-in-g.ly
      :noheader:
      :nofooter:
      :noedge:

.. lilyinclude:: /_scores/minuet-in-g.ly
   :noheader:
   :nofooter:
   :noedge:

.. _example-audio-preview:

Audio Preview
=============

.. code-block:: rst

   .. lilyinclude:: /_scores/minuet-in-g.ly
      :noheader:
      :nofooter:
      :noedge:
      :audio:

.. lilyinclude:: /_scores/minuet-in-g.ly
   :noheader:
   :nofooter:
   :noedge:
   :audio:

.. _example-transposing:

Transposing
===========

.. code-block:: rst

   .. lilyinclude:: /_scores/minuet-in-g.ly
      :noheader:
      :nofooter:
      :noedge:
      :audio:
      :transpose: g c

.. lilyinclude:: /_scores/minuet-in-g.ly
   :noheader:
   :nofooter:
   :noedge:
   :audio:
   :transpose: g c

Multiple Pages
==============

.. code-block:: rst

   .. lilyinclude:: /_scores/alice.ly
      :noedge:
      :audio:

.. lilyinclude:: /_scores/alice.ly
   :noedge:
   :audio:

Loop
====

.. versionadded:: 1.2

.. code-block:: rst

   .. lilyinclude:: /_scores/minuet-in-g.ly
      :noheader:
      :nofooter:
      :noedge:
      :loop:

.. lilyinclude:: /_scores/minuet-in-g.ly
   :noheader:
   :nofooter:
   :noedge:
   :loop:

Control Bar at the Top
======================

.. versionadded:: 1.3

.. code-block:: rst

   .. lilyinclude:: /_scores/minuet-in-g.ly
      :noheader:
      :nofooter:
      :noedge:
      :controls: top

.. lilyinclude:: /_scores/minuet-in-g.ly
   :noheader:
   :nofooter:
   :noedge:
   :controls: top

Jianpu (Numbered Musical Notation)
==================================

.. versionadded:: 1.5

.. code-block:: rst

   .. jianpu::

      %% tempo: 4=60
      title=C Major Scale
      1=C
      2/4

      1 2 3 4 5 6 7 1'

.. jianpu::

   %% tempo: 4=60
   title=C Major Scale
   1=C
   2/4

   1 2 3 4 5 6 7 1'
