Known Issues
============

- Phantom overlaps can result from massive solids intersecting with
  the geometry.  For example, a cubic 1cm RPP centred at (0,0,0)
  intersecting with an XYP at z=10,000cm (i.e. a needlessly large
  value) may produce "phantom" overlaps due to the huge size of the
  resulting solid (Not understood in terms of Geant4).  Workarounds
  have been introduced for XZP, XYP and YZP, and should work
  regardless.  Other solids, not so.
