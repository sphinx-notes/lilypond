========
Examples
========

The LilyPond documentation used in example can be downloaded here:
:download:`/_scores/minuet-in-g.ly`.

.. _example-nocrop:

Original paper size
===================

.. code-block:: rst

   .. lilyinclude:: /_scores/minuet-in-g.ly
      :nocrop:

.. lilyinclude:: /_scores/minuet-in-g.ly
   :nocrop:
 
.. _example-noaudio:

Disable Audio
=============

.. code-block:: rst

   .. lilyinclude:: /_scores/minuet-in-g.ly
      :noaudio:

.. lilyinclude:: /_scores/minuet-in-g.ly
   :noaudio:

.. _example-transposing:

Transposing
===========

.. code-block:: rst

   .. lilyinclude:: /_scores/minuet-in-g.ly
      :transpose: g c

.. lilyinclude:: /_scores/minuet-in-g.ly
   :transpose: g c

Multiple Pages
==============

.. code-block:: rst

   .. lilyinclude:: /_scores/alice.ly

.. lilyinclude:: /_scores/alice.ly

Loop
====

.. versionadded:: 1.2

.. code-block:: rst

   .. lilyinclude:: /_scores/minuet-in-g.ly
      :loop:

.. lilyinclude:: /_scores/minuet-in-g.ly
   :loop:

Control Bar at the Top
======================

.. versionadded:: 1.3

.. code-block:: rst

   .. lilyinclude:: /_scores/minuet-in-g.ly
      :controls: top

.. lilyinclude:: /_scores/minuet-in-g.ly
   :controls: top

Jianpu (Numbered Musical Notation)
==================================

.. versionadded:: 1.5

.. seealso:: :ref:`jianpu-directive`.

.. code-block:: rst

   .. jianpu::

      title=C Major Scale
      1=C
      4=60
      2/4

      1 2 3 4 5 6 7 1'

.. jianpu::

   title=C Major Scale
   1=C
   4=60
   2/4

   1 2 3 4 5 6 7 1'
