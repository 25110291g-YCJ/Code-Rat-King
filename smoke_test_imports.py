# Quick smoke test: ensure modules import cleanly (does not instantiate classes)
try:
    from cat import Cat
    from trees import Trees
    from particles import Particle, DustParticle
    from items import GroundItem
    print('IMPORT_OK', Cat, Trees, Particle, DustParticle, GroundItem)
except Exception as e:
    print('IMPORT_ERROR', e)
    raise
