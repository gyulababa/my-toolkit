<!-- helpers/led_pixels/README.md -->
helpers/led_pixels
Purpose

Lighting domain helpers for pixel strip data models, validation, and edit operations. This layer is frontend-agnostic and protocol-agnostic.

Belongs here

Pixel strip models and schema helpers

Pixel buffer edit operations (create, resize, fill, set_range)

Validation and normalization helpers for lighting docs

Does not belong here

Device IO or network protocols (see helpers/toolkits)

Persistence and revision handling (helpers/persist)

UI adapters or runtime controls (services/ui, app/adapters)

Public API (flat list)

PixelBufferEditor

PixelColorRGB

StripType

Endpoint

seed_pixel_strips_doc

seed_strip_raw

apply_master_brightness_to_rgb_triplet

normalize_master_brightness
